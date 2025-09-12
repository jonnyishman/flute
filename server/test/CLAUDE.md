# Server Test Guidelines

## MANDATORY Test Framework
- **REQUIRED**: pytest with fixtures for setup/teardown
- **REQUIRED**: Given + When + Then structure for ALL tests

## Test Focus Requirements
- **MANDATORY**: Test inputs & outputs, public state only
- **FORBIDDEN**: Testing protected members of objects
- **REQUIRED**: Use `pytest.mark.parametrize` to eliminate test duplication when structure is similar

## External Dependencies  
- **REQUIRED**: Mock external dependencies only
- **FORBIDDEN**: Mocking internal application code

## Test Structure Template
```python
def test_feature_name():
    # Given - setup test data and conditions
    
    # When - execute the code under test
    
    # Then - assert expected outcomes
```

## Performance
- Focus on testing changed files only, not full test suite unless required