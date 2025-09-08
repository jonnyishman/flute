This directory contains the web app for flute. 

When changing production code the tests for that code should be modified or created. 

Tests in this directory should be very high-level, do not write detailed unit tests or test individual
components. Only write smoke test style tests that make sure that the pages render properly and URL
params are passed around properly. 

After making changes to any production code files run linting and tests for the changed files only. 