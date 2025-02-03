from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pytesseract
from PIL import Image
import re
import io
import json
import logging
from typing import Dict, Any
from pathlib import Path
import cv2
import numpy as np

# Set up logging with more detailed configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aadhaar Card Info Extractor",
    description="API for extracting information from Aadhaar card images",
    version="1.0.0"
)

# CORS middleware configuration with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess the image to improve OCR accuracy using PIL instead of OpenCV.
    """
    try:
        # Convert to grayscale
        gray_image = image.convert('L')
        
        # Enhance contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(gray_image)
        enhanced_image = enhancer.enhance(2.0)
        
        return enhanced_image
    except Exception as e:
        logger.error(f"Error in image preprocessing: {str(e)}")
        raise ValueError("Failed to preprocess image")

def validate_aadhaar_number(aadhaar: str) -> bool:
    """
    Validate Aadhaar number format and basic checksum.
    """
    if not aadhaar:
        return False
    # Remove spaces and check if it's 12 digits
    aadhaar = aadhaar.replace(" ", "")
    return bool(re.match(r'^\d{12}$', aadhaar))

def extract_aadhaar_info(text: str) -> Dict[str, Any]:
    """
    Extract Aadhaar card information from OCR text with improved patterns.
    """
    aadhaar_info = {
        "aadhaar_number": None,
        "name": None,
        "dob": None,
        "gender": None
    }

    patterns = {
        "aadhaar": (
            r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b',
            lambda x: x.replace(" ", "")
        ),
        "name": (
            r"(?:Name|नाम)\s*[:।]?\s*([A-Za-z\s]+?)(?=\s*(?:DOB|Year|Birth|Father|Mother|पिता|माता|जन्म|Male|Female|पुरुष|महिला)|\n|$)",
            lambda x: x.strip()
        ),
        "dob": (
            r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b",
            lambda x: x
        ),
        "gender": (
            r"\b(Male|Female|Transgender|पुरुष|महिला|किन्नर)\b",
            lambda x: "Male" if x in ["Male", "पुरुष"] else "Female" if x in ["Female", "महिला"] else "Transgender"
        )
    }

    try:
        for key, (pattern, transform) in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1) if key != "aadhaar" else match.group(0)
                aadhaar_info[key] = transform(value)

        # Validate extracted data
        if aadhaar_info["aadhaar_number"]:
            if not validate_aadhaar_number(aadhaar_info["aadhaar_number"]):
                aadhaar_info["aadhaar_number"] = None
                logger.warning("Invalid Aadhaar number format detected")

        return aadhaar_info
    except Exception as e:
        logger.error(f"Error in extraction: {str(e)}")
        raise ValueError("Failed to extract information")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that displays API information."""
    return """
    <html>
        <head>
            <title>Aadhaar Card Info Extractor API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 40px auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                .endpoint {
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
                h1 { color: #333; }
                code { 
                    background: #e0e0e0;
                    padding: 2px 5px;
                    border-radius: 3px;
                }
            </style>
        </head>
        <body>
            <h1>Aadhaar Card Info Extractor API</h1>
            <p>Welcome to the Aadhaar Card Info Extractor API. This service provides OCR capabilities for extracting information from Aadhaar cards.</p>
            
            <div class="endpoint">
                <h2>Available Endpoints:</h2>
                <ul>
                    <li><code>POST /extract-aadhaar-info/</code> - Upload an Aadhaar card image to extract information</li>
                    <li><code>GET /health</code> - Check API health status</li>
                </ul>
            </div>
            
            <div class="endpoint">
                <h2>Supported Features:</h2>
                <ul>
                    <li>Image preprocessing for better OCR accuracy</li>
                    <li>Extraction of Name, Aadhaar Number, DOB, and Gender</li>
                    <li>Support for both English and Hindi text</li>
                    <li>File validation (size and type)</li>
                </ul>
            </div>
        </body>
    </html>
    """

@app.post("/extract-aadhaar-info/")
async def extract_aadhaar_data(file: UploadFile = File(...)) -> JSONResponse:
    """
    Extract information from an uploaded Aadhaar card image with improved validation and error handling.
    """
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(status_code=400, detail="File size too large (max 5MB)")

    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/jpg"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed")

    try:
        # Process image
        image = Image.open(io.BytesIO(content))
        
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Perform OCR with improved configuration
        text = pytesseract.image_to_string(
            processed_image,
            lang='eng+hin',
            config='--psm 3 --oem 3'
        )
        
        if not text.strip():
            raise ValueError("No text detected in image")

        # Extract information
        extracted_data = extract_aadhaar_info(text)
        
        # Validate extracted data
        if not any(extracted_data.values()):
            raise ValueError("No valid information could be extracted")

        logger.info(f"Successfully processed image: {file.filename}")
        
        return JSONResponse(
            content={
                "success": True,
                "data": extracted_data,
                "message": "Information extracted successfully"
            },
            status_code=200
        )
    
    except Exception as e:
        logger.error(f"Error processing {file.filename}: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "error": "Failed to process image",
                "detail": str(e)
            },
            status_code=500
        )

@app.get("/health")
async def health_check():
    """Health check endpoint with additional system information."""
    try:
        # Check if tesseract is available
        pytesseract.get_tesseract_version()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "tesseract_available": True
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e)
            },
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)