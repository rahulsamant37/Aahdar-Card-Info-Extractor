# Aadhaar Card Info Extractor

A powerful OCR solution for automatically extracting information from Aadhaar cards, with a FastAPI backend and Streamlit frontend. This application allows users to upload Aadhaar card images and extract key details such as Aadhaar number, name, date of birth, and gender.

![Aadhaar Card Extractor](https://github.com/user-attachments/assets/1348d05d-7da5-4c58-be77-e6e3601100ac)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Backend (FastAPI)](#backend-fastapi)
- [Frontend (Streamlit)](#frontend-streamlit)
- [Installation](#installation)
- [Usage](#usage)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)
- [Data Privacy & Security](#data-privacy--security)
- [License](#license)

## Overview

The Aadhaar Card Info Extractor automates the extraction of personal information from Aadhaar cards using Tesseract OCR technology. The application consists of just two main files:

- `fastapiapp.py`: FastAPI backend that handles image processing and OCR
- `streamlit_app.py`: Streamlit frontend that provides a user-friendly interface

## Features

### Core Capabilities

- **Smart OCR Processing**: Optimized text extraction for Aadhaar cards
- **Comprehensive Data Extraction**:
  - Aadhaar number (with format validation)
  - Full name
  - Date of birth
  - Gender
- **Multilingual Support**: Works with both English and Hindi Aadhaar cards
- **Data Export**: Save extracted information as CSV for future reference

### Technical Features

- **Image Preprocessing**:
  - Grayscale conversion
  - Contrast enhancement
  - Noise reduction
  - Automatic image orientation detection
- **Robust Error Handling**: Clear error messages for troubleshooting
- **Input Validation**: Ensures data integrity and proper formatting
- **Health Monitoring**: Endpoint to verify system status
- **Logging**: Comprehensive activity logging for debugging

## Backend (FastAPI)

The FastAPI backend (`fastapi_app.py`) provides the core functionality for processing Aadhaar card images and extracting information using OCR.

### Endpoints

#### POST `/extract-aadhaar-info/`

Processes an Aadhaar card image and returns structured data.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (Image file - JPEG, PNG)

**Response:**
```json
{
  "success": true,
  "data": {
    "aadhaar_number": "1234 5678 9012",
    "name": "John Doe",
    "dob": "01/01/1990",
    "gender": "Male"
  },
  "message": "Information extracted successfully"
}
```

![image](https://github.com/user-attachments/assets/4b7106a9-9299-4cdf-9396-2ae77d2ca291)


#### GET `/health`

Checks if the backend and Tesseract OCR are functioning correctly.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-03-16T12:00:00",
  "tesseract_available": true
}
```

### Dependencies

```
fastapi==0.95.0
uvicorn==0.21.1
pytesseract==0.3.10
Pillow==9.5.0
opencv-python==4.7.0.72
numpy==1.24.2
pandas==2.0.0
requests==2.28.2
python-multipart==0.0.6
```

### Running the Backend

```bash
# Start the FastAPI server
uvicorn fastapi_app:app --reload
```

## Frontend (Streamlit)

The Streamlit frontend (`streamlit_app.py`) provides an intuitive user interface for uploading images and viewing extraction results.

### UI Components

- **Upload Area**: Easy drag-and-drop interface for image uploading
- **Image Preview**: View the uploaded Aadhaar card image
- **Extraction Results**: Clearly formatted display of extracted information
- **Export Options**: Download extracted data as CSV

### Dependencies

```
streamlit==1.22.0
requests==2.28.2
pandas==2.0.0
Pillow==9.5.0
```

### Running the Frontend

```bash
# Start the Streamlit app
streamlit run streamlit_app.py
```

## Installation

### Prerequisites

- **Python**: 3.7 or higher
- **Tesseract OCR**: Version 4.0+ required
  - [Windows Installation](https://github.com/UB-Mannheim/tesseract/wiki)
  - [macOS Installation](https://brew.sh/): `brew install tesseract`
  - [Linux Installation](https://github.com/tesseract-ocr/tesseract): `sudo apt install tesseract-ocr`

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rahulsamant37/Aahdar-Card-Info-Extractor.git
   cd aadhaar-extractor
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Tesseract installation**
   ```bash
   # Check if Tesseract is properly installed
   tesseract --version
   ```

5. **Configure Tesseract path (if needed)**
   
   Edit `fastapi_app.py` to set the correct path for your Tesseract installation:
   ```python
   # Example for Windows
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   
   # Example for macOS/Linux
   # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
   ```

## Usage

### Basic Usage

1. **Start the backend server**
   ```bash
   uvicorn fastapi_app:app --reload
   ```

2. **Start the frontend application**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the application**
   - Open your browser and go to `http://localhost:8501`

4. **Extract information from an Aadhaar card**
   - Upload an Aadhaar card image using the upload button
   - Click "Extract Information" to process the image
   - View the extracted details in the results section
   - Download the data as CSV using the "Save to CSV" button

### Advanced Options

- **Image Quality**: Toggle the "Enhance Image" option for better results with low-quality images
- **Language**: Select the appropriate language model for your Aadhaar card (English/Hindi)
- **Batch Processing**: Upload multiple files to process them in sequence
- **View History**: Access previously extracted information from the CSV log

## Performance Tips

For optimal OCR performance:

- **Image Quality**: Use clear, well-lit images without glare or shadows
- **Resolution**: Aim for at least 300 DPI for best results
- **Format**: PNG format often provides better results than JPEG
- **Orientation**: Ensure the card is properly aligned in the image
- **Cropping**: If possible, crop the image to show only the Aadhaar card
- **Contrast**: Higher contrast between text and background improves extraction accuracy

## Troubleshooting

### Common Issues

1. **Tesseract Not Found**
   - Verify Tesseract is installed and in your system PATH
   - Check the Tesseract path in `fastapi_app.py`

2. **Poor Extraction Quality**
   - Try enabling image enhancement
   - Improve image quality and lighting
   - Ensure the card is clearly visible and properly aligned

3. **Backend Connection Error**
   - Verify the FastAPI server is running
   - Check the backend URL in the frontend code

4. **Missing or Incorrect Data**
   - Different Aadhaar card formats may require adjustments to the extraction logic
   - Try using a higher resolution image

### Quick Fixes

- **Restart the Services**: Sometimes simply restarting both the backend and frontend resolves issues
- **Clear Cache**: Clear your browser cache or restart the Streamlit app
- **Update Dependencies**: Ensure you're using the latest versions of all dependencies

## Data Privacy & Security

- **Local Processing**: All OCR operations occur locally on your machine
- **No Data Storage**: By default, images are processed in memory and not saved
- **Data Masking**: Option to partially mask the Aadhaar number in the results
- **Secure Export**: Ensure extracted data is stored securely

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

© 2025 Aadhaar Card Info Extractor | [GitHub Repository](https://github.com/rahulsamant37/Aahdar-Card-Info-Extractor)
