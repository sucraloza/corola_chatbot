"""
Translation module for multi-language support
"""
import json
import os
from typing import Dict, Optional

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root, then into data/translations/
project_root = os.path.dirname(script_dir)
translations_dir = os.path.join(project_root, 'data', 'translations')

# Default language
DEFAULT_LANGUAGE = 'en'

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'pt_BR']

# Cache for loaded translations
_translations_cache: Dict[str, Dict] = {}


def load_translations(language: str = DEFAULT_LANGUAGE) -> Dict:
    """Load translations for a specific language."""
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
    
    # Return cached translations if available
    if language in _translations_cache:
        return _translations_cache[language]
    
    # Load from file
    translation_file = os.path.join(translations_dir, f'{language}.json')
    
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            _translations_cache[language] = translations
            return translations
    except FileNotFoundError:
        # Fallback to English if translation file not found
        if language != DEFAULT_LANGUAGE:
            return load_translations(DEFAULT_LANGUAGE)
        return {}
    except Exception as e:
        print(f"Error loading translations for {language}: {e}")
        return {}


def get_user_language(update) -> str:
    """Detect user language from Telegram user settings."""
    if update and update.effective_user:
        # Telegram provides language_code (e.g., 'pt-BR', 'en', 'es')
        lang_code = update.effective_user.language_code
        
        if lang_code:
            # Normalize language codes
            lang_code = lang_code.replace('-', '_').lower()
            
            # Map common variations
            if lang_code.startswith('pt'):
                return 'pt_BR'
            elif lang_code.startswith('en'):
                return 'en'
            
            # Check if exact match
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
    
    # Default to English
    return DEFAULT_LANGUAGE


def t(key_path: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Get translated string by key path.
    
    Args:
        key_path: Dot-separated path to translation key (e.g., 'welcome.title')
        language: Language code (default: 'en')
        **kwargs: Format arguments for string interpolation
    
    Returns:
        Translated string, or key_path if not found
    """
    translations = load_translations(language)
    
    # Navigate through nested dictionary
    keys = key_path.split('.')
    value = translations
    
    try:
        for key in keys:
            value = value[key]
        
        # Format string if kwargs provided
        if kwargs and isinstance(value, str):
            return value.format(**kwargs)
        
        return value
    except (KeyError, TypeError):
        # Fallback to English if key not found
        if language != DEFAULT_LANGUAGE:
            return t(key_path, DEFAULT_LANGUAGE, **kwargs)
        
        # Last resort: return key path
        return key_path
