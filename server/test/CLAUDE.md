Tests should use pytest, with fixtures used for any setup or teardown. 

Tests should use the Given + When + Then structure. 

Tests should focus on testing inputs & outputs, and public state. They should not check protected members of objects.

pytest.mark.parametrize should be used sensibly to reduce duplication between tests that have a similar structure and only differ by the inputs and outputs being checked. 

Mocks should only be used to avoid calling external dependencies in tests.