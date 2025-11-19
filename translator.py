#!/usr/bin/env python3
"""
JSON i18n Translator
A tool to translate JSON files for internationalization using free translation APIs.
"""

import json
import re
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Union
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory, LangDetectException

# Set seed for consistent language detection results
DetectorFactory.seed = 0

# Supported languages with their codes
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ja': 'Japanese',
    'zh-CN': 'Chinese (Simplified)',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'ko': 'Korean',
    'nl': 'Dutch',
    'pl': 'Polish',
    'sv': 'Swedish',
    'tr': 'Turkish',
    'vi': 'Vietnamese', 
	'ca': 'Catalan',
}


class JSONTranslator:
    """Handles translation of JSON files while preserving structure and placeholders."""
    
    def __init__(self, source_lang: str = 'auto', target_lang: str = 'es', verbose: bool = False):
        """
        Initialize the translator.
        
        Args:
            source_lang: Source language code ('auto' for auto-detection)
            target_lang: Target language code
            verbose: Enable verbose output
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.verbose = verbose
        self.translator = None
        self.translation_count = 0
        
        # Regex patterns for preserving interpolation placeholders
        self.placeholder_patterns = [
            r'\{\{[^}]+\}\}',          # {{variable}} - i18next, Handlebars
            r'\{[0-9]+\}',              # {0}, {1} - .NET, Java
            r'\{[a-zA-Z_][a-zA-Z0-9_]*\}',  # {name} - Python, Vue i18n
            r'%[sd]',                   # %s, %d - C-style
            r'%\([^)]+\)[sd]',          # %(name)s - Python
            r'\$\{[^}]+\}',             # ${variable} - JavaScript
            r'\[\[[\w\s]+\]\]',         # [[key]] - Some frameworks
        ]
        
    def _init_translator(self):
        """Initialize the translator with current source and target languages."""
        try:
            self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
        except Exception as e:
            raise Exception(f"Failed to initialize translator: {str(e)}")
    
    def detect_language(self, json_data: Dict[str, Any]) -> str:
        """
        Detect the language of the JSON content.
        
        Args:
            json_data: The JSON data to analyze
            
        Returns:
            Language code (e.g., 'en', 'es')
        """
        # Collect all string values from the JSON
        text_samples = []
        self._collect_strings(json_data, text_samples, max_samples=20)
        
        if not text_samples:
            raise ValueError("No text found in JSON for language detection")
        
        # Combine samples for better detection accuracy
        combined_text = ' '.join(text_samples[:10])  # Use first 10 samples
        
        try:
            detected_lang = detect(combined_text)
            if self.verbose:
                print(f"Detected language: {detected_lang} ({SUPPORTED_LANGUAGES.get(detected_lang, 'Unknown')})")
            return detected_lang
        except LangDetectException as e:
            raise ValueError(f"Failed to detect language: {str(e)}")
    
    def _collect_strings(self, data: Any, collector: List[str], max_samples: int = 20):
        """
        Recursively collect string values from JSON data.
        
        Args:
            data: The data to traverse
            collector: List to collect strings into
            max_samples: Maximum number of samples to collect
        """
        if len(collector) >= max_samples:
            return
        
        if isinstance(data, dict):
            for value in data.values():
                self._collect_strings(value, collector, max_samples)
        elif isinstance(data, list):
            for item in data:
                self._collect_strings(item, collector, max_samples)
        elif isinstance(data, str) and data.strip():
            collector.append(data)
    
    def _extract_placeholders(self, text: str) -> tuple:
        """
        Extract placeholders from text and replace with temporary markers.
        
        Args:
            text: The text to process
            
        Returns:
            Tuple of (processed_text, list of placeholders)
        """
        placeholders = []
        processed_text = text
        
        for pattern in self.placeholder_patterns:
            matches = re.findall(pattern, processed_text)
            for match in matches:
                placeholder_id = f"__PLACEHOLDER_{len(placeholders)}__"
                placeholders.append(match)
                processed_text = processed_text.replace(match, placeholder_id, 1)
        
        return processed_text, placeholders
    
    def _restore_placeholders(self, text: str, placeholders: List[str]) -> str:
        """
        Restore placeholders in translated text.
        
        Args:
            text: The translated text with markers
            placeholders: List of original placeholders
            
        Returns:
            Text with restored placeholders
        """
        result = text
        for i, placeholder in enumerate(placeholders):
            marker = f"__PLACEHOLDER_{i}__"
            result = result.replace(marker, placeholder)
        
        return result
    
    def translate_text(self, text: str) -> str:
        """
        Translate a single text string while preserving placeholders.
        
        Args:
            text: The text to translate
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        # Extract placeholders
        processed_text, placeholders = self._extract_placeholders(text)
        
        try:
            # Translate the text
            translated = self.translator.translate(processed_text)
            
            # Restore placeholders
            if placeholders:
                translated = self._restore_placeholders(translated, placeholders)
            
            self.translation_count += 1
            if self.verbose and self.translation_count % 10 == 0:
                print(f"Translated {self.translation_count} strings...")
            
            return translated
        except Exception as e:
            if self.verbose:
                print(f"Warning: Failed to translate '{text[:50]}...': {str(e)}", file=sys.stderr)
            return text  # Return original text on failure
    
    def translate_json(self, data: Any) -> Any:
        """
        Recursively translate JSON data while preserving structure.
        
        Args:
            data: The JSON data to translate
            
        Returns:
            Translated JSON data
        """
        if isinstance(data, dict):
            return {key: self.translate_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.translate_json(item) for item in data]
        elif isinstance(data, str):
            return self.translate_text(data)
        else:
            # Return other types (numbers, booleans, null) as-is
            return data
    
    def translate_file(self, input_path: Path, output_path: Path):
        """
        Translate a JSON file and save the result.
        
        Args:
            input_path: Path to input JSON file
            output_path: Path to output JSON file
        """
        # Read input file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to read file: {str(e)}")
        
        # Auto-detect source language if needed
        if self.source_lang == 'auto':
            detected_lang = self.detect_language(data)
            self.source_lang = detected_lang
        
        # Initialize translator
        self._init_translator()
        
        # Translate the data
        if self.verbose:
            print(f"Translating from {self.source_lang} to {self.target_lang}...")
        
        translated_data = self.translate_json(data)
        
        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
        if self.verbose:
            print(f"✓ Translation complete! Translated {self.translation_count} strings.")
            print(f"Output saved to: {output_path}")


def list_languages():
    """Display all supported languages."""
    print("\nSupported Languages:")
    print("-" * 50)
    for code, name in sorted(SUPPORTED_LANGUAGES.items(), key=lambda x: x[1]):
        print(f"  {code:8} - {name}")
    print()


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Translate JSON files for internationalization (i18n)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect source language and translate to Spanish
  python translator.py input.json -t es
  
  # Translate from English to multiple languages
  python translator.py input.json -s en -t es fr de
  
  # Specify output directory
  python translator.py input.json -t es -o ./translations
  
  # List all supported languages
  python translator.py --list-languages
        """
    )
    
    parser.add_argument('input', nargs='?', type=str,
                        help='Input JSON file path')
    parser.add_argument('-s', '--source', type=str, default='auto',
                        help='Source language code (default: auto-detect)')
    parser.add_argument('-t', '--target', nargs='+', type=str,
                        help='Target language code(s) (e.g., es fr de)')
    parser.add_argument('-o', '--output', type=str, default='./translations',
                        help='Output directory (default: ./translations)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('-l', '--list-languages', action='store_true',
                        help='List all supported languages and exit')
    
    args = parser.parse_args()
    
    # List languages and exit
    if args.list_languages:
        list_languages()
        return 0
    
    # Validate required arguments
    if not args.input:
        parser.error("Input file is required (unless using --list-languages)")
    if not args.target:
        parser.error("Target language(s) required (use -t)")
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    
    if not input_path.suffix.lower() == '.json':
        print(f"Warning: Input file does not have .json extension", file=sys.stderr)
    
    # Validate language codes
    for lang_code in args.target:
        if lang_code not in SUPPORTED_LANGUAGES:
            print(f"Error: Unsupported target language: {lang_code}", file=sys.stderr)
            print(f"Use --list-languages to see supported languages", file=sys.stderr)
            return 1
    
    if args.source != 'auto' and args.source not in SUPPORTED_LANGUAGES:
        print(f"Error: Unsupported source language: {args.source}", file=sys.stderr)
        print(f"Use --list-languages to see supported languages", file=sys.stderr)
        return 1
    
    # Process translations
    output_dir = Path(args.output)
    base_name = input_path.stem
    
    try:
        for target_lang in args.target:
            print(f"\n{'='*60}")
            print(f"Translating to {SUPPORTED_LANGUAGES[target_lang]} ({target_lang})")
            print(f"{'='*60}")
            
            # Create output filename
            output_filename = f"{base_name}.{target_lang}.json"
            output_path = output_dir / output_filename
            
            # Translate
            translator = JSONTranslator(
                source_lang=args.source,
                target_lang=target_lang,
                verbose=args.verbose
            )
            
            translator.translate_file(input_path, output_path)
            
            print(f"✓ Saved to: {output_path}")
        
        print(f"\n{'='*60}")
        print(f"All translations completed successfully!")
        print(f"{'='*60}\n")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
