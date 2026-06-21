Create a concrete implementation plan for the repository. Treat the analysis and assignment text as mandatory requirements.

Return structured output only. Return one valid JSON object only.

The plan must cover every item from:

- mandatory_requirements
- required_dependencies
- required_files
- required_interfaces
- feedback_requirements
- acceptance_criteria

If "teacher_feedback" is non-empty, include every feedback item in requirement_traceability and self_checklist. This is a revision: the plan must produce a complete assignment solution, not a small patch-only answer.

Do not omit a dependency, file, command, interface, or output format named in the task. Do not substitute requested dependencies or frameworks with alternatives. If the repository already has dependency files, plan exact updates to them. If no dependency file exists and dependencies are required, create the appropriate one for the project style.

Return JSON only:

{
  "requirement_traceability": [
    {
      "requirement": "exact requirement",
      "implementation": "file/action that satisfies it"
    }
  ],
  "dependency_plan": [],
  "files_to_inspect": [],
  "files_to_create": [],
  "files_to_modify": [],
  "commands_to_run": [],
  "expected_final_behavior": [],
  "self_checklist": []
}

Rules:

- Every mandatory requirement must appear in requirement_traceability.
- Every required dependency must appear in dependency_plan and in files_to_create or files_to_modify when applicable.
- Prefer complete, runnable solutions over sketches, placeholders, or pseudo-code.
- Include CLI commands or usage examples when the assignment asks for a CLI or runnable script.
- Include validation steps that would catch missing dependencies and missing required interfaces.
- If replacement_commit is true or is_revision is true, plan changes as a full resubmission commit whose diff contains the complete assignment solution.
