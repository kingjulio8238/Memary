import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

# Get the code version
version = {}
with open(os.path.join(here, "memary/version.py")) as fp:
    exec(fp.read(), version)
__version__ = version["__version__"]

install_requires = [
    "neo4j==5.17.0",
    "python-dotenv==1.0.1",
    "pyvis==0.3.2",
    "streamlit==1.31.1",
    "llama-index==0.10.11", 
    "llama-index-agent-openai==0.1.5",
    "llama-index-core==0.1.12",
    "llama-index-embeddings-openai==0.1.5",
    "llama-index-graph-stores-nebula==0.1.2",
    "llama-index-graph-stores-neo4j==0.1.1",
    "llama-index-legacy==0.9.48",
    "llama-index-lms-openai==0.1.5",
    "llama-index-multi-modal-llms-openai==0.1.3",
    "llama-index-program-openai==0.1.3",
    "llama-index-question-gen-openai==0.1.2",
    "llama-index-readers-file==0.1.4",
    "langchain==0.1.12",
    "langchain-openai==0.0.8",
    "llama-index-lms-perplexity==0.1.3",
    "pandas",
    "geocoder",
    "googlemaps",
    "ansistrip", 
]


setuptools.setup(
    name="memary",
    version=__version__,
    author="memary Labs",
    author_email="hello@memarylabs.com",
    description="Longterm Memory for Autonomous Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kingjulio8238/memary",
    packages=setuptools.find_packages(include=["memary*"], exclude=["tests"]),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8,<=3.11.9",
)
