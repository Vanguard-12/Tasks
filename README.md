# Deep Agent with Live Web Search and Virtual File System

This project implements a deep agent based on the *Deep Agents from Scratch* framework. The agent can perform live web searches, store results in a virtual file system, and export those files to the real file system.

## Installation

```bash
# Clone the repository
git clone https://github.com/Vanguard-12/Tasks.git
cd Tasks/assignment-agent/task/69de7223f3-8-deep-agents-from-scratch

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following keys:

```dotenv
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_api_key
```

## Running the Agent

```bash
# From the command line
python agent.py "Python async programming"
```

The agent will perform a web search for the query, store the results in a virtual file, and export `search_results.txt` to the `output_files` directory.

## Notebook Demo

Open `run_agent.ipynb` in Jupyter to see a step‑by‑step demonstration.
