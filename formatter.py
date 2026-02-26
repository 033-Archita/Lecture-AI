import re
from typing import List, Dict

def format_notes(notes: str) -> str:
    """
    Format notes with improved markdown styling
    
    Args:
        notes: Raw notes text
        
    Returns:
        Formatted notes in markdown
    """
    # Ensure proper spacing around headers
    notes = re.sub(r'\n(#{1,6})\s*', r'\n\n\1 ', notes)
    
    # Ensure blank line before lists
    notes = re.sub(r'\n([*-])\s', r'\n\n\1 ', notes)
    
    # Clean up multiple consecutive blank lines
    notes = re.sub(r'\n{3,}', r'\n\n', notes)
    
    return notes.strip()

def extract_sections(notes: str) -> Dict[str, str]:
    """
    Extract different sections from structured notes
    
    Args:
        notes: Formatted notes
        
    Returns:
        Dictionary with section names as keys and content as values
    """
    sections = {}
    current_section = "Introduction"
    current_content = []
    
    lines = notes.split('\n')
    
    for line in lines:
        # Check if line is a header
        if line.strip().startswith('#'):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = line.strip().lstrip('#').strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

def create_table_of_contents(notes: str) -> str:
    """
    Generate a table of contents from headers in notes
    
    Args:
        notes: Formatted notes
        
    Returns:
        Markdown table of contents
    """
    toc = ["## Table of Contents\n"]
    
    lines = notes.split('\n')
    for line in lines:
        if line.strip().startswith('#'):
            # Count header level
            level = len(re.match(r'^#+', line.strip()).group())
            
            # Extract header text
            header_text = line.strip().lstrip('#').strip()
            
            # Create anchor link
            anchor = header_text.lower().replace(' ', '-').replace('[^a-z0-9-]', '')
            
            # Add to TOC with proper indentation
            indent = '  ' * (level - 1)
            toc.append(f"{indent}- [{header_text}](#{anchor})")
    
    return '\n'.join(toc) + '\n\n'

def highlight_keywords(text: str, keywords: List[str]) -> str:
    """
    Highlight keywords in text using markdown bold
    
    Args:
        text: Input text
        keywords: List of keywords to highlight
        
    Returns:
        Text with highlighted keywords
    """
    for keyword in keywords:
        # Use word boundaries to match whole words
        pattern = r'\b' + re.escape(keyword) + r'\b'
        text = re.sub(pattern, f"**{keyword}**", text, flags=re.IGNORECASE)
    
    return text

def create_summary_box(summary: str) -> str:
    """
    Create a styled summary box in markdown
    
    Args:
        summary: Summary text
        
    Returns:
        Formatted summary box
    """
    box = f"""
> **📌 Summary**
> 
> {summary}

"""
    return box

def format_bullet_list(items: List[str], ordered: bool = False) -> str:
    """
    Format a list of items as markdown bullets
    
    Args:
        items: List of items
        ordered: Whether to use ordered list (1. 2. 3.) or unordered (-)
        
    Returns:
        Formatted markdown list
    """
    if ordered:
        return '\n'.join([f"{i+1}. {item}" for i, item in enumerate(items)])
    else:
        return '\n'.join([f"- {item}" for item in items])

def add_page_breaks(notes: str, every_n_sections: int = 3) -> str:
    """
    Add page break markers for printing
    
    Args:
        notes: Formatted notes
        every_n_sections: Add break after every N sections
        
    Returns:
        Notes with page break markers
    """
    lines = notes.split('\n')
    result = []
    section_count = 0
    
    for line in lines:
        result.append(line)
        
        if line.strip().startswith('#'):
            section_count += 1
            if section_count % every_n_sections == 0:
                result.append('\n<div style="page-break-after: always;"></div>\n')
    
    return '\n'.join(result)

def create_flashcards(notes: str) -> List[Dict[str, str]]:
    """
    Extract potential flashcard Q&A pairs from notes
    
    Args:
        notes: Formatted notes
        
    Returns:
        List of dictionaries with 'question' and 'answer' keys
    """
    flashcards = []
    
    # Look for definition patterns
    definition_pattern = r'\*\*([^*]+)\*\*:\s*(.+?)(?=\n|$)'
    matches = re.finditer(definition_pattern, notes)
    
    for match in matches:
        term = match.group(1).strip()
        definition = match.group(2).strip()
        
        flashcards.append({
            'question': f"What is {term}?",
            'answer': definition
        })
    
    return flashcards

def export_to_anki_format(flashcards: List[Dict[str, str]]) -> str:
    """
    Export flashcards to Anki-compatible CSV format
    
    Args:
        flashcards: List of flashcard dictionaries
        
    Returns:
        CSV-formatted string
    """
    csv_lines = ["Question,Answer"]
    
    for card in flashcards:
        question = card['question'].replace('"', '""')
        answer = card['answer'].replace('"', '""')
        csv_lines.append(f'"{question}","{answer}"')
    
    return '\n'.join(csv_lines)

def clean_transcript(transcript: str) -> str:
    """
    Clean up transcript text
    
    Args:
        transcript: Raw transcript
        
    Returns:
        Cleaned transcript
    """
    # Remove excessive whitespace
    transcript = re.sub(r'\s+', ' ', transcript)
    
    # Fix common transcription errors
    transcript = transcript.replace(' um ', ' ')
    transcript = transcript.replace(' uh ', ' ')
    transcript = transcript.replace(' like ', ' ')
    
    # Add proper spacing after punctuation
    transcript = re.sub(r'([.!?])([A-Z])', r'\1 \2', transcript)
    
    return transcript.strip()
