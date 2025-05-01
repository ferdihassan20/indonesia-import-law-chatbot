import os
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm  # Import tqdm for progress bar

def pdf_to_images_with_ocr(pdf_path, image_folder, text_folder, success_count, error_files, total_pages):
    """
    Convert each page of a PDF to an image, perform OCR to extract text,
    and save both images and text to respective folders.
    """
    pdf_name = os.path.basename(pdf_path)[:-4]  # Extract file name without .pdf
    pdf_image_folder = os.path.join(image_folder, pdf_name)  # Create folder based on PDF name
    pdf_text_folder = os.path.join(text_folder, pdf_name)  # Folder for extracted text
    
    os.makedirs(pdf_image_folder, exist_ok=True)
    os.makedirs(pdf_text_folder, exist_ok=True)

    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        error_files.append(pdf_name)  # Store the name of the file that encountered an error
        return  # Skip the PDF if an error occurs

    success_count[0] += 1  # Increment successful PDF count
    total_pages[0] += len(images)  # Increment total pages processed

    # Use tqdm for a progress bar while processing PDF pages
    for page_number, image in tqdm(enumerate(images), desc=f"Processing {pdf_name}", total=len(images)):
        image_path = os.path.join(pdf_image_folder, f"{pdf_name}_page_{page_number + 1}.png")
        text_file_path = os.path.join(pdf_text_folder, f"{pdf_name}_page_{page_number + 1}.txt")

        image.save(image_path, 'PNG')
        
        text = pytesseract.image_to_string(image)
        
        with open(text_file_path, 'w') as text_file:
            text_file.write(text)

def process_pdf_folder(pdf_folder, image_folder, text_folder):
    """
    Process all PDFs in a folder by converting pages to images and extracting text via OCR.
    Skips PDFs that have already been processed.
    """
    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(text_folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    success_count = [0]  # Mutable counter for successful PDFs
    error_files = []  # List of PDFs that encountered errors
    total_pages = [0]  # Mutable counter for total pages processed

    for filename in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
        pdf_name = filename[:-4]
        pdf_image_folder = os.path.join(image_folder, pdf_name)
        pdf_text_folder = os.path.join(text_folder, pdf_name)

        # Skip processing if both image and text folders exist and are not empty
        if os.path.exists(pdf_image_folder) and os.path.exists(pdf_text_folder):
            if os.listdir(pdf_image_folder) and os.listdir(pdf_text_folder):
                print(f"Skipping {filename} as it is already processed.")
                continue

        pdf_path = os.path.join(pdf_folder, filename)
        pdf_to_images_with_ocr(pdf_path, image_folder, text_folder, success_count, error_files, total_pages)

    # Output summary
    print("\n===== SUMMARY =====")
    print(f"{success_count[0]} PDF files were successfully processed.")
    print(f"{total_pages[0]} pages were processed with OCR.")
    
    if error_files:
        print(f"{len(error_files)} PDF files encountered errors:")
        for file in error_files:
            print(f"   - {file}")
    else:
        print("All PDFs were processed successfully.")

if __name__ == "__main__":
    pdf_folder = "datasets/pdfs"  # Folder containing PDFs
    image_folder = "datasets/images"  # Folder for saving images
    text_folder = "datasets/raw_texts"  # Folder for saving extracted text
    
    process_pdf_folder(pdf_folder, image_folder, text_folder)
