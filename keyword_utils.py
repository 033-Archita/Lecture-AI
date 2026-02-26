import re
from collections import Counter
from typing import List, Set, Dict
import string

# Common English stop words
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
    'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how', 'all',
    'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    'can', 'just', 'should', 'now', 'i', 'you', 'we', 'our', 'your', 'their'
}

def extract_keywords_statistical(text: str, top_n: int = 20) -> List[str]:
    """
    Extract keywords using statistical frequency analysis
    
    Args:
        text: Input text
        top_n: Number of top keywords to return
        
    Returns:
        List of keywords sorted by importance
    """
    # Convert to lowercase and tokenize
    text = text.lower()
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    # Split into words
    words = text.split()
    
    # Filter out stop words and short words
    filtered_words = [
        word for word in words 
        if word not in STOP_WORDS and len(word) > 3
    ]
    
    # Count frequencies
    word_freq = Counter(filtered_words)
    
    # Get top N keywords
    keywords = [word for word, _ in word_freq.most_common(top_n)]
    
    return keywords

def extract_noun_phrases(text: str) -> List[str]:
    """
    Extract potential noun phrases (2-3 word combinations)
    
    Args:
        text: Input text
        
    Returns:
        List of noun phrases
    """
    # Simple pattern: Adjective + Noun or Noun + Noun
    # This is a basic implementation; a full NLP library would be better
    
    text = text.lower()
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    
    phrases = []
    
    for sentence in sentences:
        words = sentence.split()
        
        # Look for 2-3 word phrases
        for i in range(len(words) - 1):
            # 2-word phrase
            phrase = f"{words[i]} {words[i+1]}"
            if is_valid_phrase(phrase):
                phrases.append(phrase)
            
            # 3-word phrase
            if i < len(words) - 2:
                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                if is_valid_phrase(phrase):
                    phrases.append(phrase)
    
    # Count and return most common
    phrase_freq = Counter(phrases)
    return [phrase for phrase, count in phrase_freq.most_common(15) if count > 1]

def is_valid_phrase(phrase: str) -> bool:
    """
    Check if a phrase is a valid keyword phrase
    
    Args:
        phrase: Phrase to validate
        
    Returns:
        True if valid, False otherwise
    """
    words = phrase.split()
    
    # Must have 2-3 words
    if len(words) < 2 or len(words) > 3:
        return False
    
    # No stop words at the start or end
    if words[0] in STOP_WORDS or words[-1] in STOP_WORDS:
        return False
    
    # Must have at least one word longer than 3 characters
    if not any(len(w) > 3 for w in words):
        return False
    
    return True

def identify_technical_terms(text: str) -> List[str]:
    """
    Identify potential technical terms (capitalized words, acronyms, etc.)
    
    Args:
        text: Input text
        
    Returns:
        List of technical terms
    """
    terms = []
    
    # Find all-caps words (acronyms)
    acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
    terms.extend(acronyms)
    
    # Find capitalized words (not at sentence start)
    capitalized = re.findall(r'(?<!^)(?<!\. )\b[A-Z][a-z]+\b', text)
    terms.extend(capitalized)
    
    # Count and return unique terms that appear multiple times
    term_freq = Counter(terms)
    return [term for term, count in term_freq.items() if count > 1]

def extract_numbers_and_stats(text: str) -> Dict[str, List[str]]:
    """
    Extract numbers, percentages, and statistics from text
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with categories of numerical data
    """
    data = {
        'percentages': [],
        'numbers': [],
        'dates': [],
        'measurements': []
    }
    
    # Percentages
    percentages = re.findall(r'\d+\.?\d*\s*%', text)
    data['percentages'] = list(set(percentages))
    
    # Numbers with context
    numbers = re.findall(r'\d+\.?\d*\s+(?:million|billion|thousand|hundred)', text, re.IGNORECASE)
    data['numbers'] = list(set(numbers))
    
    # Years
    years = re.findall(r'\b(19|20)\d{2}\b', text)
    data['dates'] = list(set(years))
    
    # Measurements
    measurements = re.findall(r'\d+\.?\d*\s*(?:kg|g|m|cm|km|ml|l|°C|°F)', text)
    data['measurements'] = list(set(measurements))
    
    return data

def create_keyword_cloud_data(keywords: List[str], text: str) -> Dict[str, int]:
    """
    Create data for a word cloud with keyword frequencies
    
    Args:
        keywords: List of keywords
        text: Original text
        
    Returns:
        Dictionary with keyword: frequency pairs
    """
    text_lower = text.lower()
    
    keyword_freq = {}
    for keyword in keywords:
        count = text_lower.count(keyword.lower())
        if count > 0:
            keyword_freq[keyword] = count
    
    return keyword_freq

def find_related_terms(keyword: str, text: str, window_size: int = 20) -> List[str]:
    """
    Find terms that frequently appear near a keyword
    
    Args:
        keyword: The keyword to analyze
        text: Full text
        window_size: Number of words to look at around the keyword
        
    Returns:
        List of related terms
    """
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    # Find all occurrences
    words = text_lower.split()
    related = []
    
    for i, word in enumerate(words):
        if keyword_lower in word:
            # Get surrounding words
            start = max(0, i - window_size)
            end = min(len(words), i + window_size + 1)
            
            context_words = words[start:i] + words[i+1:end]
            related.extend(context_words)
    
    # Filter and count
    filtered = [w for w in related if w not in STOP_WORDS and len(w) > 3]
    word_freq = Counter(filtered)
    
    return [word for word, _ in word_freq.most_common(10)]

def categorize_keywords(keywords: List[str]) -> Dict[str, List[str]]:
    """
    Categorize keywords into groups (concepts, terms, actions, etc.)
    
    Args:
        keywords: List of keywords
        
    Returns:
        Dictionary with categories and their keywords
    """
    categories = {
        'concepts': [],
        'technical_terms': [],
        'actions': [],
        'general': []
    }
    
    # Simple heuristic-based categorization
    action_suffixes = ['ing', 'tion', 'ment', 'ance', 'ence']
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Check if it's all caps (likely acronym/technical term)
        if keyword.isupper() and len(keyword) > 2:
            categories['technical_terms'].append(keyword)
        # Check if it ends with action-related suffixes
        elif any(keyword_lower.endswith(suffix) for suffix in action_suffixes):
            categories['actions'].append(keyword)
        # Check if it's a multi-word phrase (likely concept)
        elif ' ' in keyword:
            categories['concepts'].append(keyword)
        else:
            categories['general'].append(keyword)
    
    return {k: v for k, v in categories.items() if v}  # Remove empty categories

def highlight_keywords_in_text(text: str, keywords: List[str], max_length: int = 500) -> str:
    """
    Create a snippet of text with keywords highlighted
    
    Args:
        text: Original text
        keywords: Keywords to highlight
        max_length: Maximum length of snippet
        
    Returns:
        Text snippet with highlighted keywords
    """
    # Find first occurrence of any keyword
    text_lower = text.lower()
    first_pos = len(text)
    
    for keyword in keywords:
        pos = text_lower.find(keyword.lower())
        if pos != -1 and pos < first_pos:
            first_pos = pos
    
    # Extract snippet around first keyword
    start = max(0, first_pos - 100)
    end = min(len(text), start + max_length)
    snippet = text[start:end]
    
    # Highlight keywords
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        snippet = pattern.sub(f"**{keyword}**", snippet)
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    
    return snippet
