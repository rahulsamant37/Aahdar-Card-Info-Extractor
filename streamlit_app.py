import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
from PIL import Image
import io
import json

# Configuration
FASTAPI_URL = "http://localhost:8000/extract-aadhaar-info/"
CSV_FILE = "aadhaar_data.csv"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Page configuration
st.set_page_config(
    page_title="Aadhaar Card Info Extractor",
    page_icon="🆔",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        background-color: #FF4B4B;
        color: white;
        border-radius: 0.5rem;
    }
    .upload-box {
        border: 2px dashed #ccc;
        padding: 2rem;
        text-align: center;
        border-radius: 0.5rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #D4EDDA;
        color: #155724;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #F8D7DA;
        color: #721C24;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def validate_file(uploaded_file):
    """Validate the uploaded file."""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size
    file_size = len(uploaded_file.getvalue())
    if file_size > MAX_FILE_SIZE:
        return False, f"File size exceeds 5MB limit. Current size: {file_size/1024/1024:.2f}MB"
    
    # Check file type
    if uploaded_file.type not in ["image/jpeg", "image/png", "image/jpg"]:
        return False, "Invalid file type. Please upload a JPEG or PNG image"
    
    return True, ""

def save_to_csv(data):
    """Save extracted data to CSV with error handling."""
    try:
        df = pd.DataFrame([data])
        if os.path.exists(CSV_FILE):
            df.to_csv(CSV_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def display_extraction_results(data):
    """Display extracted information in a formatted way."""
    st.markdown("### Extracted Information")
    
    # Create a container for better organization
    with st.container():
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Aadhaar Number:**")
            st.write(data.get("aadhaar_number", "Not found"))
            
            st.markdown("**Name:**")
            st.write(data.get("name", "Not found"))
        
        with col2:
            st.markdown("**Date of Birth:**")
            st.write(data.get("dob", "Not found"))
            
            st.markdown("**Gender:**")
            st.write(data.get("gender", "Not found"))

def main():
    # Create a container for the main content
    with st.container():
        st.title("Aadhaar Card Info Extractor")
        st.markdown("Upload an Aadhaar card image to extract information")
        
        # File uploader with custom styling
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=["png", "jpg", "jpeg"],
            help="Upload a clear image of the Aadhaar card"
        )
        
        if uploaded_file is not None:
            # Validate file
            is_valid, error_message = validate_file(uploaded_file)
            if not is_valid:
                st.error(error_message)
                return
            
            # Display uploaded image
            st.image(
                uploaded_file, 
                caption="Uploaded Image", 
                use_container_width=True  # Updated from use_column_width
            )
            
            # Process button
            if st.button("Extract Information", key="extract_button"):
                with st.spinner("Processing image..."):
                    try:
                        # Prepare file for upload
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        # Make API request
                        response = requests.post(FASTAPI_URL, files=files)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data["success"]:
                                st.success("Information extracted successfully!")
                                
                                # Display results
                                display_extraction_results(data["data"])
                                
                                # Save to CSV
                                if save_to_csv(data["data"]):
                                    st.info("Data saved successfully to CSV")
                            else:
                                st.error(f"Error: {data.get('error', 'Unknown error')}")
                        else:
                            st.error(f"Error: {response.status_code}")
                            st.error(response.text)
                    
                    except requests.exceptions.ConnectionError:
                        st.error("Failed to connect to the server. Please make sure the FastAPI server is running.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()