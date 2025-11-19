# Feature Showcase

This document demonstrates all the key features of the JSON i18n Translator.

## ✨ Feature Overview

### 1. **Auto Language Detection**

The tool can automatically detect the source language from your JSON content:

```bash
# No need to specify source language
python translator.py input.json -t es
```

**How it works:**
- Collects sample strings from the JSON
- Uses `langdetect` library to identify the language
- Supports 55+ languages with high accuracy

---

### 2. **Preserves All Placeholder Types**

The translator intelligently preserves interpolation variables used by various i18n frameworks:

| Framework | Placeholder | Example | Preserved? |
|-----------|-------------|---------|------------|
| i18next | `{{var}}` | "Hello {{username}}" | ✅ |
| Vue i18n | `{var}` | "Hello {name}" | ✅ |
| .NET/Java | `{0}` | "You have {0} messages" | ✅ |
| Python | `%(var)s` | "Email: %(email)s" | ✅ |
| JavaScript | `${var}` | "Welcome ${name}!" | ✅ |
| C-style | `%s`, `%d` | "Hello %s" | ✅ |

**Example:**

Input:
```json
{
  "welcome": "Welcome back, {{username}}!",
  "messages": "You have {0} new messages",
  "greeting": "Hello, ${name}!"
}
```

Output (Spanish):
```json
{
  "welcome": "¡Bienvenido de nuevo, {{username}}!",
  "messages": "Tienes {0} mensajes nuevos",
  "greeting": "¡Hola, ${name}!"
}
```

---

### 3. **Nested JSON Structure Support**

Maintains complex nested objects and arrays:

Input:
```json
{
  "auth": {
    "login": {
      "title": "Sign in",
      "errors": {
        "invalid": "Invalid credentials"
      }
    }
  },
  "menu": ["Home", "About", "Contact"]
}
```

Output maintains exact same structure with translated values.

---

### 4. **Batch + Parallel Translation**

Translate to multiple languages AND group strings to reduce API calls:
```bash
python translator.py input.json -t es fr de it pt ja zh-CN --batch-size 18 --max-workers 4
```

What happens under the hood:
- Strings are collected and split into batches (default 15)
- Each batch is translated as a combined request
- Multiple batches run in parallel (threads)

Benefits:
- Fewer network round trips
- Better throughput for medium/large files
- Configurable: `--batch-size`, `--max-workers`

---

### 5. **Smart File Naming**

Automatically generates output files with language codes:

| Input File | Target Lang | Output File |
|------------|-------------|-------------|
| `en.json` | Spanish | `en.es.json` |
| `messages.json` | French | `messages.fr.json` |
| `app-en.json` | German | `app-en.de.json` |

---

### 6. **Verbose Mode**

Track translation progress in real-time:

```bash
python translator.py input.json -t es -v
```

Output:
```
============================================================
Translating to Spanish (es)
============================================================
Detected language: en (English)
Translating from en to es...
Translated 10 strings...
Translated 20 strings...
Translated 30 strings...
✓ Translation complete! Translated 35 strings.
Output saved to: translations/input.es.json
```

---

### 7. **17+ Language Support**

Built-in support for major languages:

- 🇬🇧 English (`en`)
- 🇪🇸 Spanish (`es`)
- 🇫🇷 French (`fr`)
- 🇩🇪 German (`de`)
- 🇮🇹 Italian (`it`)
- 🇵🇹 Portuguese (`pt`)
- 🇯🇵 Japanese (`ja`)
- 🇨🇳 Chinese (`zh-CN`)
- 🇷🇺 Russian (`ru`)
- 🇸🇦 Arabic (`ar`)
- 🇮🇳 Hindi (`hi`)
- 🇰🇷 Korean (`ko`)
- 🇳🇱 Dutch (`nl`)
- 🇵🇱 Polish (`pl`)
- 🇸🇪 Swedish (`sv`)
- 🇹🇷 Turkish (`tr`)
- 🇻🇳 Vietnamese (`vi`)

---

### 8. **Free & Unlimited**

- ✅ No API keys required
- ✅ No usage limits
- ✅ No sign-ups or authentication
- ✅ Uses Google Translate via `deep-translator`

---

### 9. **Error Handling**

Graceful error handling for real-world scenarios:

- **Invalid JSON:** Clear error messages with line numbers
- **Network errors:** Retries with original text on failure
- **Missing files:** Helpful file path suggestions
- **Unsupported languages:** Lists available options

---

### 10. **Custom Output Directory**

Choose where to save translations:

```bash
python translator.py input.json -t es -o ./locales
python translator.py input.json -t es -o ../shared/i18n
python translator.py input.json -t es -o /path/to/project/translations
```

---

### 11. **Persistent Translation Cache**

Automatically stores translations in a SQLite DB (`.translation_cache.db`).

```bash
python translator.py messages.json -t es
# Repeat run → Instant cache hits
python translator.py messages.json -t es -v
```

Cache Advantages:
- Avoids re-translating identical strings
- Dramatically faster iterative development
- Reusable across languages pairs (per source-target)

Disable if needed:
```bash
python translator.py input.json -t fr --no-cache
```

### 12. **Arrays & Complex Structures**

Handles all JSON data types:

```json
{
  "menu": ["Home", "About", "Contact"],
  "features": [
    {
      "title": "Fast",
      "desc": "Lightning speed"
    },
    {
      "title": "Secure",
      "desc": "Encrypted data"
    }
  ],
  "config": {
    "timeout": 5000,
    "enabled": true,
    "message": "System ready"
  }
}
```

**Result:**
- Arrays of strings → translated
- Objects in arrays → translated
- Numbers, booleans → preserved as-is
- Nested structures → maintained

---

### 13. **UTF-8 Support**

Properly handles all unicode characters:

- Emoji: 🎉 ✨ 🌍
- Accents: é, ñ, ü, ç
- Asian languages: 你好, こんにちは, 안녕하세요
- RTL languages: Arabic, Hebrew

---

## Real-World Use Cases

### Case 1: React i18next App

```bash
# Original English file
python translator.py src/locales/en.json -s en -t es fr de it

# Generates:
# src/locales/en.es.json
# src/locales/en.fr.json
# src/locales/en.de.json
# src/locales/en.it.json
```

### Case 2: Vue.js Internationalization

```bash
python translator.py src/i18n/en-US.json -t es fr ja zh-CN -v
```

### Case 3: Mobile App (React Native)

```bash
python translator.py locales/en.json -t es pt hi ar -o ./app/locales
```

### Case 4: API Response Messages

```bash
python translator.py messages/errors.json -s en -t es fr de -v
```

---

## Performance (v1.1.0 Optimized)

| Scenario | Strings | First Run (No Cache) | Cached Repeat |
|----------|---------|----------------------|---------------|
| Simple file | 20 | ~1s | <0.15s |
| Nested file | 56 | ~2.6s | ~0.16s |
| Previous naive (pre v1.1.0) | 56 | ~22–24s | N/A |

Mechanisms:
- Batch grouping lowers API overhead
- Threaded execution speeds total processing time
- Persistent cache reduces repeated work to near-zero

Tuning Guidelines:
- `--batch-size` 10–20 ideal; too large may reduce accuracy slightly
- `--max-workers` 2–4 recommended (higher increases rate-limit risk)
- Keep cache enabled for iterative runs

---

## Comparison with Alternatives

| Feature | This Tool | Manual Translation | Paid APIs |
|---------|-----------|-------------------|-----------|
| Cost | Free | N/A | $$$ |
| Speed | Fast | Slow | Fast |
| Accuracy | Good | Excellent | Excellent |
| Placeholders | Auto-preserved | Manual | Manual/Auto |
| Setup | Easy | N/A | Complex |
| Limits | None | None | Yes |

---

## Tips for Best Results

1. **Use complete sentences** - Better context = better translation
2. **Keep keys in English** - Only values get translated
3. **Review important strings** - Machine translation isn't perfect
4. **Use verbose mode** - Track progress on large files
5. **Batch similar languages** - Translate Romance languages together
6. **Version control** - Commit before translating for easy rollback

---

## Future Enhancements (Potential)

- 📊 Translation quality scoring
- 🔀 YAML / TOML formats
- 🌐 Optional DeepL integration
- 📝 Glossary / translation memory
- 🔍 Diff mode (only new / changed keys)
- 🎯 Context-aware translation improvements

---

**Ready to translate?** Check out [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions!
