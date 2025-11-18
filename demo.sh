#!/bin/bash
# Demo script to showcase the JSON i18n Translator capabilities

echo "=================================="
echo "JSON i18n Translator - Demo"
echo "=================================="
echo ""

# Activate virtual environment
source venv/bin/activate

echo "📋 Step 1: List supported languages"
echo "Command: python translator.py --list-languages"
python translator.py --list-languages

echo ""
echo "=================================="
echo "📄 Step 2: Translate simple.json to Spanish"
echo "Command: python translator.py examples/simple.json -t es"
python translator.py examples/simple.json -t es

echo ""
echo "📄 Output preview (first 10 lines):"
head -10 translations/simple.es.json

echo ""
echo "=================================="
echo "📄 Step 3: Translate nested.json to Spanish and French"
echo "Command: python translator.py examples/nested.json -t es fr"
python translator.py examples/nested.json -t es fr

echo ""
echo "🔍 Verifying placeholders are preserved..."
echo "Checking Spanish translation:"
grep -E '(\{\{|\{[0-9]|\$\{|%\()' translations/nested.es.json | head -5

echo ""
echo "=================================="
echo "📄 Step 4: Translate with-arrays.json to Spanish (verbose)"
echo "Command: python translator.py examples/with-arrays.json -t es -v"
python translator.py examples/with-arrays.json -t es -v

echo ""
echo "=================================="
echo "✅ Demo Complete!"
echo ""
echo "Generated files:"
ls -lh translations/
echo ""
echo "To run your own translations:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run: python translator.py your-file.json -t es"
echo "  3. Check output: cat translations/your-file.es.json"
echo ""

deactivate
