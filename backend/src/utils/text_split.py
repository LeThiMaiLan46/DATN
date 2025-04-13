import re
from typing import List, Optional
from enum import Enum


def split_by_char_limit_multilingual(text: str, lang: str = 'en', limit: int = 200) -> List[str]:
    # Language-specific sentence patterns
    patterns = {
        'en': r'(?<=[.!?])\s+',
        'ja': r'(?<=[。！？])',
        'ko': r'(?<=[.!?。！？])',
        'vi': r'(?<=[.!?])\s+'
    }
    
    # Language-specific word splitting patterns
    word_split_patterns = {
        'en': r'\s+',
        'ja': r'(?<=[\p{Han}\p{Hiragana}\p{Katakana}])',
        'ko': r'(?<=[\p{Hangul}])|(?<=\s)',
        'vi': r'\s+'
    }
    
    # Validate language
    if lang not in patterns:
        raise ValueError(f"Unsupported language: {lang}. Supported languages are: {', '.join(patterns.keys())}")

    chunks = []
    current_chunk = ""
    
    # Split by sentences using language-specific pattern
    sentences = [s.strip() for s in re.split(patterns[lang], text) if s.strip()]
    
    for sentence in sentences:
        # If adding the sentence doesn't exceed limit
        if len(current_chunk) + len(sentence) + (1 if current_chunk else 0) <= limit:
            current_chunk += (" " if current_chunk and lang in ['en', 'vi'] else "") + sentence
        else:
            # Save current chunk if it exists
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If single sentence is longer than limit, split by words/characters
            if len(sentence) > limit:
                # Split using language-specific word pattern
                if lang in ['ja', 'ko']:
                    words = [w for w in re.finditer(word_split_patterns[lang], sentence)]
                    current_pos = 0
                    current_chunk = ""
                    
                    for match in words:
                        word = sentence[current_pos:match.end()]
                        current_pos = match.end()
                        
                        if len(current_chunk) + len(word) <= limit:
                            current_chunk += word
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = word
                            
                    # Add remaining text
                    if current_pos < len(sentence):
                        remaining = sentence[current_pos:]
                        if len(current_chunk) + len(remaining) <= limit:
                            current_chunk += remaining
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = remaining
                else:
                    # For English and Vietnamese, split by words
                    words = sentence.split()
                    current_chunk = ""
                    for word in words:
                        if len(current_chunk) + len(word) + 1 <= limit:
                            current_chunk += (" " if current_chunk else "") + word
                        else:
                            chunks.append(current_chunk.strip())
                            current_chunk = word
            else:
                current_chunk = sentence
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

