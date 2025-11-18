#!/bin/bash
# Setup script for JSON i18n Translator

echo "🚀 Setting up JSON i18n Translator..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use the translator:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the translator: python translator.py input.json -t es"
echo "  3. When done, deactivate: deactivate"
echo ""
echo "Quick test:"
echo "  source venv/bin/activate && python translator.py --list-languages"
echo ""
