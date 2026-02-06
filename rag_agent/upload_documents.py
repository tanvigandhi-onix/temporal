"""
Simple script to upload documents to your RAG corpus.
Place your PDF/TXT files in the 'data/' folder and run this script.
"""

import os
from dotenv import load_dotenv
import vertexai
from vertexai.preview import rag
from google.auth import default

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
CORPUS_NAME = os.getenv("RAG_CORPUS")

# Initialize Vertex AI
credentials, _ = default()
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

# Directory containing documents to upload
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def upload_documents():
    """Upload all PDF and TXT files from the data/ directory."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created {DATA_DIR} directory. Please add your documents there.")
        return
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.pdf', '.txt'))]
    
    if not files:
        print(f"No PDF or TXT files found in {DATA_DIR}")
        print("Please add some documents and run this script again.")
        return
    
    print(f"Found {len(files)} files to upload...")
    
    for filename in files:
        file_path = os.path.join(DATA_DIR, filename)
        print(f"\nUploading {filename}...")
        
        try:
            rag_file = rag.upload_file(
                corpus_name=CORPUS_NAME,
                path=file_path,
                display_name=filename,
                description=f"Uploaded from {filename}"
            )
            print(f"✅ Successfully uploaded {filename}")
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
    
    # List all files in corpus
    print("\n" + "="*50)
    print("Files in corpus:")
    print("="*50)
    files = list(rag.list_files(corpus_name=CORPUS_NAME))
    for i, file in enumerate(files, 1):
        print(f"{i}. {file.display_name}")
    print(f"\nTotal: {len(files)} files")

if __name__ == "__main__":
    upload_documents()
