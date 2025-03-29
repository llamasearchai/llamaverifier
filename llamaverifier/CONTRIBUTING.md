# Contributing to LlamaVerifier

Thank you for your interest in contributing to LlamaVerifier! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

There are many ways to contribute to LlamaVerifier:

1. **Report bugs**: If you find a bug, please create an issue on GitHub with a detailed description.
2. **Suggest features**: If you have an idea for a new feature, please create an issue on GitHub.
3. **Improve documentation**: Help us improve the documentation by fixing typos, adding examples, or clarifying explanations.
4. **Submit pull requests**: If you've fixed a bug or implemented a new feature, please submit a pull request.

## Development Setup

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/llamaverifier.git
   cd llamaverifier
   ```
3. Create a virtual environment and install the development dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```
4. Create a branch for your changes:
   ```bash
   git checkout -b feature-or-bugfix-name
   ```

## Pull Request Process

1. Ensure your code follows the project's style guidelines.
2. Add or update tests as necessary.
3. Update the documentation as necessary.
4. Ensure all tests pass:
   ```bash
   pytest
   ```
5. Submit a pull request to the `main` branch.

## Style Guidelines

- Follow PEP 8 for Python code.
- Use meaningful variable and function names.
- Write docstrings for all functions, classes, and modules.
- Keep lines under 100 characters.
- Use type hints where appropriate.

## Testing

- Write tests for all new features and bug fixes.
- Ensure all tests pass before submitting a pull request.
- Aim for high test coverage.

## Documentation

- Update the documentation for all new features and changes.
- Use clear and concise language.
- Provide examples where appropriate.

## License

By contributing to LlamaVerifier, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 