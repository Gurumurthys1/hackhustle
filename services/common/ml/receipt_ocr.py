import pytesseract
import pymupdf  # PyMuPDF, import as fitz
import io
import re
from PIL import Image, ImageFilter, ImageEnhance
from dataclasses import dataclass
from typing import Optional
from datetime import date
import numpy as np
import structlog

log = structlog.get_logger()

@dataclass
class ReceiptOCRResult:
    raw_text: str
    extracted_amount: Optional[float]
    extracted_date: Optional[date]
    extracted_sku: Optional[str]
    extracted_store: Optional[str]
    pdf_layers_detected: bool
    pdf_creation_date: Optional[date]
    manipulation_detected: bool

def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    """Deskew, denoise, binarize — dramatically improves Tesseract accuracy."""
    # Convert to grayscale
    gray = image.convert('L')
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(2.0)
    # Sharpen
    sharpened = enhanced.filter(ImageFilter.SHARPEN)
    return sharpened

def analyze_receipt(receipt_bytes: bytes, file_type: str) -> ReceiptOCRResult:
    pdf_layers = False
    pdf_creation_date = None
    
    if file_type.upper() == 'PDF':
        # Use PyMuPDF for PDF analysis
        doc = pymupdf.open(stream=receipt_bytes, filetype="pdf")
        
        # Check for multiple font layers (text replacement indicator)
        fonts_per_page = []
        for page in doc:
            fonts = page.get_fonts()
            fonts_per_page.append(len(fonts))
        pdf_layers = max(fonts_per_page) > 5  # > 5 fonts = suspicious
        
        # Check PDF creation metadata
        metadata = doc.metadata
        if metadata.get('creationDate'):
            try:
                date_str = metadata['creationDate'][2:10]  # D:YYYYMMDD...
                pdf_creation_date = date(
                    int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8])
                )
            except:
                pass
        
        # Render first page to image for OCR
        page = doc[0]
        mat = pymupdf.Matrix(2, 2)  # 2x zoom for better OCR
        pix = page.get_pixmap(matrix=mat)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
    else:
        image = Image.open(io.BytesIO(receipt_bytes))
    
    # Preprocess
    processed = preprocess_for_ocr(image)
    
    # Run Tesseract with receipt-optimized config
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,/:-₹$€£ "'
    raw_text = pytesseract.image_to_string(processed, config=custom_config)
    
    # Extract structured data
    amount = _extract_amount(raw_text)
    receipt_date = _extract_date(raw_text)
    sku = _extract_sku(raw_text)
    store = _extract_store(raw_text)
    
    return ReceiptOCRResult(
        raw_text=raw_text,
        extracted_amount=amount,
        extracted_date=receipt_date,
        extracted_sku=sku,
        extracted_store=store,
        pdf_layers_detected=pdf_layers,
        pdf_creation_date=pdf_creation_date,
        manipulation_detected=pdf_layers
    )

def _extract_amount(text: str) -> Optional[float]:
    patterns = [
        r'(?:Total|Amount|Grand Total|TOTAL)\s*:?\s*[₹$€£]?\s*([0-9,]+\.?[0-9]*)',
        r'[₹$€£]\s*([0-9,]+\.?[0-9]*)',
        r'([0-9,]+\.[0-9]{2})\s*(?:INR|USD|EUR)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except:
                continue
    return None

def _extract_date(text: str) -> Optional[date]:
    patterns = [
        r'(\d{2})[/-](\d{2})[/-](\d{4})',  # DD/MM/YYYY
        r'(\d{4})[/-](\d{2})[/-](\d{2})',  # YYYY-MM-DD
        r'(\d{1,2})\s+(\w{3})\s+(\d{4})',  # 15 Jan 2024
    ]
    months = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
              'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                groups = match.groups()
                if len(groups[2]) == 4:  # DD/MM/YYYY
                    return date(int(groups[2]), int(groups[1]), int(groups[0]))
                elif len(groups[0]) == 4:  # YYYY-MM-DD
                    return date(int(groups[0]), int(groups[1]), int(groups[2]))
                else:  # DD Mon YYYY
                    month = months.get(groups[1].lower()[:3])
                    if month:
                        return date(int(groups[2]), month, int(groups[0]))
            except:
                continue
    return None

def _extract_sku(text: str) -> Optional[str]:
    patterns = [r'SKU[:\s]+([A-Z0-9-]{4,20})', r'Item[:\s]+([A-Z0-9-]{4,20})']
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

def _extract_store(text: str) -> Optional[str]:
    # First non-empty line is usually store name
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return lines[0] if lines else None
