"""Run with PYTHONPATH=src python -m unittest discover -s tests -v.

The real resolver, FunctionTool and ReAct loop run with scripted model replies.
Only model/database infrastructure and HTTP I/O are replaced.
"""

import io
import json
import os
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests
from llama_index.core.llms import ChatMessage, ChatResponse, MockLLM

from memary.agent.base_agent import Agent
from memary.agent.chat_agent import ChatAgent
from memary.agent.parallel_search import ENDPOINT, PROTOCOL_VERSION, USER_AGENT, ParallelSearch


RESULT_TEXT = 'Source: https://example.org/news\nA useful current finding.'


class MCPServer:
    """Observe prepared HTTP requests, including auth, URL and headers."""

    def __init__(self, events=False, failure=None):
        self.requests = []
        self.responses = []
        self.events = events
        self.failure = failure
        self.result = {'content': [{'type': 'text', 'text': RESULT_TEXT}]}

    def send(self, request, **kwargs):
        message = json.loads(request.body)
        self.requests.append((request, message, kwargs))
        self_check = message['method']
        if self_check == 'tools/call' and self.failure is not None:
            raise self.failure
        if self_check == 'initialize':
            result = {'protocolVersion': PROTOCOL_VERSION, 'capabilities': {}}
        elif self_check == 'notifications/initialized':
            result = None
        else:
            result = self.result
        response = requests.Response()
        response.status_code = 202 if result is None else 200
        response.request = request
        response.url = request.url
        response.headers['Content-Type'] = 'application/json'
        if self_check == 'initialize':
            response.headers['Mcp-Session-Id'] = 'transport-session'
        payload = json.dumps({'jsonrpc': '2.0', 'id': message.get('id'), 'result': result})
        if self.events and self_check == 'tools/call':
            response.headers['Content-Type'] = 'text/event-stream; charset=utf-8'
            payload = ': keepalive\n\ndata: {"jsonrpc":"2.0","method":"notifications/message"}\n\nevent: message\ndata: ' + payload + '\n\n'
        response.raw = io.BytesIO(payload.encode())
        response.close = Mock(wraps=response.close)
        self.responses.append(response)
        return response


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ, {}, clear=True))
        self.stack.enter_context(patch('memary.agent.base_agent.load_dotenv'))
        self.stack.enter_context(patch.object(
            Agent, 'load_llm_model', lambda agent, name: setattr(agent, 'llm', MockLLM())
        ))
        self.stack.enter_context(patch.object(Agent, 'load_vision_model'))
        for name in ['googlemaps.Client', 'StorageContext.from_defaults',
                     'KnowledgeGraphRAGRetriever', 'Message', 'MemoryStream',
                     'EntityKnowledgeStore']:
            self.stack.enter_context(patch('memary.agent.base_agent.' + name))
        self.stack.enter_context(patch('llama_index.graph_stores.neo4j.Neo4jGraphStore'))
        self.graph = SimpleNamespace(query=Mock(return_value=SimpleNamespace(metadata=None)))
        self.stack.enter_context(patch(
            'memary.agent.base_agent.RetrieverQueryEngine.from_args', return_value=self.graph
        ))
        self.server = MCPServer()
        self.stack.enter_context(patch('requests.adapters.HTTPAdapter.send', side_effect=self.server.send))

    def agent(self, **kwargs):
        kwargs.setdefault('include_from_defaults', ['search'])
        return ChatAgent('test', 'memory.json', 'entities.json', 'system.txt',
                         'user.txt', 'chat.json', **kwargs)

    def test_fresh_no_key_react_dispatch_and_consumption(self):
        agent = self.agent()
        self.assertEqual(agent.search_provider, 'parallel')
        observed = []

        def reply(messages, **kwargs):
            observed.append(messages)
            if len(observed) == 1:
                text = 'Thought: I need current information.\nAction: search\nAction Input: {"query": "current news"}'
            else:
                self.assertIn(RESULT_TEXT, '\n'.join(str(m.content) for m in messages))
                text = 'Thought: I can answer from the source.\nAnswer: A useful current finding, from https://example.org/news'
            return ChatResponse(message=ChatMessage(role='assistant', content=text))

        with patch.object(MockLLM, 'chat', side_effect=reply):
            answer = agent.routing_agent.chat('What is the current news?')
        self.assertIn('https://example.org/news', str(answer))
        self.assertEqual(len(answer.sources), 1)
        self.assertIn(RESULT_TEXT, answer.sources[0].content)
        self.assertEqual(len(observed), 2)
        for request, message, kwargs in self.server.requests:
            self.assertEqual(request.url, ENDPOINT)
            self.assertEqual(request.headers['User-Agent'], USER_AGENT)
            self.assertNotIn('Authorization', request.headers)
            self.assertEqual(kwargs['timeout'], 30.0)
        call = self.server.requests[-1][1]['params']
        self.assertEqual(call['name'], 'web_search')
        self.assertEqual(call['arguments']['search_queries'], ['current news'])

    def test_configured_perplexity_and_no_silent_fallback(self):
        os.environ['PERPLEXITY_API_KEY'] = 'configured-key'
        with patch('memary.agent.base_agent.Perplexity') as provider:
            agent = self.agent()
            provider.assert_called_once_with(api_key='configured-key', model='mistral-7b-instruct', temperature=0.5)
            provider.return_value.chat.return_value = 'Existing provider answer'
            self.assertEqual(agent.search('question'), 'Existing provider answer')
            provider.return_value.chat.side_effect = RuntimeError('provider failed')
            with self.assertRaisesRegex(RuntimeError, 'provider failed'):
                agent.search('question')
        self.assertEqual(self.server.requests, [])

    def test_environment_choice_and_constructor_override(self):
        os.environ['MEMARY_SEARCH_PROVIDER'] = 'disabled'
        self.assertEqual(self.agent().search_provider, 'disabled')
        os.environ['PERPLEXITY_API_KEY'] = 'configured-key'
        agent = self.agent(search_provider='parallel', search_timeout=7)
        self.assertEqual(agent.search('question'), RESULT_TEXT)
        self.assertTrue(all(c[2]['timeout'] == 7 for c in self.server.requests))

    def test_missing_explicit_credentials_and_invalid_provider(self):
        with self.assertRaisesRegex(ValueError, 'PERPLEXITY_API_KEY'):
            self.agent(search_provider='perplexity')
        with self.assertRaisesRegex(ValueError, 'search_provider'):
            self.agent(search_provider='unknown')

    def test_graph_answer_and_disabled_external_search(self):
        agent = self.agent(search_provider='disabled')
        graph_answer = SimpleNamespace(metadata={'source': 'graph'})
        self.graph.query.return_value = graph_answer
        self.assertIs(agent.search('question'), graph_answer)
        self.graph.query.return_value = SimpleNamespace(metadata=None)
        self.assertEqual(agent.search('question'), 'External web search is disabled.')
        self.assertEqual(self.server.requests, [])

    def test_tool_permissions_removal_and_custom_override(self):
        self.assertNotIn('search', self.agent(include_from_defaults=[]).tools)
        agent = self.agent()
        agent.update_tools([])
        self.assertNotIn('search', agent.tools)
        agent.update_tools(['search'])
        agent.remove_tool('search')
        self.assertNotIn('search', agent.tools)

        def search(query: str) -> str:
            """Search using the application's chosen source."""
            return 'custom source'

        agent.add_tool({'search': search})
        self.assertEqual(agent.tools['search']('question'), 'custom source')
        self.assertEqual(self.server.requests, [])

    def test_query_llm_override_is_preserved(self):
        agent = self.agent()
        agent.query_llm = Mock()
        agent.query_llm.chat.return_value = 'application model'
        self.assertEqual(agent.external_query('question'), 'application model')
        self.assertEqual(self.server.requests, [])

    def test_fetch_url_preserves_query_and_conversation(self):
        agent = self.agent()
        agent.search('question')
        agent.search('https://example.org/a?x=one&y=two#part')
        calls = [m['params'] for _, m, _ in self.server.requests if m['method'] == 'tools/call']
        self.assertEqual(calls[1]['name'], 'web_fetch')
        self.assertEqual(calls[1]['arguments']['urls'], ['https://example.org/a?x=one&y=two#part'])
        self.assertEqual(calls[0]['arguments']['session_id'], calls[1]['arguments']['session_id'])
        for request, message, _ in self.server.requests:
            if message['method'] != 'initialize':
                self.assertEqual(request.headers['Mcp-Session-Id'], 'transport-session')
                self.assertEqual(request.headers['MCP-Protocol-Version'], PROTOCOL_VERSION)

    def test_sse_response(self):
        self.server.events = True
        self.assertEqual(self.agent().search('question'), RESULT_TEXT)
        self.assertTrue(all(r.close.called for r in self.server.responses))

    def test_timeout_and_interrupt_propagate_without_retry(self):
        for failure in (requests.Timeout('timed out'), requests.ConnectionError('offline'), KeyboardInterrupt()):
            with self.subTest(failure=type(failure).__name__):
                self.server.requests.clear()
                self.server.failure = failure
                with self.assertRaises(type(failure)):
                    self.agent(search_provider='parallel').search('question')
                self.assertEqual(len(self.server.requests), 3)
                self.assertTrue(all(r.close.called for r in self.server.responses))

    def test_tool_error_propagates_without_provider_switch(self):
        self.server.result = {'isError': True, 'content': [{'type': 'text', 'text': 'quota exceeded'}]}
        agent = self.agent(search_provider='parallel')
        with self.assertRaisesRegex(RuntimeError, 'quota exceeded'):
            agent.search('question')
        self.assertEqual(len(self.server.requests), 3)

    def test_ambient_netrc_credentials_are_not_sent(self):
        with tempfile.TemporaryDirectory() as directory:
            netrc = Path(directory) / 'netrc'
            netrc.write_text('machine search.parallel.ai login accidental password secret\n')
            os.environ['NETRC'] = str(netrc)
            self.agent().search('question')
        self.assertTrue(all('Authorization' not in request.headers for request, _, _ in self.server.requests))


class ProtocolTests(unittest.TestCase):
    def test_invalid_timeout_and_empty_query(self):
        for timeout in (0, -1, float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                ParallelSearch(timeout=timeout)
        with self.assertRaises(ValueError):
            ParallelSearch().search('  ')

    def test_json_rpc_and_tool_errors(self):
        for message in ({'jsonrpc': '2.0', 'id': 2, 'error': {'code': -32602}},
                        {'jsonrpc': '2.0', 'id': 99, 'result': {}},
                        {'jsonrpc': '2.0', 'id': 2, 'result': None}):
            with self.assertRaises(RuntimeError):
                ParallelSearch._result(message, 2)
        for result in ({'isError': True, 'content': [{'type': 'text', 'text': 'quota exceeded'}]},
                       {'content': []}):
            with patch.object(ParallelSearch, '_post', side_effect=[
                {'protocolVersion': PROTOCOL_VERSION}, {}, result,
            ]):
                with self.assertRaises(RuntimeError):
                    ParallelSearch().search('question')

    def test_http_error_redirect_and_malformed_json(self):
        for status, body, error in [(429, '{}', requests.HTTPError),
                                    (302, '{}', RuntimeError),
                                    (200, 'not json', ValueError)]:
            server = MCPServer()
            def send(request, **kwargs):
                response = server.send(request, **kwargs)
                response.status_code = status
                if status == 302:
                    response.headers['Location'] = 'https://elsewhere.example/'
                response.raw = io.BytesIO(body.encode())
                return response
            with patch('requests.adapters.HTTPAdapter.send', side_effect=send):
                with self.assertRaises(error):
                    ParallelSearch().search('question')
            self.assertEqual(len(server.requests), 1)

    def test_protocol_mismatch_and_unexpected_content_type(self):
        with patch.object(ParallelSearch, '_post', return_value={'protocolVersion': 'unknown'}):
            with self.assertRaisesRegex(RuntimeError, 'unsupported protocol'):
                ParallelSearch().search('question')
        server = MCPServer()
        def send(request, **kwargs):
            response = server.send(request, **kwargs)
            response.headers['Content-Type'] = 'text/html'
            return response
        with patch('requests.adapters.HTTPAdapter.send', side_effect=send):
            with self.assertRaisesRegex(RuntimeError, 'content type'):
                ParallelSearch().search('question')

    def test_bounded_json_and_sse_responses(self):
        for events in (False, True):
            with self.subTest(events=events):
                server = MCPServer(events=events)
                with patch('requests.adapters.HTTPAdapter.send', side_effect=server.send), patch(
                    'memary.agent.parallel_search.MAX_RESPONSE_BYTES', 200,
                ):
                    server.result = {'content': [{'type': 'text', 'text': 'x' * 300}]}
                    with self.assertRaisesRegex(RuntimeError, 'too large'):
                        ParallelSearch().search('question')


if __name__ == '__main__':
    unittest.main()
