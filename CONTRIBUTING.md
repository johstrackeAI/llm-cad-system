# Contributing to Python CAD System

Thank you for considering contributing to the Python CAD System project. This document outlines the process and guidelines for contributing.

## Project Structure

The project follows a modular architecture:

- `cad_system/core/`: Core functionality
  - `geometry/`: Geometric primitives and base classes
  - `operations/`: Boolean operations and transformations
- `cad_system/document/`: Document handling and visualization
- `cad_system/part/`: Part modeling and parametric features

## Code Style Guidelines

1. **Python Version**: Use Python 3.8+ features and type hints.

2. **Code Formatting**:
   - Use `black` for code formatting
   - Use `isort` for import sorting
   ```bash
   black .
   isort .
   ```

3. **Type Hints**:
   - Add type hints to all function arguments and return values
   - Use `mypy` for type checking:
   ```bash
   mypy cad_system/
   ```

4. **Documentation**:
   - Document all public APIs using Google-style docstrings
   - Include examples in docstrings where appropriate
   - Keep docstrings up-to-date with code changes

5. **Testing**:
   - Write unit tests for new features
   - Maintain test coverage above 80%
   - Place tests in the `tests/` directory mirroring the package structure

## Testing Procedures

1. **Running Tests**:
   ```bash
   # Run all tests
   pytest tests/
   
   # Run with coverage
   pytest --cov=cad_system tests/
   
   # Run specific test file
   pytest tests/core/test_geometry.py
   ```

2. **Writing Tests**:
   - Name test files with `test_` prefix
   - Use descriptive test function names
   - Follow the Arrange-Act-Assert pattern
   - Use fixtures for common setup
   - Mock external dependencies

## Pull Request Process

1. **Fork and Clone**:
   - Fork the repository
   - Clone your fork locally
   - Add the upstream repository as a remote

2. **Create a Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Development**:
   - Write your code following style guidelines
   - Add/update tests
   - Update documentation
   - Commit with clear, descriptive messages

4. **Pre-PR Checklist**:
   - [ ] Run all tests
   - [ ] Check code formatting
   - [ ] Run type checker
   - [ ] Update documentation
   - [ ] Add entry to CHANGELOG.md

5. **Submit PR**:
   - Create PR against main branch
   - Fill in PR template
   - Link related issues
   - Wait for CI checks
   - Address review comments

## Review Process

1. All PRs require at least one review
2. CI checks must pass
3. Documentation must be updated
4. Test coverage must not decrease
5. Breaking changes require discussion

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

Thank you for contributing!
