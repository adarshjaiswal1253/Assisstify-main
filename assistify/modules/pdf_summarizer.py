"""
PDF processing and AI summarization functionality.
"""

from PyPDF2 import PdfReader
from transformers import pipeline
from config.settings import PDF_CHUNK_SIZE, PDF_MAX_LENGTH, PDF_MIN_LENGTH, PDF_MAX_CHUNKS, PDF_SUMMARIZER_MODEL


class PDFProcessor:
    """Handles PDF text extraction."""
    
    @staticmethod
    def extract_text(pdf_path):
        """
        Extract text from PDF file.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            str: Extracted text or empty string
        """
        try:
            reader = PdfReader(pdf_path)
            full_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            return full_text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""


class AISummarizer:
    """Handles AI-powered PDF summarization."""
    
    def __init__(self):
        self.model = None
    
    def _get_model(self):
        """Lazy load the summarization model."""
        if self.model is None:
            self.model = pipeline("summarization", model=PDF_SUMMARIZER_MODEL)
        return self.model
    
    def summarize(self, text, chunk_size=PDF_CHUNK_SIZE, max_length=PDF_MAX_LENGTH, min_length=PDF_MIN_LENGTH):
        """
        Summarize text using AI model.
        
        Args:
            text (str): Text to summarize
            chunk_size (int): Size of text chunks
            max_length (int): Maximum summary length
            min_length (int): Minimum summary length
            
        Returns:
            str: Summarized text
        """
        if not text.strip():
            return "❌ Could not extract text from the PDF."
        
        # Split into chunks
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        summarizer = self._get_model()
        summary = ""
        
        for idx, chunk in enumerate(chunks):
            if idx >= PDF_MAX_CHUNKS:
                summary += "(Summary truncated... PDF is very long)\n"
                break
            
            chunk = " ".join(chunk.split())
            if len(chunk) < 60:
                continue
            
            try:
                out = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                sub_summary = out[0]['summary_text']
                summary += f"Part {idx+1}:\n{sub_summary}\n\n"
            except Exception as e:
                print(f"Summarization error for chunk {idx}: {e}")
                continue
        
        return summary.strip()


class PDFSummarizer:
    """Unified PDF summarizer combining extraction and AI summarization."""
    
    def __init__(self):
        self.processor = PDFProcessor()
        self.ai_summarizer = AISummarizer()
    
    def summarize_file(self, pdf_path):
        """
        Summarize a PDF file.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            str: Summarized content
        """
        text = self.processor.extract_text(pdf_path)
        return self.ai_summarizer.summarize(text)
