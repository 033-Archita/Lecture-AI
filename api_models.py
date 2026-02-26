import os
import time
import streamlit as st
from groq import Groq
import assemblyai as aai
from typing import Optional

def get_api_key(key_name: str) -> str:
    """
    Retrieve API key from Streamlit secrets or environment
    Priority: st.secrets (for deployment) > environment variables (for local)
    """
    # Try Streamlit secrets first (works for both local .streamlit/secrets.toml and Cloud deployment)
    try:
        return st.secrets[key_name]
    except (KeyError, FileNotFoundError, AttributeError):
        pass
    
    # Fallback to environment variable
    key = os.getenv(key_name)
    if key:
        return key
    
    raise ValueError(f"API key '{key_name}' not found in Streamlit secrets or environment variables")

def transcribe_audio(audio_path: str, max_retries: int = 3) -> Optional[str]:
    """
    Transcribe audio file using AssemblyAI with retry logic
    
    Args:
        audio_path: Path to the audio file
        max_retries: Maximum number of retry attempts
        
    Returns:
        Transcribed text or None if failed
    """
    try:
        api_key = get_api_key("ASSEMBLYAI_API_KEY")
        aai.settings.api_key = api_key
        
        config = aai.TranscriptionConfig(
            speech_models=["universal-3-pro"],
            language_code="en",
            punctuate=True,
            format_text=True,
        )
        
        transcriber = aai.Transcriber(config=config)
        
        for attempt in range(max_retries):
            try:
                # Upload and transcribe
                transcript = transcriber.transcribe(audio_path)
                
                # Check status
                if transcript.status == aai.TranscriptStatus.error:
                    error_msg = transcript.error if hasattr(transcript, 'error') else "Unknown error"
                    raise Exception(f"Transcription failed: {error_msg}")
                
                # Return text if successful
                if transcript.text:
                    return transcript.text
                else:
                    raise Exception("Transcription returned empty text")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"Transcription attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Transcription failed after {max_retries} attempts: {str(e)}")
        
        return None
        
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        raise

def generate_notes(transcript: str, max_retries: int = 3) -> Optional[str]:
    """
    Generate structured notes from transcript using Groq
    
    Args:
        transcript: The transcribed text
        max_retries: Maximum number of retry attempts
        
    Returns:
        Generated notes or None if failed
    """
    try:
        api_key = get_api_key("GROQ_API_KEY")
        client = Groq(api_key=api_key)
        
        # Truncate transcript if too long (Groq has token limits)
        max_chars = 30000  # Conservative limit
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "\n\n[Transcript truncated due to length]"
        
        system_prompt = """You are an expert academic note-taker and learning scientist. Your task is to transform lecture transcripts into comprehensive, well-structured study notes.

Create notes that include:

1. **OVERVIEW**: A concise summary of the main topic and key objectives (2-3 sentences)

2. **KEY CONCEPTS**: List and explain core theories, principles, and definitions
   - Use clear, concise language
   - Include relevant examples for each concept
   - Highlight relationships between concepts

3. **DETAILED NOTES**: Organized breakdown of the content
   - Use clear hierarchical structure with headings and subheadings
   - Include all important details, explanations, and elaborations
   - Preserve numerical data, statistics, and specific examples
   - Note any methodologies, processes, or procedures discussed

4. **EXAMPLES & APPLICATIONS**: Real-world applications or examples mentioned
   - Case studies
   - Practical applications
   - Problem-solving examples

5. **KEY TAKEAWAYS**: 5-7 bullet points summarizing the most important information

6. **QUESTIONS FOR REVIEW**: 3-5 thought-provoking questions based on the content

Format the notes using clear markdown with proper headings, bullet points, and emphasis where appropriate. Make the notes scannable and easy to review."""

        user_prompt = f"""Please create comprehensive study notes from the following lecture transcript:

---
{transcript}
---

Generate well-structured, academic-quality notes following the format specified."""

        for attempt in range(max_retries):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3,
                    max_tokens=8000,
                    top_p=0.9,
                )
                
                notes = chat_completion.choices[0].message.content
                
                if notes and len(notes.strip()) > 100:
                    return notes
                else:
                    raise Exception("Generated notes are too short or empty")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"Note generation attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Note generation failed after {max_retries} attempts: {str(e)}")
        
        return None
        
    except Exception as e:
        print(f"Error in note generation: {str(e)}")
        raise

def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """
    Extract key terms and concepts from text
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords
    """
    try:
        api_key = get_api_key("GROQ_API_KEY")
        client = Groq(api_key=api_key)
        
        # Truncate if too long
        if len(text) > 10000:
            text = text[:10000]
        
        prompt = f"""Extract the {max_keywords} most important keywords, terms, or concepts from this text. 
Return only the keywords as a comma-separated list, nothing else.

Text:
{text}"""

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=200,
        )
        
        keywords_str = chat_completion.choices[0].message.content.strip()
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        
        return keywords[:max_keywords]
        
    except Exception as e:
        print(f"Error extracting keywords: {str(e)}")
        return []

def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Create a concise summary of text
    
    Args:
        text: Input text
        max_length: Maximum words in summary
        
    Returns:
        Summary text
    """
    try:
        api_key = get_api_key("GROQ_API_KEY")
        client = Groq(api_key=api_key)
        
        # Truncate if too long
        if len(text) > 15000:
            text = text[:15000]
        
        prompt = f"""Create a concise summary (maximum {max_length} words) of the following text. 
Focus on the main points and key information.

Text:
{text}"""

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500,
        )
        
        summary = chat_completion.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        print(f"Error creating summary: {str(e)}")
        return "Summary generation failed"
