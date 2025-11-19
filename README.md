# 🌍 JSON i18n Translator

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A powerful Python CLI tool that automatically translates JSON files for internationalization (i18n) using free translation APIs. Perfect for quickly creating multilingual versions of your application's language files.

**🚀 No API keys required • ✨ 17+ languages • 🎯 Smart placeholder preservation • 📦 Batch + ⚡ Parallel + 🧩 Cache**

## 🎯 Features

✨ **Free & Unlimited** - Uses Google Translate via deep-translator (no API key required)  
🌍 **17+ Languages** - English, Spanish, French, German, Italian, Portuguese, Japanese, Chinese, and more  
🧠 **Auto-Detection** - Automatically detects source language from JSON content  
🔄 **Preserves Structure** - Maintains nested JSON structures and arrays  
🎯 **Smart Placeholders** - Preserves interpolation variables: `{{name}}`, `{0}`, `%s`, `${var}`  
📦 **Batch Translation** - Translate to multiple languages in one command & group strings for fewer API calls  
⚡ **Parallel Execution** - Multi-threaded batch processing (configurable workers)  
🧩 **Persistent Cache** - Reuses previously translated strings instantly  
⚡ **Easy to Use** - Simple CLI interface with helpful options  
🛠️ **Framework Agnostic** - Works with React i18next, Vue i18n, Angular, Flutter, and more  

## Installation

### Option 1: Automated Setup (Recommended)

Run the setup script to create a virtual environment and install dependencies:

```bash
./setup.sh
```

Then activate the virtual environment:

```bash
source venv/bin/activate
```

### Option 2: Manual Setup

1. **Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! No API keys or configuration needed.

**Note:** Remember to activate the virtual environment (`source venv/bin/activate`) each time you want to use the translator.

## Usage

### Basic Usage

Translate a JSON file to Spanish (auto-detect source language):
```bash
python translator.py input.json -t es
```

### Specify Source Language

Translate from English to Spanish:
```bash
python translator.py en.json -s en -t es
```

### Multiple Target Languages

Translate to multiple languages at once:
```bash
python translator.py input.json -t es fr de it pt
```

### Custom Output Directory

Specify where to save translated files:
```bash
python translator.py input.json -t es -o ./locales
```

### Verbose Mode

See detailed progress during translation:
```bash
python translator.py input.json -t es -v
```

### List Supported Languages

View all available language codes:
```bash
python translator.py --list-languages
```

### Performance Tuning

Adjust batch size (strings per group) & number of parallel workers:
```bash
python translator.py input.json -t es --batch-size 20 --max-workers 5
```

Disable cache (forces re-translation):
```bash
python translator.py input.json -t es --no-cache
```

Recommended ranges:
- `--batch-size`: 10–20 (default 15)
- `--max-workers`: 2–4 (default 3)

Cache file: `.translation_cache.db` (auto-created, safe to commit or share)

High-performance multi-language with verbose output:
```bash
python translator.py messages.json -s en -t es fr de it pt --batch-size 18 --max-workers 4 -v
```

## Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `es` | Spanish |
| `fr` | French |
| `de` | German |
| `it` | Italian |
| `pt` | Portuguese |
| `ja` | Japanese |
| `zh-CN` | Chinese (Simplified) |
| `ru` | Russian |
| `ar` | Arabic |
| `hi` | Hindi |
| `ko` | Korean |
| `nl` | Dutch |
| `pl` | Polish |
| `sv` | Swedish |
| `tr` | Turkish |
| `vi` | Vietnamese |

## Examples

### Example 1: Simple Flat JSON

**Input** (`en.json`):
```json
{
  "welcome": "Welcome to our app",
  "goodbye": "See you later",
  "user_name": "Username",
  "user_email": "Email address"
}
```

**Command:**
```bash
python translator.py en.json -s en -t es
```

**Output** (`en.es.json`):
```json
{
  "welcome": "Bienvenido a nuestra aplicación",
  "goodbye": "Hasta luego",
  "user_name": "Nombre de usuario",
  "user_email": "Dirección de correo electrónico"
}
```

### Example 2: Nested Structure with Placeholders

**Input** (`messages.json`):
```json
{
  "auth": {
    "login": {
      "title": "Login to your account",
      "welcome": "Welcome back, {{username}}!",
      "error": "Invalid credentials"
    },
    "register": {
      "title": "Create new account",
      "success": "Account created for {email}"
    }
  },
  "notifications": {
    "count": "You have {0} new messages",
    "greeting": "Hello, ${name}!"
  }
}
```

**Command:**
```bash
python translator.py messages.json -t es fr
```

**Output** (`messages.es.json`):
```json
{
  "auth": {
    "login": {
      "title": "Inicia sesión en tu cuenta",
      "welcome": "¡Bienvenido de nuevo, {{username}}!",
      "error": "Credenciales inválidas"
    },
    "register": {
      "title": "Crear nueva cuenta",
      "success": "Cuenta creada para {email}"
    }
  },
  "notifications": {
    "count": "Tienes {0} mensajes nuevos",
    "greeting": "¡Hola, ${name}!"
  }
}
```

Notice how the placeholders `{{username}}`, `{email}`, `{0}`, and `${name}` are preserved!

### Example 3: Translate Multiple Languages

Create Spanish, French, and German versions:
```bash
python translator.py app.json -s en -t es fr de -v
```

This creates:
- `app.es.json` (Spanish)
- `app.fr.json` (French)
- `app.de.json` (German)

### Example 4: Performance & Cache
Initial (no cache yet):
```bash
time python translator.py nested.json -s en -t de -v
```
Repeat (all strings cached):
```bash
time python translator.py nested.json -s en -t de -v
```
Sample (56 strings): first run ~2.6s, cached run ~0.16s (previous naive approach was ~22–24s).

## How It Works

1. **Load JSON** - Reads and validates your input JSON file
2. **Detect Language** (optional) - Analyzes content to identify source language
3. **Extract Placeholders** - Identifies and protects interpolation variables
4. **Translate** - Sends text to Google Translate via deep-translator
5. **Batch / Parallel** - Groups strings and optionally uses threads
6. **Cache Lookup** - Skips strings already translated earlier
7. **Restore Placeholders** - Puts back the original variables
8. **Save** - Writes translated JSON with preserved structure

## Supported Placeholder Formats

The tool automatically preserves these interpolation formats:

- `{{variable}}` - i18next, Handlebars, Mustache
- `{name}` - Vue i18n, Python format strings
- `{0}`, `{1}` - .NET, Java MessageFormat
- `%s`, `%d` - C-style printf
- `%(name)s` - Python named format
- `${variable}` - JavaScript template literals
- `[[key]]` - Some custom frameworks

## Output File Naming

Translated files are automatically named using this pattern:
```
{original_name}.{language_code}.json
```

Examples:
- `en.json` → `en.es.json`, `en.fr.json`
- `messages.json` → `messages.es.json`, `messages.de.json`
- `app.en.json` → `app.en.es.json`

## Tips & Best Practices

### For Better Translations

1. **Use clear, complete sentences** - Short fragments may not translate well
2. **Provide context** - Longer strings give better translation quality
3. **Keep keys in English** - Only values are translated, keys remain unchanged
4. **Review output** - Machine translation isn't perfect; review important strings

### For Large Files
1. Tune batch size (`--batch-size 18`) for fewer requests
2. Use parallel workers (`--max-workers 3`) for speed
3. Leverage cache (default on) for iterative runs
4. Verbose mode (`-v`) shows progress & cache hits
5. Version control: commit original before translating

## Performance (v1.1.0)

| Scenario | Strings | First Run (No Cache) | Cached Repeat |
|----------|---------|----------------------|---------------|
| Simple file | 20 | ~1s | <0.15s |
| Nested file | 56 | ~2.6s | ~0.16s |
| Previous (pre-optimizations) | 56 | ~22–24s | N/A |

Optimizations:
- Batch grouping reduces API overhead
- Parallel threads speed up batch processing
- Persistent SQLite cache provides O(1) reuse

Tips:
- Increase `--batch-size` until no further speed gains
- Avoid too many workers (>5) to reduce rate-limit risk
- Cache file can be shared to seed translations

### Common i18n Patterns

The tool works great with popular i18n libraries:

- **React i18next** ✅
- **Vue i18n** ✅
- **Angular i18n** ✅
- **Next.js i18n** ✅
- **Flutter intl** ✅
- **Any JSON-based i18n** ✅

## Troubleshooting

### "Failed to detect language"
- Ensure your JSON has enough text content (not just single words)
- Manually specify source language with `-s` flag

### "Invalid JSON file"
- Validate your JSON at [jsonlint.com](https://jsonlint.com)
- Check for trailing commas or syntax errors

### Translation quality issues
- Provide more context in strings
- Consider using official DeepL API for higher quality (see below)

### Network errors
- Check your internet connection
- Retry the command (temporary API issues)

## Advanced: Using DeepL API (Optional)

For higher quality translations, you can modify the code to use DeepL API:

1. Sign up for free DeepL API key (500k characters/month free)
2. Install DeepL library: `pip install deepl`
3. Modify `translator.py` to use `DeeplTranslator` instead of `GoogleTranslator`

## Project Structure

```
translator-json/
├── translator.py       # Main translation script
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── examples/          # Sample input files
│   ├── simple.json
│   └── nested.json
└── translations/      # Default output directory (auto-created)
```

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 3 steps
- **[Features Overview](FEATURES.md)** - Detailed feature showcase
- **[Project Overview](PROJECT_OVERVIEW.md)** - Technical details and architecture
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Some ideas for contributions:
- Add support for more translation services (DeepL, Azure, etc.)
- Add YAML/TOML format support
- Glossary / translation memory
- Diff mode (only new keys) implementation
- DeepL optional integration
- Add more placeholder patterns

## 📄 License

MIT License - feel free to use this in your projects! See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [deep-translator](https://github.com/nidhaloff/deep-translator) - Translation API wrapper
- [langdetect](https://github.com/Mimino666/langdetect) - Language detection

## ⭐ Show Your Support

If this tool helped you, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs or suggesting features
- 🔀 Contributing code improvements
- 📢 Sharing with others who might find it useful

## 💬 Support

- 📖 Read the [documentation](README.md)
- 🐛 [Report issues](https://github.com/GarriguesN/json-i18n-translator/issues)
- 💡 [Request features](https://github.com/GarriguesN/json-i18n-translator/issues/new)

---

> **📝 Note:** This documentation was created with the assistance of AI tools to ensure comprehensive coverage and clarity.

**Made with ❤️ for the i18n community**

Happy translating! 🌍✨
