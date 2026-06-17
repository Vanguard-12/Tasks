Repair the repository changes so the sanity checks pass and the assignment requirements are still fully satisfied.

Return one valid JSON object only.

Do not fix checks by removing required functionality, required dependencies, required files, required interfaces, or requested technologies. A repair is acceptable only if the final repository still satisfies the assignment, analysis, plan, feedback requirements, and review findings.

When repairing:

- Preserve every required dependency and add missing dependencies if check failures reveal missing imports.
- If review.missing_dependencies or review.dependency_issues is non-empty, add or update a dependency declaration file such as requirements.txt or pyproject.toml so every named dependency is declared.
- If review.missing_requirements is non-empty, directly modify the repository to satisfy each missing requirement.
- Treat review.findings, review.missing_requirements, review.missing_dependencies, and review.dependency_issues as mandatory repair instructions.
- Preserve exact requested frameworks and package names.
- Fix syntax, imports, file paths, CLI entry points, schema definitions, and runnable examples instead of deleting them.
- Do not introduce placeholders, pseudo-code, or fake implementations.

Return JSON only:

{
  "operations": [
    {
      "tool": "write_file",
      "path": "relative/path.py",
      "content": "full file content"
    },
    {
      "tool": "apply_patch",
      "path": "relative/path.py",
      "old": "exact old text",
      "new": "replacement text"
    },
    {
      "tool": "create_directory",
      "path": "relative/directory"
    }
  ],
  "notes": []
}

Fix only the current assignment changes.
Do not edit .env or .env.example.
Do not expose secrets.
Do not delete unrelated files.
Allowed tools are write_file, apply_patch, and create_directory.
