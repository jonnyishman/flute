# Project layout

Any references to front end code refer to the code in the @web directory which contains a typescript and react based website for the flute application. 

Any references to back end code refer to the code in the @server directory which contains a python flask based API server for the flute application. 

Any bash command that follow assume they are execute from the repository root directory. 
Adjust them as required if running from another directory.

# When making changes to server code

**Above all**, defer to the surrounding code style.

## Bash commands
- ./server/venv/bin/ruff check --fix ./server (Lints server code and fixes simple errors)
- ./server/venv/bin/pytest ./server (Runs all server tests)

## Code style

- Ensure function definitions have type annotations
- Follow PEP 8 for code style, and PEP 257 for docstrings
- Follow PEP 585 for type hints: for example, prefer `list[str]` to `List[str]`
- Use walrus operator (`:=`) when it eliminates redundancy AND improves readability
- List comprehensions over loops when straightforward
- Use boolean expressions and `elif` instead of nested ifs
- For function design accept flexible types (`Sequence`), return specific types (`list`)

## Test style
- Tests should mostly on inputs/outputs, rather than state
- Accessing protected attributes should be avoided
- External dependencies should be mocked, and only external dependencies
- Use pytest, and utilise pytest fixtures for common start up / tear down code

# When making changes to web code

## Bash commands
- npm run --prefix ./web lint (Lints web code)
- npm run --prefix ./web typecheck (Runs type checker on web code)
- npm run --prefix ./web test:run (Run tests on web code)

## Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo} from 'bar')

## Test style
- Tests should be very high-level, smoke-like tests. No detailed tests of individual components
required.

# Critical Verification Workflow
1. Be sure to run linters in the appropiate directory when making a series of code changes
2. **ALL checks must pass** - No exceptions, no "unrelated errors"
3. Prefer running single tests, and not the whole test suite, for performance
4. If you create helper classes/functions, verify that are actually USED
5. If you refactor code, verify the old code is actually REPLACED

## Research Before Suppressing

- When encountering linting/typing errors, research proper solutions FIRST
- Never suggest `# pylint: disable=` or `# type: ignore` without investigating:
  - Modern best practices (e.g., `Annotated` for Pydantic)
  - Whether error indicates real issue vs. tool limitation
  - Alternative approaches that fix root cause
- Only use suppressions as absolute last resort with clear justification

## Comments

- Explain WHY, not WHAT
- Only comment non-obvious aspects. I.e. timing dependencies, edge cases, domain knowledge
