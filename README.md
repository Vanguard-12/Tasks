# Structured Output – Discriminated Union Example

This repository demonstrates how to turn a raw log containing heterogeneous
lines into a list of **typed** events using **Pydantic v2** discriminated unions
and **LangChain** structured output.

## Features

- Two concrete event models (`HttpOkEvent` and `HttpErrorEvent`) with a `kind`
  discriminator.
- `ApiEvent` declared as a discriminated union (`Annotated[Union[...],
  Field(discriminator="kind")]`).
- Log splitting on blank lines or `---` delimiters.
- LLM‑driven parsing via `ChatOpenAI.with_structured_output` – no manual
  `json.loads` or regex.
- Simple CLI (`cli.py`) that prints each parsed model and renders a nice table
  using **rich**.
- Example log is bundled; you can also provide your own file with `--log`.

## Setup

```bash
# Clone the repo
git clone <repo-url>
cd <repo-dir>

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -U pip
pip install -r requirements.txt

# Configure the OpenAI key
cp .env.example .env
# Edit .env and replace the placeholder with your real key
```

> **Note**: The code uses the `gpt-4o-mini` model. You can change the model name
> in `parser.py` if you prefer another one.

## Usage

Run the CLI with the built‑in example log:

```bash
python cli.py
```

Provide a custom log file:

```bash
python cli.py --log path/to/your.log
```

The output consists of two parts:

1. A raw ``model_dump()`` representation of each parsed event.
2. A formatted table showing the common fields (`kind`, `path`, `status`) and the
   branch‑specific fields (`duration_ms` for successful requests, `error_message`
   for errors).

## Project Structure

```
├─ models.py          # Pydantic discriminated union definitions
├─ parser.py          # Log splitting and LLM‑based parsing logic
├─ cli.py             # Command‑line interface
├─ .env.example       # Template for environment variables
├─ requirements.txt   # Python dependencies
└─ README.md          # This file
```

## Testing (optional)

A minimal test suite lives in the `tests/` directory.  To run the tests:

```bash
pip install pytest
pytest -q
```

The tests verify that the union discriminates correctly and that the log
splitting works as expected.  They do **not** hit the OpenAI API – the parsing
logic is exercised with a mocked LLM.

## License

This example is provided under the MIT License.
