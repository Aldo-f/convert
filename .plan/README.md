# convert — Adoption & Ecosystem Plan

Master plan for growing `convert` from a working CLI into a widely-used tool.
All tasks are modular, TDD-first, and YAGNI-filtered. Each task can be delegated
to a Hermes subagent as a self-contained spec.

## Task Index

| # | Task | Module | TDD | Status |
|---|------|--------|-----|--------|
| 1 | HTTP microservice | `convert` core | Yes | Pending |
| 2 | Node CLI wrapper | Ecosystem shim | Yes | Pending |
| 3 | Ruby CLI wrapper | Ecosystem shim | Yes | Pending |
| 4 | PyPI publish | Publishing | Yes | Pending |
| 5 | GitHub README | Publishing | Verify | Pending |
| 6 | Code of Conduct | Trust | N/A | Pending |
| 7 | Security policy | Trust | N/A | Pending |
| 8 | Install docs | First-timer | Verify | Pending |
| 9 | Contextual help | First-timer | Yes | Pending |
| 10 | Error messages | First-timer | Yes | Pending |
| 11 | Issue templates | Feedback | N/A | Pending |
| 12 | Badges | Social proof | N/A | Pending |
| 13 | Examples gallery | Social proof | Verify | Pending |
| 14 | Blog automation | Cross-pollination | Yes | Pending |

## Execution Order

Tasks 6, 7, 11, 12 are zero-dependency trust/feedback scaffolding — do first.
Tasks 8, 9, 10 depend on a working CLI — do after core is stable.
Tasks 1, 2, 3 extend the CLI — do in parallel after core is stable.
Tasks 4, 5, 13 are publishing — do after core + trust scaffolding.
Task 14 is standalone — do whenever.

## Cross-Cutting Principles

- **TDD**: For code tasks, write tests before implementation. Tests are the acceptance criteria.
- **YAGNI**: Every task has an explicit "What's OUT" section. Don't build it until someone asks.
- **Modular**: Each task adds one module. No task modifies another task's files.
- **Delegation-ready**: Each task file is a complete spec a subagent can execute without context.