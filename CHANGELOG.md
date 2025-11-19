# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-19

### 🧹 Performance Optimization

#### Removed
- Artificial delay between translations (was slowing down the process unnecessarily)
- Fast mode flag (`-f`, `--fast`) - no longer needed as everything is fast by default

#### Changed
- All translations now run at maximum speed without artificial delays
- Cleaner, simpler codebase

#### Performance
- ~10% faster translation times on large files
- More responsive user experience

## [1.0.0] - 2025-11-18

### 🎉 Initial Release

#### Added
- Core translation functionality using Google Translate (via deep-translator)
- Automatic language detection from JSON content
- Support for 17+ languages
- Smart placeholder preservation for multiple i18n frameworks:
  - `{{variable}}` - i18next, Handlebars
  - `{name}` - Vue i18n, Python
  - `{0}` - .NET, Java
  - `%s`, `%d` - C-style
  - `%(name)s` - Python named
  - `${variable}` - JavaScript
- Recursive JSON traversal for nested structures
- Array support
- Batch translation to multiple languages
- CLI interface with argparse
- Verbose mode for progress tracking
- Custom output directory option
- Comprehensive documentation:
  - README.md with usage examples
  - QUICKSTART.md for beginners
  - FEATURES.md with detailed feature showcase
  - PROJECT_OVERVIEW.md with technical details
  - CONTRIBUTING.md with contribution guidelines
- Example JSON files demonstrating different use cases
- Automated setup script (setup.sh)
- Demo script (demo.sh)
- MIT License

#### Features
- **Free & Unlimited**: No API keys or usage limits
- **Auto-Detection**: Automatically identifies source language
- **Structure Preservation**: Maintains JSON hierarchy
- **Error Handling**: Graceful failures with helpful messages
- **UTF-8 Support**: Full unicode character support
- **Progress Tracking**: Real-time translation count in verbose mode

#### Documentation
- Complete README with installation and usage instructions
- Quick start guide for new users
- Detailed feature documentation
- Technical architecture overview
- Contributing guidelines
- Multiple example files

#### Examples Included
- `simple.json` - Basic flat structure (20 strings)
- `nested.json` - Complex nested with placeholders (56 strings)
- `with-arrays.json` - Arrays and mixed types (27 strings)

---

## Future Releases

### Planned for v1.1.0
- [ ] Translation caching system
- [ ] DeepL API integration option
- [ ] Batch API calls for improved performance
- [ ] Progress bar for large files

### Planned for v1.2.0
- [ ] YAML format support
- [ ] TOML format support
- [ ] Translation diff mode
- [ ] Custom glossary support

### Planned for v2.0.0
- [ ] Web UI interface
- [ ] Translation memory
- [ ] Quality scoring
- [ ] Parallel translation requests
- [ ] Plugin system

---

[1.0.0]: https://github.com/YOUR-USERNAME/json-i18n-translator/releases/tag/v1.0.0
