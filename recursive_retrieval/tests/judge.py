import openai

# Set your OpenAI API key
openai.api_key = "OPENAI_API_KEY"

def evaluate_response(response, question):
    """
    Evaluate the quality of a response based on a given question using the OpenAI API.

    Args:
    - response (str): The response to evaluate.
    - question (str): The question used to evaluate the response.

    Returns:
    - quality_score (float): The quality score of the response.
    """
    # Use the OpenAI API to ask a question and evaluate the response
    prompt = f"Question: {question}\nResponse: {response}\n"
    response = openai.Completion.create(
        engine="davinci",  # or any other engine you prefer
        prompt=prompt,
        temperature=0,
        max_tokens=50,
        n=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    # Extract the quality score from the response
    quality_score = response['choices'][0]['score']
    
    return quality_score

def evaluate_responses(responses, question):
    """
    Evaluate the quality of each response in a string array based on a given question.

    Args:
    - responses (list of str): The responses to evaluate.
    - question (str): The question used to evaluate the responses.

    Returns:
    - quality_scores (list of float): The quality scores of the responses.
    """
    quality_scores = []
    for response in responses:
        quality_score = evaluate_response(response, question)
        quality_scores.append(quality_score)
    
    return quality_scores

# if __name__ == "__main__":
#     # Example usage
#     responses = [
#         "This is the first response.",
#         "This is the second response.",
#         "This is the third response."
#     ]
#     question = "What is your opinion on the topic?"
    
#     quality_scores = evaluate_responses(responses, question)
#     for response, score in zip(responses, quality_scores):
#         print(f"Response: {response}\nQuality Score: {score}\n")
