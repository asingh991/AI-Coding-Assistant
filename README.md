# AI Coding Assistant & Review Agent

A Python tool that takes a plain-English task, generates code for it, writes pytest tests for that code, and produces a structured code review. It is built with LangChain and Google's Gemini API, and it keeps working when one model hits a rate limit.

> **Credit:** The approach and coding style of this project were inspired by Nicholas Renotte's tutorial ["How to Build a Multi Agent AI System"](https://youtu.be/gUrENDkPw_k) and his repository [nicknochnack/WatsonxCrewAI](https://github.com/nicknochnack/WatsonxCrewAI). See [Acknowledgements](#acknowledgements) for details.

## Why this project exists

LLMs write code quickly, but the output usually needs a second look and has no tests. This project chains the steps a developer would do by hand (write, review, test) into one repeatable command, so each result arrives with a review and a test file instead of a bare code block.

## How it works

```
task (plain English)
   │
   ▼
[Generate]  ──►  outputs/generated.py
   │
   ├──►  [Review]       ──►  outputs/review.md
   │
   └──►  [Write tests]  ──►  outputs/test_generated.py
```

1. **Generate:** a prompt tells the model to act as a senior Python developer and return only code. A small helper strips the Markdown fences so the saved file is clean Python.
2. **Review:** the generated code goes to a second prompt that plays a strict reviewer and lists bugs, style issues and improvements, most severe first.
3. **Test:** a third prompt writes pytest tests for the generated code.

Each step is a LangChain chain (`prompt | model | output parser`), built by one small factory function. Adding a new step means adding a prompt, not rewriting the program.

## Design decisions

- **Model fallbacks.** Free API tiers have strict limits, and some models have none on the free tier. Models are listed in `.env` in priority order. LangChain's `.with_fallbacks()` moves to the next model automatically if a call fails, so a single rate limit does not stop a run.
- **Secrets stay out of Git.** The API key lives in `.env`, which is listed in `.gitignore`. The code stops with a clear message if the key or model list is missing.
- **Separate prompts per role.** Splitting generation, review and testing into separate prompts keeps each task focused and makes each one easy to improve on its own.
- **Deterministic output.** Temperature is set to 0 so repeated runs on the same task behave consistently.

## Tech stack

Python · LangChain (`langchain-google-genai`) · Google Gemini API · python-dotenv · pytest · Git/GitHub

## Setup

```bash
git clone https://github.com/asingh991/AI-Coding-Assistant.git
cd AI-Coding-Assistant
pip install langchain-google-genai python-dotenv
```

Create a `.env` file (never commit it):

```
GOOGLE_API_KEY=your_key_here
GEMINI_MODELS=model_id_1,model_id_2
```

Run `python list_models.py` to see the model IDs your key can use.

## Usage

```bash
python assistant.py "a function that validates email addresses"
```

Results are written to `outputs/`: `generated.py`, `review.md` and `test_generated.py`.

## Project structure

| File | Purpose |
|---|---|
| `assistant.py` | Prompts, chains, model fallback and the generate → review → test workflow |
| `list_models.py` | Lists the Gemini models available to your API key |
| `.env` | API key and model list (not committed) |

## Current limitations

- Generated tests are written but not yet executed automatically, so a passing test run is not verified by the tool.
- Output quality depends on the model and on how specific the task description is.

## Roadmap

- Run the generated tests in an isolated Docker container and capture the logs
- Feed test failures back to the model for automatic fixes
- Score code quality and compare prompt versions
- Benchmark response time and cost per run

## Acknowledgements

The structure of this project (a single, clearly sectioned Python file covering configuration, model setup, prompts and workflow) follows the style of [Nicholas Renotte's tutorial](https://youtu.be/gUrENDkPw_k) and his [WatsonxCrewAI repository](https://github.com/nicknochnack/WatsonxCrewAI). The use case, the LangChain and Gemini implementation, and the model-fallback logic are my own adaptation.
