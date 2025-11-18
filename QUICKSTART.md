# Quick Start Guide

## Setup (First Time Only)

1. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

## Basic Usage

### Try the Examples

1. **List supported languages:**
   ```bash
   python translator.py --list-languages
   ```

2. **Translate simple.json to Spanish:**
   ```bash
   python translator.py examples/simple.json -t es
   ```

3. **Translate nested.json to multiple languages:**
   ```bash
   python translator.py examples/nested.json -t es fr de -v
   ```

4. **Check the output:**
   ```bash
   cat translations/simple.es.json
   ```

### Translate Your Own Files

1. **Auto-detect source language, translate to Spanish:**
   ```bash
   python translator.py your-file.json -t es
   ```

2. **Specify source language (English to Spanish):**
   ```bash
   python translator.py your-file.json -s en -t es
   ```

3. **Multiple target languages with verbose output:**
   ```bash
   python translator.py your-file.json -t es fr de it -v
   ```

4. **Custom output directory:**
   ```bash
   python translator.py your-file.json -t es -o ./my-translations
   ```

## Output Files

Translated files are automatically named:
- Input: `messages.json`
- Output: `messages.es.json`, `messages.fr.json`, etc.

Default output directory: `./translations/`

## Common Commands

```bash
# Activate virtual environment (do this first!)
source venv/bin/activate

# Show help
python translator.py --help

# List all supported languages
python translator.py --list-languages

# Translate to Spanish with verbose output
python translator.py input.json -t es -v

# Translate to multiple languages
python translator.py input.json -t es fr de it pt

# When done, deactivate virtual environment
deactivate
```

## Tips

- ✅ Use `-v` flag to see translation progress
- ✅ Multiple target languages save time (batch processing)
- ✅ Auto-detect works well for most cases
- ✅ Placeholders like `{{var}}`, `{0}`, `${name}` are preserved
- ✅ JSON structure is maintained (nested objects, arrays)

## Troubleshooting

**"Command not found: python"**
→ Try `python3` instead of `python`

**"ModuleNotFoundError: No module named 'deep_translator'"**
→ Activate virtual environment: `source venv/bin/activate`

**"Invalid JSON file"**
→ Validate your JSON at https://jsonlint.com

**"Failed to detect language"**
→ Specify source language manually: `-s en`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check the [examples/](examples/) folder for sample files
- Customize the language list in `translator.py` if needed

Happy translating! 🌍✨
