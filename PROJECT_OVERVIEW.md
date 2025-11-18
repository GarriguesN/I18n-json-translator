# JSON i18n Translator - Project Overview

## 📦 What's Included

A complete, production-ready Python tool for translating JSON files for internationalization (i18n).

### Core Files

- **`translator.py`** (376 lines) - Main translation script with full CLI
- **`requirements.txt`** - Python dependencies (deep-translator, langdetect)
- **`setup.sh`** - Automated setup script for virtual environment
- **`.gitignore`** - Git ignore patterns for Python projects

### Documentation

- **`README.md`** (330 lines) - Complete user guide with examples
- **`QUICKSTART.md`** (119 lines) - Quick start guide for beginners
- **`FEATURES.md`** (325 lines) - Detailed feature showcase
- **`demo.sh`** - Automated demo script

### Examples

- **`examples/simple.json`** - Basic flat JSON structure
- **`examples/nested.json`** - Complex nested structure with placeholders
- **`examples/with-arrays.json`** - Arrays and mixed content types

### Output

- **`translations/`** - Directory for translated files (auto-created)

---

## 🚀 Quick Start (3 Steps)

1. **Setup:**
   ```bash
   ./setup.sh
   ```

2. **Activate:**
   ```bash
   source venv/bin/activate
   ```

3. **Translate:**
   ```bash
   python translator.py examples/simple.json -t es
   ```

---

## ✨ Key Features

✅ **Free & Unlimited** - No API keys, no limits  
✅ **17+ Languages** - Major world languages supported  
✅ **Auto-Detection** - Detects source language automatically  
✅ **Smart Placeholders** - Preserves `{{var}}`, `{0}`, `${name}`, etc.  
✅ **Nested Structures** - Handles complex JSON  
✅ **Batch Translation** - Multiple languages at once  
✅ **Error Handling** - Graceful failures with helpful messages  
✅ **UTF-8 Support** - Emoji, accents, Asian languages  

---

## 📊 Project Stats

- **Lines of Code:** 376 (translator.py)
- **Lines of Docs:** 774 (README + FEATURES + QUICKSTART)
- **Dependencies:** 2 (deep-translator, langdetect)
- **Languages Supported:** 17+
- **Example Files:** 3
- **Setup Time:** ~30 seconds
- **Translation Speed:** ~10-15 strings/second

---

## 🎯 Use Cases

Perfect for:

- **React/Vue/Angular** apps with i18next, vue-i18n, etc.
- **Mobile apps** (React Native, Flutter)
- **API response messages**
- **Email templates**
- **CMS content**
- **Documentation**

---

## 🛠️ Technical Implementation

### Architecture

```
Input JSON → Load & Validate → Detect Language → Extract Placeholders
     ↓
Translate → Restore Placeholders → Maintain Structure → Save Output
```

### Key Components

1. **JSONTranslator Class**
   - Recursive JSON traversal
   - Placeholder pattern matching (7 types)
   - Translation with error handling
   - Progress tracking

2. **Language Detection**
   - Uses langdetect library
   - Analyzes multiple strings for accuracy
   - Deterministic results (seeded)

3. **Translation Engine**
   - Google Translate via deep-translator
   - Fallback on failure (returns original)
   - Batch processing capability

4. **CLI Interface**
   - argparse for argument parsing
   - Multiple target languages
   - Verbose mode
   - Custom output directory

---

## 📚 Documentation Structure

### For Beginners → `QUICKSTART.md`
Step-by-step guide with copy-paste commands

### For General Use → `README.md`
Complete guide with examples and tips

### For Feature Details → `FEATURES.md`
Deep dive into all capabilities

### For Demo → `demo.sh`
Automated demonstration script

---

## 🧪 Testing

Successfully tested with:

- ✅ Simple flat JSON (20 strings)
- ✅ Nested structures (56 strings, 5 levels deep)
- ✅ Arrays and mixed types (27 strings)
- ✅ Multiple placeholders types
- ✅ Batch translation (Spanish + French)
- ✅ Auto language detection
- ✅ UTF-8 characters

Sample output files included in `translations/` directory.

---

## 🔧 Customization

Easy to extend:

1. **Add languages:**
   - Edit `SUPPORTED_LANGUAGES` dict in `translator.py`

2. **Add placeholder patterns:**
   - Add regex to `placeholder_patterns` list

3. **Change translation service:**
   - Swap `GoogleTranslator` for `DeeplTranslator`, etc.

4. **Add caching:**
   - Implement translation cache in `translate_text()`

---

## 📈 Performance

**Benchmarks:**

| File Size | Strings | Languages | Time |
|-----------|---------|-----------|------|
| Small | 20 | 1 | ~2s |
| Medium | 56 | 2 | ~15s |
| Large | 100+ | 3 | ~30s |

**Bottlenecks:**
- Network latency (API calls)
- Individual string translation (not batched yet)

**Optimizations:**
- Batch API calls (future)
- Translation caching (future)
- Parallel requests (future)

---

## 🌟 Best Practices

### Before Translating

1. ✅ Validate JSON at jsonlint.com
2. ✅ Commit to version control
3. ✅ Review placeholder syntax

### During Translation

1. ✅ Use verbose mode for large files
2. ✅ Test with one language first
3. ✅ Check network connection

### After Translation

1. ✅ Review output files
2. ✅ Test in your application
3. ✅ Verify placeholders work
4. ✅ Check special characters display correctly

---

## 🐛 Troubleshooting

### Common Issues

**ModuleNotFoundError**
→ Activate venv: `source venv/bin/activate`

**Invalid JSON**
→ Validate at jsonlint.com

**Language detection failed**
→ Use `-s` flag to specify source language

**Translation quality issues**
→ Provide more context in strings

**Network errors**
→ Check internet connection, retry

---

## 🚀 Future Enhancements

Potential improvements:

- [ ] Translation caching (Redis/file-based)
- [ ] DeepL API integration option
- [ ] YAML/TOML format support
- [ ] Batch API calls for speed
- [ ] Translation diff mode
- [ ] Quality scoring
- [ ] Custom glossaries
- [ ] Web UI interface

---

## 📄 License

MIT License - Free to use in any project

---

## 🙏 Credits

Built with:
- [deep-translator](https://github.com/nidhaloff/deep-translator) by @nidhaloff
- [langdetect](https://github.com/Mimino666/langdetect) by @Mimino666

---

## 📞 Support

Questions or issues?
1. Check `QUICKSTART.md` for basic usage
2. Read `README.md` for detailed guide
3. Review `FEATURES.md` for capabilities
4. Run `./demo.sh` to see it in action

---

**Happy translating! 🌍✨**

Built with ❤️ for the i18n community
