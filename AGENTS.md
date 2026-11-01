# Project Working Guidelines

1. Communicate explanations and progress summaries to the user in Hebrew. Write all project documents in English, including README, SoW, SRS, the decisions and assumptions register, and these guidelines. Write code and commit messages in English. Pass this language distinction to every sub-agent.

2. The user owns the goals and major decisions. The primary agent coordinates execution, work allocation, integration, checks, and routine corrections.

3. Work in small, meaningful stages. Before starting each stage, the primary agent briefly presents its purpose and deliverables and waits for the user's approval to begin. Once approved, complete the stage and its routine corrections without requesting guidance for every action.

4. Consult the user about material ambiguity in requirements, changes to approved scope or design, any need for payment, or destructive actions.

5. When parallel work begins, the primary agent may activate sub-agents within the approved stage. Assign each agent clear responsibilities, files, and deliverables; coordinate interfaces and prevent conflicting edits. Only the primary agent may perform Git operations that modify the repository.

6. Documentation and implementation evolve together. Requirements documents begin as drafts; design, diagrams, and tests are updated as decisions and implementation progress. Distinguish assignment requirements, working assumptions, and user-approved decisions.

7. Do not present a capability, experiment, or test as completed unless it actually occurred. Report limitations and failures.

8. Organize commits around meaningful units of work, with descriptive messages in English. At the end of a suitable unit, state that it is time for a commit.

9. Commit only when the user requests it. Before committing, review the diff, run checks appropriate to code changes, and include only relevant files. Do not include secrets, build outputs, or unnecessarily large files.

10. Push only when the user explicitly requests it. A commit request does not authorize a push. Before pushing, verify the remote and branch; report the result afterward.

11. Do not force-push or rewrite history without an explicit user request.

12. At the end of each stage, summarize what was completed, what was checked, what remains open, and whether a commit is recommended.
