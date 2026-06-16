# AI Fluency Plan Repository

This repository contains a personal **AI Fluency development plan** created to fulfill the assignment for the *AI Fluency* course (Skilljar).

## Repository Contents

- **`AI_Fluency_Plan.md`** – The full plan in Markdown format. It includes:
  - Executive Summary
  - Self‑assessment against the five AI Fluency dimensions
  - SMART short‑term and long‑term goals
  - Learning resources
  - Timeline & milestones
  - Evaluation metrics
  - References
- **`README.md`** – You are reading it right now! It explains how to view and optionally export the plan.

## Viewing the Plan

The plan is a regular Markdown file, so you can view it directly on GitHub, or clone the repository and open it with any Markdown viewer or text editor.

```bash
git clone <repo‑url>
cd <repo‑directory>
cat AI_Fluency_Plan.md   # or open with VS Code, Obsidian, etc.
```

## Generating a PDF (Optional)

If you need a PDF version for submission, you can convert the Markdown file using **Pandoc**:

1. Install Pandoc (if not already installed):
   ```bash
   # Debian/Ubuntu
   sudo apt-get install pandoc
   # macOS (Homebrew)
   brew install pandoc
   ```
2. Convert the Markdown to PDF:
   ```bash
   pandoc AI_Fluency_Plan.md -o AI_Fluency_Plan.pdf
   ```
   This will produce `AI_Fluency_Plan.pdf` in the repository root.

## License

The content of this plan is personal and may be shared publicly. The repository itself is provided under the MIT License.
