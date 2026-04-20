import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import process_document

docs_folder = "documents"

pdf_files = [f for f in os.listdir(docs_folder) if f.endswith('.pdf')]

if not pdf_files:
    print("No PDFs found in documents folder")
    sys.exit(1)

print(f"Found {len(pdf_files)} PDFs to ingest:")
for pdf in pdf_files:
    print(f"  - {pdf}")

print("\nIngesting...")
total_chunks = 0
for pdf in pdf_files:
    path = os.path.join(docs_folder, pdf)
    chunks = process_document(path)
    total_chunks += chunks
    print(f"  ✅ {pdf} — {chunks} chunks")

print(f"\nDone. Total chunks ingested: {total_chunks}")