import os
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm  # Import tqdm for progress bar

def pdf_to_images_with_ocr(pdf_path, image_folder, text_folder, success_count, error_files, total_pages):
    pdf_name = os.path.basename(pdf_path)[:-4]  # Extract file name without .pdf
    pdf_image_folder = os.path.join(image_folder, pdf_name)  # Create folder based on PDF name
    pdf_text_folder = os.path.join(text_folder, pdf_name)  # Folder for extracted text
    
    os.makedirs(pdf_image_folder, exist_ok=True)  # Create folder if it does not exist
    os.makedirs(pdf_text_folder, exist_ok=True)  # Create folder if it does not exist

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

        # Save image
        image.save(image_path, 'PNG')
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        # Save extracted text
        with open(text_file_path, 'w') as text_file:
            text_file.write(text)

def process_pdf_folder(pdf_folder, image_folder, text_folder):
    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(text_folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    success_count = [0]  # List is used so it can be modified inside functions
    error_files = []  # Store the names of files that encountered errors
    total_pages = [0]  # Store the total number of pages processed

    for filename in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
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
    pdf_folder = "Pdf_files"  # Folder containing PDFs
    image_folder = "Dataset/Dataset_image"  # Folder for saving images
    text_folder = "Dataset/Dataset_text"  # Folder for saving extracted text
    
    process_pdf_folder(pdf_folder, image_folder, text_folder)
