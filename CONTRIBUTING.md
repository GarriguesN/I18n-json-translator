# Contributing to JSON i18n Translator

First off, thank you for considering contributing to JSON i18n Translator! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Your environment** (OS, Python version)
- **Sample JSON** that demonstrates the issue (if applicable)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Use case** - Why would this feature be useful?
- **Proposed solution** - How do you envision it working?
- **Alternatives** - Have you considered other approaches?

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** with clear, descriptive commits
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/json-i18n-translator.git
cd json-i18n-translator

# Setup virtual environment
./setup.sh
source venv/bin/activate

# Make your changes
# ... edit files ...

# Test your changes
python translator.py examples/simple.json -t es -v
```

## Code Style

- Follow **PEP 8** Python style guidelines
- Use **descriptive variable names**
- Add **docstrings** to functions and classes
- Keep functions **focused** and **single-purpose**
- Add **comments** for complex logic

## Testing

Before submitting:

1. Test with the provided examples:
   ```bash
   python translator.py examples/simple.json -t es
   python translator.py examples/nested.json -t es fr
   python translator.py examples/with-arrays.json -t es
   ```

2. Test edge cases:
   - Empty JSON files
   - Very large files (100+ strings)
   - All placeholder types
   - Invalid input

3. Test CLI options:
   ```bash
   python translator.py --list-languages
   python translator.py --help
   ```

## Commit Messages

Use clear, descriptive commit messages:

```
✅ Good:
- "Add support for DeepL API"
- "Fix placeholder regex for Vue i18n"
- "Update README with new examples"

❌ Bad:
- "Update"
- "Fix bug"
- "Changes"
```

## Ideas for Contributions

Here are some areas where contributions would be especially welcome:

### Features
- [ ] Translation caching system
- [ ] DeepL API integration option
- [ ] YAML/TOML format support
- [ ] Batch API calls for better performance
- [ ] Translation diff mode
- [ ] Custom glossary support
- [ ] Progress bar for large files
- [ ] Parallel translation requests

### Improvements
- [ ] Better error messages
- [ ] More comprehensive tests
- [ ] Performance optimizations
- [ ] Additional placeholder patterns
- [ ] More language support

### Documentation
- [ ] Video tutorials
- [ ] More usage examples
- [ ] API integration guides
- [ ] Troubleshooting guide
- [ ] Translation quality tips

## Questions?

Feel free to open an issue for:
- Questions about the codebase
- Clarification on features
- Discussion about potential changes

## Code of Conduct

Be respectful and constructive in all interactions. We're all here to learn and improve the tool together!

---

**Thank you for contributing!** 🙏

Your efforts help make JSON i18n Translator better for everyone in the i18n community.
