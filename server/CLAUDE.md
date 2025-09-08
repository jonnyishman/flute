This is a flask app serving the backend API for flute. 

Any changes to production code under @src should be reflected by modifying or adding tests under @test.

The structure for @test should reflect the same structure for code in @src, but with the `test_` prefix for test modules. For example, tests for `src/routes/books.py` should live in `test/routes/test_books.py`. 

Python typing should be used for all function arguments and to specify the return types of functions. Imports that are used only for typing and not for runtime should be kept under an 'if TYPE_CHECKING:` block.

After making changes linting and tests should be run for the changed files only. 