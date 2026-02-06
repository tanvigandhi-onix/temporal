"""
Upload real documents to RAG corpus from URLs.
"""

import os
from dotenv import load_dotenv
import vertexai
from vertexai.preview import rag
from google.auth import default
import requests
import tempfile

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
CORPUS_NAME = os.getenv("RAG_CORPUS")

# Initialize Vertex AI
credentials, _ = default()
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

# Real document URLs to upload
DOCUMENT_URLS = [
    {
        "url": "https://storage.googleapis.com/rag-agent-testing-aiml-demo/1-s2.0-S0160791X2500003X-main.pdf",
        "display_name": "research_paper.pdf",
        "description": "Research paper from GCS bucket"
    },
]

def download_from_url(url, output_path):
    """Download a file from URL."""
    print(f"Downloading from {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ Downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def upload_to_corpus(file_path, display_name, description):
    """Upload a file to the RAG corpus."""
    print(f"Uploading {display_name} to corpus...")
    
    try:
        rag_file = rag.upload_file(
            corpus_name=CORPUS_NAME,
            path=file_path,
            display_name=display_name,
            description=description
        )
        print(f"✅ Successfully uploaded {display_name}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def main():
    print(f"Corpus: {CORPUS_NAME}")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for doc in DOCUMENT_URLS:
            url = doc["url"]
            display_name = doc["display_name"]
            description = doc.get("description", "")
            
            print(f"\n📄 Processing: {display_name}")
            
            temp_file = os.path.join(temp_dir, display_name)
            
            if download_from_url(url, temp_file):
                if upload_to_corpus(temp_file, display_name, description):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1
    
    # List all files in corpus
    print("\n" + "="*60)
    print("📚 Files currently in corpus:")
    print("="*60)
    try:
        files = list(rag.list_files(corpus_name=CORPUS_NAME))
        for i, file in enumerate(files, 1):
            print(f"{i}. {file.display_name}")
        print(f"\nTotal: {len(files)} files")
    except Exception as e:
        print(f"Error listing files: {e}")
    
    print("\n" + "="*60)
    print(f"✅ Successful uploads: {success_count}")
    print(f"❌ Failed uploads: {fail_count}")
    print("="*60)

if __name__ == "__main__":
    main()
