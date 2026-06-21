Modify the repository to solve the assignment completely. Treat the task, analysis, and plan as a strict contract.

Use repository tools.
If the repository is empty, create the complete minimal project needed to satisfy the assignment. "Minimal" means no unrelated extras; it does not mean omitting required behavior, files, dependencies, commands, or interfaces.

Strict requirements:

- Implement every mandatory requirement from the analysis.
- If teacher_feedback is non-empty, address every feedback requirement explicitly.
- If replacement_commit is true, create the complete final assignment solution in this branch. Do not return a patch-only fix; the resulting git diff must contain all files needed for the assignment.
- Add every required dependency named by the task to the correct dependency file, unless it is already present.
- Use the exact dependency, framework, file, class, function, command, model, output format, and interface names requested by the task.
- Do not replace requested technologies with similar alternatives.
- If the task asks for a CLI, provide a runnable CLI entry point or script and document the command.
- If the task asks for structured output, schemas, TypedDict, Pydantic models, LangGraph nodes, tools, prompts, memory, RAG, MCP, Tavily, ChromaDB, or other specific components, create the actual code for those components.
- Do not leave placeholders, TODO-only implementations, pseudo-code, fake imports, or stubs that do not run.
- Do not leave placeholder repository URLs or template text. If documentation needs a repository URL, use the provided repo_url. If it needs a branch URL, use repo_url + "/tree/" + branch. Never invent https://github.com/yourusername/... links.
- Do not leave unresolved values such as yourusername, your-username, example.com, REPLACE_ME, INSERT_, TODO:, or FIXME:.
- Keep the solution focused on the current assignment and preserve unrelated existing files.

Dependency rules:

- If exact versions are specified, preserve them.
- If versions are not specified, use modern stable package names and avoid obsolete packages or unnecessary old pins.
- Do not omit dependency files when third-party packages are used.

Safety rules:

- Do not edit .env or .env.example.
- Do not expose secrets.
- Do not delete unrelated files.

Return structured JSON only:

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

Allowed tools are write_file, apply_patch, and create_directory.

Before returning, internally verify that the operations satisfy every item in requirement_traceability, dependency_plan, and self_checklist. If any mandatory item is not satisfied, add operations to satisfy it before returning.
