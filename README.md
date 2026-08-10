# AI Data Assistant

A local AI assistant that answers questions about your data (CSV, JSON, TXT) by planning tool calls with an LLM (via [Ollama](https://ollama.ai) / `llama3:8b`) and executing them in Python.

## How It Works

1. **Plan** — Your query + available tools + data metadata are sent to the LLM, which returns a JSON plan (a sequence of tool calls, with variables for chaining results).
2. **Execute** — Python runs the plan step by step (filter → count → calculate, etc.) — no LLM involved, so no made-up numbers.
3. **Respond** — The final result is passed back to the LLM to generate a plain-English answer.

## Example

```
Ask Your Question: Multiply the number of employees in Finance with the number of employees in HR
```

The assistant filters + counts each department, saves the counts as variables, then multiplies them via the `calculate` tool.

## Tools

`filter_data` · `count_data` · `sort_data` · `max_data` · `min_data` · `average_data` · `unique_values` · `calculate` · `read_txt` · `read_json` · `read_csv` · `get_current_datetime` · `get_current_date`

## Setup

```bash
pip install ollama pandas
ollama pull llama3:8b
```

Put your data files in `AI_assistant/data/`, then run:

```bash
python main.py
```

## Project Structure

```
AI_assistant/
├── data/     # your CSV / JSON / TXT files
├── log/      # query + plan + result logs
├── tools/    # tool implementations
└── main.py
```
