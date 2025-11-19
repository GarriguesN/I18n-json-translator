#!/usr/bin/env python3
"""
JSON i18n Translator
A tool to translate JSON files for internationalization using free translation APIs.
"""

import json
import re
import argparse
import sys
import sqlite3
import hashlib
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory, LangDetectException

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Set seed for consistent language detection results
DetectorFactory.seed = 0

# Pre-compile regex patterns for performance
PLACEHOLDER_PATTERNS_COMPILED = [
    re.compile(r'\{\{[^}]+\}\}'),          # {{variable}}
    re.compile(r'\{[0-9]+\}'),              # {0}, {1}
    re.compile(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}'),  # {name}
    re.compile(r'%[sd]'),                   # %s, %d
    re.compile(r'%\([^)]+\)[sd]'),          # %(name)s
    re.compile(r'\$\{[^}]+\}'),             # ${variable}
    re.compile(r'\[\[[\w\s]+\]\]'),         # [[key]]
]

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


class TranslationCache:
    """SQLite-based cache for storing and retrieving translations."""
    
    def __init__(self, cache_file: str = '.translation_cache.db'):
        """
        Initialize the translation cache.
        
        Args:
            cache_file: Path to the SQLite database file
        """
        self.cache_file = cache_file
        self._connections = {}
        self._pending_writes = []
        self._write_lock = threading.Lock()
        self._init_db()
    
    def _get_connection(self):
        """Get a thread-local database connection with optimizations."""
        thread_id = threading.get_ident()
        
        if thread_id not in self._connections:
            conn = sqlite3.connect(self.cache_file, check_same_thread=False, isolation_level=None)
            # Performance optimizations
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=10000')
            conn.execute('PRAGMA temp_store=MEMORY')
            self._connections[thread_id] = conn
        
        return self._connections[thread_id]
    
    def _init_db(self):
        """Create the cache database and table if they don't exist."""
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                text_hash TEXT,
                source_lang TEXT,
                target_lang TEXT,
                original_text TEXT,
                translated_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (text_hash, source_lang, target_lang)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON translations(text_hash)')
        conn.commit()
        conn.close()
    
    def _get_hash(self, text: str) -> str:
        """Generate a hash for the text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Retrieve a cached translation.
        
        Args:
            text: Original text
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text if found in cache, None otherwise
        """
        text_hash = self._get_hash(text)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT translated_text FROM translations WHERE text_hash = ? AND source_lang = ? AND target_lang = ?',
            (text_hash, source_lang, target_lang)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def set(self, text: str, source_lang: str, target_lang: str, translated_text: str):
        """
        Store a translation in the cache with optimized batching.
        
        Args:
            text: Original text
            source_lang: Source language code
            target_lang: Target language code
            translated_text: Translated text
        """
        text_hash = self._get_hash(text)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Direct insert for better performance (no transaction overhead)
        cursor.execute(
            '''INSERT OR REPLACE INTO translations 
               (text_hash, source_lang, target_lang, original_text, translated_text)
               VALUES (?, ?, ?, ?, ?)''',
            (text_hash, source_lang, target_lang, text, translated_text)
        )
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM translations')
        total = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT source_lang || "-" || target_lang) FROM translations')
        pairs = cursor.fetchone()[0]
        return {'total_translations': total, 'language_pairs': pairs}
    
    def close(self):
        """Close all database connections."""
        if hasattr(self, '_connections'):
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()


class JSONTranslator:
    """Handles translation of JSON files while preserving structure and placeholders."""
    
    def __init__(self, source_lang: str = 'auto', target_lang: str = 'es', verbose: bool = False, 
                 use_cache: bool = True, max_workers: int = 3, diff_mode: bool = False, glossary: Dict[str, str] = None,
                 batch_size: int = 0):
        """
        Initialize the translator.
        
        Args:
            source_lang: Source language code ('auto' for auto-detection)
            target_lang: Target language code
            verbose: Enable verbose output
            use_cache: Enable translation cache
            max_workers: Number of parallel translation threads (2-5 recommended)
            diff_mode: Only translate new/changed keys (requires existing output file)
            glossary: Optional dict of term replacements {source_term: target_term}
            batch_size: Number of strings per super-batch (0=disabled, 20-50 recommended for large files)
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.verbose = verbose
        self.use_cache = use_cache
        self.max_workers = max_workers
        self.diff_mode = diff_mode
        self.glossary = glossary or {}
        self.batch_size = batch_size
        self.translator = None
        self._translators = {}  # Thread-local translators
        self._lock = threading.Lock()
        self.translation_count = 0
        self.cache_hits = 0
        self.cache = TranslationCache() if use_cache else None
        
    def _init_translator(self):
        """Initialize the translator with current source and target languages."""
        try:
            self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
        except Exception as e:
            raise Exception(f"Failed to initialize translator: {str(e)}")
    
    def _get_translator(self):
        """Get a thread-safe translator instance."""
        thread_id = threading.get_ident()
        if thread_id not in self._translators:
            with self._lock:
                if thread_id not in self._translators:
                    self._translators[thread_id] = GoogleTranslator(
                        source=self.source_lang, 
                        target=self.target_lang
                    )
        return self._translators[thread_id]
    
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
        Uses pre-compiled regex patterns for better performance.
        
        Args:
            text: The text to process
            
        Returns:
            Tuple of (processed_text, list of placeholders)
        """
        placeholders = []
        processed_text = text
        
        for pattern in PLACEHOLDER_PATTERNS_COMPILED:
            matches = pattern.findall(processed_text)
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
    
    def _apply_glossary(self, text: str) -> str:
        """
        Apply custom glossary terms to translated text.
        Case-insensitive word boundary matching.
        
        Args:
            text: Translated text
            
        Returns:
            Text with glossary terms applied
        """
        if not self.glossary:
            return text
        
        result = text
        for source_term, target_term in self.glossary.items():
            # Case-insensitive word boundary replacement
            pattern = re.compile(r'\b' + re.escape(source_term) + r'\b', re.IGNORECASE)
            result = pattern.sub(target_term, result)
        
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
        
        # Check cache first
        if self.cache:
            cached = self.cache.get(text, self.source_lang, self.target_lang)
            if cached:
                self.cache_hits += 1
                return cached
        
        # Extract placeholders
        processed_text, placeholders = self._extract_placeholders(text)
        
        try:
            # Translate the text
            translated = self.translator.translate(processed_text)
            
            # Restore placeholders
            if placeholders:
                translated = self._restore_placeholders(translated, placeholders)
            
            # Store in cache
            if self.cache:
                self.cache.set(text, self.source_lang, self.target_lang, translated)
            
            self.translation_count += 1
            if self.verbose and self.translation_count % 10 == 0:
                print(f"Translated {self.translation_count} strings... (cache hits: {self.cache_hits})")
            
            return translated
        except Exception as e:
            if self.verbose:
                print(f"Warning: Failed to translate '{text[:50]}...': {str(e)}", file=sys.stderr)
            return text  # Return original text on failure
    
    def _translate_single_indexed(self, index: int, text: str) -> Tuple[int, str]:
        """
        Translate a single text with index for parallel processing.
        Thread-safe with isolated translator instance.
        
        Args:
            index: Original position index
            text: Text to translate
            
        Returns:
            Tuple of (index, translated_text)
        """
        if not text or not text.strip():
            return (index, text)
        
        # Check cache first (thread-safe)
        if self.cache:
            cached = self.cache.get(text, self.source_lang, self.target_lang)
            if cached:
                with self._lock:
                    self.cache_hits += 1
                return (index, cached)
        
        # Extract placeholders
        processed, placeholders = self._extract_placeholders(text)
        
        try:
            # Get thread-safe translator
            translator = self._get_translator()
            translated = translator.translate(processed)
            
            if placeholders:
                translated = self._restore_placeholders(translated, placeholders)
            
            # Apply glossary terms
            if self.glossary:
                translated = self._apply_glossary(translated)
            
            # Store in cache (thread-safe)
            if self.cache:
                self.cache.set(text, self.source_lang, self.target_lang, translated)
            
            with self._lock:
                self.translation_count += 1
            
            return (index, translated)
        except Exception as e:
            if self.verbose:
                print(f"Warning: Failed to translate '{text[:40]}': {e}", file=sys.stderr)
            return (index, text)
    
    def _process_super_batch(self, batch_info: Tuple[int, int, List[str]]) -> List[Tuple[int, str]]:
        """
        Process a super-batch of strings with its own thread pool.
        
        Args:
            batch_info: Tuple of (start_index, batch_id, strings)
            
        Returns:
            List of (index, translated_text) tuples
        """
        start_index, batch_id, strings = batch_info
        results = []
        
        # Use thread pool for this super-batch
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._translate_single_indexed, start_index + idx, text): idx
                for idx, text in enumerate(strings)
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    idx = futures[future]
                    if self.verbose:
                        print(f"Warning: Super-batch {batch_id} failed at index {idx}: {e}", file=sys.stderr)
                    results.append((start_index + idx, strings[idx]))
        
        return results
    
    def _collect_all_strings(self, data: Any) -> List[Tuple[List[Any], Any, str]]:
        """
        Collect all translatable strings from JSON with their paths.
        
        Args:
            data: The JSON data to traverse
            
        Returns:
            List of tuples: (path, parent, key/index, value)
        """
        strings = []
        
        def traverse(obj, path=[]):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    traverse(value, path + [('dict', obj, key)])
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    traverse(item, path + [('list', obj, i)])
            elif isinstance(obj, str) and obj.strip():
                strings.append((path, obj))
        
        traverse(data)
        return strings
    
    def _compute_diff(self, new_data: Any, existing_data: Any) -> Dict[str, Any]:
        """
        Compute which keys are new or changed between new and existing data.
        
        Args:
            new_data: New source JSON data
            existing_data: Existing translated JSON data
            
        Returns:
            Dict with 'new_keys' and 'changed_keys' lists containing paths
        """
        new_strings = {}
        existing_strings = {}
        
        def collect_with_path(obj, path="", target=None):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    collect_with_path(value, new_path, target)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    collect_with_path(item, new_path, target)
            elif isinstance(obj, str) and obj.strip():
                target[path] = obj
        
        collect_with_path(new_data, target=new_strings)
        collect_with_path(existing_data, target=existing_strings)
        
        new_keys = [k for k in new_strings if k not in existing_strings]
        changed_keys = [k for k in new_strings if k in existing_strings and new_strings[k] != existing_strings[k]]
        
        return {
            'new_keys': new_keys,
            'changed_keys': changed_keys,
            'new_strings': new_strings,
            'existing_strings': existing_strings
        }
    
    def translate_json(self, data: Any) -> Any:
        """
        Recursively translate JSON data while preserving structure.
        Uses batch translation and threading for optimal performance.
        
        Args:
            data: The JSON data to translate
            
        Returns:
            Translated JSON data
        """
        import copy
        
        # Create a deep copy to avoid modifying original
        result = copy.deepcopy(data)
        
        # Collect all strings with their paths
        string_data = self._collect_all_strings(result)
        
        if not string_data:
            return result
        
        # Extract just the strings for translation
        strings_to_translate = [item[1] for item in string_data]
        
        if self.verbose:
            if self.batch_size > 0:
                print(f"Translating {len(strings_to_translate)} strings using 2-level batching (super-batch={self.batch_size}, workers={self.max_workers})...")
            else:
                print(f"Translating {len(strings_to_translate)} strings using parallel mode (workers={self.max_workers})...")
        
        # Prepare ordered result container
        translated_strings = [None] * len(strings_to_translate)
        
        # 2-level batching: super-batches processed in parallel, each with thread pool
        if self.batch_size > 0 and len(strings_to_translate) > self.batch_size:
            # Divide into super-batches
            super_batches = []
            for i in range(0, len(strings_to_translate), self.batch_size):
                batch_strings = strings_to_translate[i:i + self.batch_size]
                super_batches.append((i, len(super_batches), batch_strings))
            
            if self.verbose:
                print(f"Created {len(super_batches)} super-batches of ~{self.batch_size} strings each")
            
            # Process super-batches in parallel
            if TQDM_AVAILABLE and self.verbose:
                pbar = tqdm(total=len(strings_to_translate), desc="Translating", unit="string")
            else:
                pbar = None
            
            # Use process pool or sequential depending on super-batch count
            if len(super_batches) > 1:
                with ThreadPoolExecutor(max_workers=min(len(super_batches), 4)) as super_executor:
                    super_futures = {
                        super_executor.submit(self._process_super_batch, batch_info): batch_info[1]
                        for batch_info in super_batches
                    }
                    
                    for future in as_completed(super_futures):
                        try:
                            batch_results = future.result()
                            for idx, translated in batch_results:
                                translated_strings[idx] = translated
                                if pbar:
                                    pbar.update(1)
                        except Exception as e:
                            batch_id = super_futures[future]
                            if self.verbose and not pbar:
                                print(f"Warning: Super-batch {batch_id} failed: {e}", file=sys.stderr)
            else:
                # Single super-batch, process directly
                batch_results = self._process_super_batch(super_batches[0])
                for idx, translated in batch_results:
                    translated_strings[idx] = translated
                    if pbar:
                        pbar.update(1)
            
            if pbar:
                pbar.close()
        
        # Standard parallel execution (no super-batching)
        elif self.max_workers > 1:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all translations with their indices
                futures = {
                    executor.submit(self._translate_single_indexed, idx, text): idx 
                    for idx, text in enumerate(strings_to_translate)
                }
                
                # Use tqdm progress bar if available and verbose
                if TQDM_AVAILABLE and self.verbose:
                    pbar = tqdm(total=len(strings_to_translate), desc="Translating", unit="string")
                else:
                    pbar = None
                
                completed_count = 0
                last_progress = 0
                for future in as_completed(futures):
                    try:
                        idx, translated = future.result()
                        translated_strings[idx] = translated
                        completed_count += 1
                        
                        if pbar:
                            pbar.update(1)
                        elif self.verbose and completed_count - last_progress >= 15:
                            # Fallback progress without tqdm
                            print(f"Progress: {completed_count}/{len(strings_to_translate)} strings translated")
                            last_progress = completed_count
                    except Exception as e:
                        idx = futures[future]
                        if self.verbose and not pbar:
                            print(f"Warning: Translation failed at index {idx}: {e}", file=sys.stderr)
                        translated_strings[idx] = strings_to_translate[idx]
                        completed_count += 1
                        if pbar:
                            pbar.update(1)
                
                if pbar:
                    pbar.close()
                elif self.verbose:
                    print(f"Progress: {len(strings_to_translate)}/{len(strings_to_translate)} strings translated")
        else:
            # Sequential fallback
            if TQDM_AVAILABLE and self.verbose:
                iterator = tqdm(enumerate(strings_to_translate), total=len(strings_to_translate), desc="Translating", unit="string")
            else:
                iterator = enumerate(strings_to_translate)
            
            for idx, text in iterator:
                _, translated = self._translate_single_indexed(idx, text)
                translated_strings[idx] = translated
                if not TQDM_AVAILABLE and self.verbose and (idx + 1) % 15 == 0:
                    print(f"Progress: {idx + 1}/{len(strings_to_translate)} strings translated")
            
            if not TQDM_AVAILABLE and self.verbose:
                print(f"Progress: {len(strings_to_translate)}/{len(strings_to_translate)} strings translated")
        
        # Apply translations back to the data structure
        for i, (path, original) in enumerate(string_data):
            if i < len(translated_strings):
                # Navigate to the location and update
                current = result
                for path_type, parent, key in path:
                    if path_type == 'dict':
                        if key in parent:
                            current = parent
                            break
                    elif path_type == 'list':
                        current = parent
                        break
                
                # Update the value
                if path:
                    path_type, parent, key = path[-1]
                    parent[key] = translated_strings[i]
        
        return result
    
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
        
        # Check for diff mode
        existing_data = None
        if self.diff_mode and output_path.exists():
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                if self.verbose:
                    print(f"Diff mode: Loading existing translation from {output_path}")
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not load existing file for diff: {e}")
                existing_data = None
        
        # Auto-detect source language if needed
        if self.source_lang == 'auto':
            detected_lang = self.detect_language(data)
            self.source_lang = detected_lang
        
        # Initialize translator
        self._init_translator()
        
        # Translate the data
        if self.verbose:
            print(f"Translating from {self.source_lang} to {self.target_lang}...")
            if self.cache:
                stats = self.cache.get_stats()
                print(f"Cache contains {stats['total_translations']} translations across {stats['language_pairs']} language pairs")
        
        # Diff mode: detect structural changes
        if self.diff_mode and existing_data:
            # Compare structure: check if keys match
            def get_structure(obj, path=""):
                keys = set()
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        keys.add(new_path)
                        keys.update(get_structure(value, new_path))
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_path = f"{path}[{i}]"
                        keys.add(new_path)
                        keys.update(get_structure(item, new_path))
                return keys
            
            source_keys = get_structure(data)
            existing_keys = get_structure(existing_data)
            new_keys = source_keys - existing_keys
            removed_keys = existing_keys - source_keys
            
            if self.verbose:
                print(f"Diff analysis: {len(new_keys)} new keys, {len(removed_keys)} removed keys")
            
            if len(new_keys) == 0:
                if self.verbose:
                    print("No structural changes detected. Using existing translation.")
                translated_data = existing_data
            else:
                # Translate and merge
                translated_data = self.translate_json(data)
        else:
            translated_data = self.translate_json(data)
        
        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
        if self.verbose:
            print(f"✓ Translation complete!")
            print(f"  • Total strings translated: {self.translation_count}")
            print(f"  • Cache hits: {self.cache_hits}")
            print(f"  • New translations: {self.translation_count}")
            print(f"  • Output saved to: {output_path}")
        
        # Close cache connection
        if self.cache:
            self.cache.close()


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
  
  # Disable cache (not recommended)
  python translator.py input.json -t es --no-cache
  
  # Adjust performance settings (parallel workers)
  python translator.py input.json -t es --max-workers 5
  
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
    parser.add_argument('--no-cache', action='store_true',
                        help='Disable translation cache')
    parser.add_argument('--max-workers', type=int, default=3,
                        help='Number of parallel translation threads (default: 3, range: 1-5)')
    parser.add_argument('--batch-size', type=int, default=0,
                        help='Super-batch size for 2-level parallelism (default: 0=disabled, 20-50 for large files)')
    parser.add_argument('--diff', action='store_true',
                        help='Translate only new or changed keys (compares with existing output)')
    parser.add_argument('--glossary', type=str,
                        help='Path to JSON glossary file for custom terminology {"term": "translation"}')
    
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
    
    # Validate performance settings
    if args.max_workers < 1 or args.max_workers > 5:
        print(f"Warning: max-workers should be between 1-5. Using default (3).", file=sys.stderr)
        args.max_workers = 3
    
    # Process translations
    output_dir = Path(args.output)
    base_name = input_path.stem
    
    # Load glossary if provided
    glossary = None
    if args.glossary:
        glossary_path = Path(args.glossary)
        if not glossary_path.exists():
            print(f"Error: Glossary file not found: {glossary_path}", file=sys.stderr)
            return 1
        try:
            with open(glossary_path, 'r', encoding='utf-8') as f:
                glossary = json.load(f)
            if args.verbose:
                print(f"Loaded glossary with {len(glossary)} terms from {glossary_path}")
        except Exception as e:
            print(f"Error loading glossary: {e}", file=sys.stderr)
            return 1
    
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
                verbose=args.verbose,
                use_cache=not args.no_cache,
                max_workers=args.max_workers,
                diff_mode=args.diff,
                glossary=glossary,
                batch_size=args.batch_size
            )
            
            translator.translate_file(input_path, output_path)
            
            if not args.verbose:
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
