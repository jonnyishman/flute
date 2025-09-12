# Project Layout

**CRITICAL**: Frontend code is in `@web` (TypeScript/React), backend code is in `@server` (Python/Flask).

**ALL bash commands MUST be executed from repository root directory.**

# When making changes to server code

**Above all**, defer to the surrounding code style.

## MANDATORY Commands After Server Changes
```bash
./server/venv/bin/ruff check --fix ./server    # MUST run - fixes linting
./server/venv/bin/pytest ./server              # MUST run - validates changes
```

## NON-NEGOTIABLE Code Style Rules
- **ALWAYS** add type annotations to ALL function definitions
- **STRICTLY** follow PEP 8 (style) and PEP 257 (docstrings)  
- **REQUIRED**: Use modern type hints (`list[str]`, NOT `List[str]`)
- **PREFERRED**: Walrus operator `:=` when it improves readability
- **PREFERRED**: List comprehensions over explicit loops
- **REQUIRED**: Function parameters accept flexible types (`Sequence`), return specific types (`list`)

## Test style
- Tests should mostly on inputs/outputs, rather than state
- Accessing protected attributes should be avoided
- External dependencies should be mocked, and only external dependencies
- Use pytest, and utilise pytest fixtures for common start up / tear down code

# When making changes to web code

## MANDATORY Commands After Web Changes
```bash
npm run --prefix ./web lint        # MUST run - fixes linting
npm run --prefix ./web typecheck   # MUST run - validates types
npm run --prefix ./web test:run    # MUST run - validates changes
```

## Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo} from 'bar')

## Test style
- Tests should be very high-level, smoke-like tests. No detailed tests of individual components
required.

# CRITICAL Verification Workflow - NEVER SKIP
1. **MANDATORY**: Run appropriate linters after ANY code changes
2. **ZERO TOLERANCE**: ALL checks must pass - no exceptions, no "unrelated errors"
3. **PERFORMANCE**: Run targeted tests, not full suite unless required
4. **VERIFICATION**: Ensure new helper classes/functions are actually USED
5. **CLEANUP**: When refactoring, verify old code is completely REPLACED

## NEVER Suppress Without Investigation

- **FORBIDDEN**: Using `# pylint: disable=` or `# type: ignore` without research
- **REQUIRED**: First investigate proper solutions:
  - Modern best practices (e.g., `Annotated` for Pydantic)
  - Root cause analysis 
  - Alternative implementation approaches
- **LAST RESORT**: Suppressions only with clear documentation why

## Comments

- Explain WHY, not WHAT
- Only comment non-obvious aspects. I.e. timing dependencies, edge cases, domain knowledge

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
