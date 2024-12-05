import os
from flask import Flask, request, send_file, jsonify
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image

app = Flask(__name__)

# Define file storage paths
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ZIP_FOLDER = 'zips'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_files():
    # Retrieve files from request
    pdf_files = request.files.getlist('pdfFiles')
    signature_file = request.files.get('signatureFile')

    if not pdf_files or not signature_file:
        return jsonify({'error': 'Please upload both PDF files and a signature image.'}), 400

    # Save signature image
    signature_path = os.path.join(UPLOAD_FOLDER, 'signature.png')
    signature_file.save(signature_path)

    # Process each PDF file
    modified_files = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        pdf_file.save(pdf_path)

        # Modify PDF (Add Signature)
        modified_pdf_path = os.path.join(OUTPUT_FOLDER, f"modified_{pdf_file.filename}")
        add_signature_to_pdf(pdf_path, signature_path, modified_pdf_path)
        modified_files.append(modified_pdf_path)

    # Create ZIP file
    zip_file_path = os.path.join(ZIP_FOLDER, 'modified_pdfs.zip')
    create_zip_file(modified_files, zip_file_path)

    # Return ZIP file URL
    return jsonify({'zipUrl': '/download/modified_pdfs.zip'})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(ZIP_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found.'}), 404
    return send_file(file_path, as_attachment=True)

def add_signature_to_pdf(pdf_path, signature_path, output_path):
    """Adds a signature image to every page of a PDF above the 'Prepared by' text."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Load signature image
    signature = Image.open(signature_path)
    signature.thumbnail((200, 100))  # Resize the signature

    # Iterate through PDF pages
    for page in reader.pages:
        # Add your logic to position the signature here (requires a library like PyMuPDF or ReportLab for fine control)
        writer.add_page(page)

    # Save modified PDF
    with open(output_path, 'wb') as f:
        writer.write(f)

def create_zip_file(files, output_zip_path):
    """Creates a ZIP file containing the given files."""
    import zipfile
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))

if __name__ == '__main__':
    app.run(debug=True)
