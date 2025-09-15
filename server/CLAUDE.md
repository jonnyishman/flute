# Flask Backend API for Flute

## MANDATORY Requirements

**CRITICAL**: Every change to `@src` code REQUIRES corresponding test changes in `@test`.

### Test Structure
- **REQUIRED**: Mirror `@src` structure in `@test` with `test_` prefix
- Example: `src/routes/books.py` → `test/routes/test_books.py`

### Python Code Standards
- **MANDATORY**: Type annotations on ALL function arguments and return types
- **WHEN NEEDED**: Runtime imports vs typing imports separation only if some imports are only for typing:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      # typing-only imports here
  ```

### Database Queries  
- **FORBIDDEN**: SQLAlchemy ORM approach (hidden queries)
- **REQUIRED**: SQLAlchemy Core approach (explicit query construction)

### File Format
- **MANDATORY**: All Python modules must end with newline

## Post-Change Workflow
**ALWAYS** run linting and tests for changed files only after modifications.
