# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.auth import default
from google.api_core.exceptions import ResourceExhausted
import vertexai
from vertexai.preview import rag
import os
from dotenv import load_dotenv, set_key
import requests
import tempfile

# Load environment variables from .env file
load_dotenv()

# --- Please fill in your configurations ---
# Retrieve the PROJECT_ID from the environmental variables.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )
CORPUS_DISPLAY_NAME = "Research_Documents_Corpus"
CORPUS_DESCRIPTION = "Corpus containing research documents"
# Using GCS bucket URL for production-ready document access
PDF_URL = "https://storage.googleapis.com/rag-agent-testing-aiml-demo/1-s2.0-S0160791X2500003X-main.pdf"
PDF_FILENAME = "research_paper.pdf"
# Point to the RAG agent's specific .env file, not the shared apps/.env
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))


# --- Start of the script ---
def initialize_vertex_ai():
  credentials, _ = default()
  vertexai.init(
      project=PROJECT_ID, location=LOCATION, credentials=credentials
  )


def create_or_get_corpus():
  """Creates a new corpus or retrieves an existing one."""
  embedding_model_config = rag.EmbeddingModelConfig(
      publisher_model="publishers/google/models/text-embedding-004"
  )
  existing_corpora = rag.list_corpora()
  corpus = None
  for existing_corpus in existing_corpora:
    if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
      corpus = existing_corpus
      print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
      break
  if corpus is None:
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=CORPUS_DESCRIPTION,
        embedding_model_config=embedding_model_config,
    )
    print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
  return corpus


def download_pdf_from_url(url, output_path):
  """Downloads a PDF file from GCS using authenticated access."""
  print(f"Downloading PDF from {url}...")
  
  # Check if it's a GCS URL
  if url.startswith("https://storage.googleapis.com/"):
    # Extract bucket and blob name from URL
    # Format: https://storage.googleapis.com/BUCKET_NAME/BLOB_NAME
    parts = url.replace("https://storage.googleapis.com/", "").split("/", 1)
    if len(parts) == 2:
      bucket_name = parts[0]
      blob_name = parts[1]
      
      try:
        from google.cloud import storage
        from google.auth import default
        
        print(f"Using authenticated GCS access for bucket: {bucket_name}")
        credentials, _ = default()
        storage_client = storage.Client(credentials=credentials, project=PROJECT_ID)
        
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.download_to_filename(output_path)
        print(f"PDF downloaded successfully to {output_path}")
        return output_path
      except Exception as e:
        print(f"GCS download failed: {e}")
        print("Falling back to HTTP download...")
        # Fall through to HTTP download
  
  # Fallback to HTTP download with headers
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
  }
  
  try:
    response = requests.get(url, headers=headers, stream=True, timeout=60, allow_redirects=True)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    with open(output_path, 'wb') as f:
      for chunk in response.iter_content(chunk_size=8192):
        if chunk:  # filter out keep-alive new chunks
          f.write(chunk)
    
    print(f"PDF downloaded successfully to {output_path}")
    return output_path
  except requests.exceptions.HTTPError as e:
    print(f"HTTP Error {e.response.status_code}: Failed to download PDF")
    print(f"The URL {url} may be blocking automated downloads.")
    print(f"You can manually download the PDF and place it in the data/ folder, then use upload_documents.py instead.")
    raise
  except Exception as e:
    print(f"Error downloading PDF: {e}")
    raise



def upload_pdf_to_corpus(corpus_name, pdf_path, display_name, description):
  """Uploads a PDF file to the specified corpus."""
  print(f"Uploading {display_name} to corpus...")
  try:
    rag_file = rag.upload_file(
        corpus_name=corpus_name,
        path=pdf_path,
        display_name=display_name,
        description=description,
    )
    print(f"Successfully uploaded {display_name} to corpus")
    return rag_file
  except ResourceExhausted as e:
    print(f"Error uploading file {display_name}: {e}")
    print("\nThis error suggests that you have exceeded the API quota for the embedding model.")
    print("This is common for new Google Cloud projects.")
    print("Please see the 'Troubleshooting' section in the README.md for instructions on how to request a quota increase.")
    return None
  except Exception as e:
    print(f"Error uploading file {display_name}: {e}")
    return None

def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")

def list_corpus_files(corpus_name):
  """Lists files in the specified corpus."""
  files = list(rag.list_files(corpus_name=corpus_name))
  print(f"Total files in corpus: {len(files)}")
  for file in files:
    print(f"File: {file.display_name} - {file.name}")


def main():
  initialize_vertex_ai()
  corpus = create_or_get_corpus()

  # Update the .env file with the corpus name
  update_env_file(corpus.name, ENV_FILE_PATH)
  
  # Create a temporary directory to store the downloaded PDF
  with tempfile.TemporaryDirectory() as temp_dir:
    pdf_path = os.path.join(temp_dir, PDF_FILENAME)
    
    # Download the PDF from the URL
    download_pdf_from_url(PDF_URL, pdf_path)
    
    # Upload the PDF to the corpus
    upload_pdf_to_corpus(
        corpus_name=corpus.name,
        pdf_path=pdf_path,
        display_name=PDF_FILENAME,
        description="Alphabet's 10-K 2024 document"
    )
  
  # List all files in the corpus
  list_corpus_files(corpus_name=corpus.name)

if __name__ == "__main__":
  main()
