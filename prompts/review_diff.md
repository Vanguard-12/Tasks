Review the git diff against the assignment description, analysis, and plan. Be strict.

Return structured output only. Return one valid JSON object only.

The solution is acceptable only if every mandatory requirement is implemented in the repository diff or already present in the final repository state represented by the diff context. If any required dependency, file, interface, command, output format, framework, package, schema, or feedback fix is missing, set "acceptable" to false.

If teacher_feedback is non-empty, reject the solution unless every feedback point is addressed. If replacement_commit is true, reject patch-only diffs: the diff must include the complete assignment solution files needed for review.

The input may include repo_url, branch, and base_sha. If the solution documentation needs a repository or branch link, verify that it uses a real value from repo_url/branch rather than a template or placeholder.

Return JSON only:

{
  "acceptable": true,
  "findings": [],
  "missing_requirements": [],
  "missing_dependencies": [],
  "dependency_issues": [],
  "summary": "short summary"
}

Strict checks:

- Every mandatory requirement from the task is implemented.
- Every feedback requirement from the submission is addressed.
- Every dependency explicitly requested by the task is present in the appropriate dependency file.
- Third-party imports used by the code are declared in dependency files when the project uses such files.
- Requested dependencies/frameworks are not replaced with alternatives.
- Required file names, function names, class names, CLI commands, output formats, and schemas match the task.
- Code is syntactically valid and plausibly runnable.
- Changed files are relevant to the current assignment.
- No secrets are included.
- No unrelated destructive changes are present.

Reject the solution when:

- A required dependency is absent.
- A requested technology is substituted by a different one.
- The implementation is only a stub, placeholder, pseudo-code, or documentation-only answer when runnable code is required.
- README, code, or configuration contains unresolved placeholders such as yourusername, your-username, example.com, REPLACE_ME, INSERT_, TODO:, FIXME:, or fake GitHub URLs.
- The diff cannot plausibly satisfy the assignment as written.
