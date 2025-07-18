import os
import gc
import psutil
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def pdf_to_images_with_ocr(pdf_path, image_folder, text_folder, success_count, error_files, total_pages):
    """
    Convert each page of a PDF to an image, perform OCR to extract text,
    and save both images and text to respective folders.
    Processes pages one by one to minimize memory usage.
    """
    pdf_name = os.path.basename(pdf_path)[:-4]
    pdf_image_folder = os.path.join(image_folder, pdf_name)
    pdf_text_folder = os.path.join(text_folder, pdf_name)
    
    os.makedirs(pdf_image_folder, exist_ok=True)
    os.makedirs(pdf_text_folder, exist_ok=True)

    try:
        # Get total pages first without loading images
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        total_page_count = len(convert_from_path(pdf_path))
        
        # Process pages in batches to manage memory
        batch_size = 5  # Process 5 pages at a time
        pages_processed = 0
        
        for batch_start in range(1, total_page_count + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, total_page_count)
            
            # Load only current batch
            batch_images = convert_from_path(
                pdf_path, 
                first_page=batch_start, 
                last_page=batch_end
            )
            
            for relative_page, image in enumerate(batch_images):
                actual_page = batch_start + relative_page
                image_path = os.path.join(pdf_image_folder, f"{pdf_name}_page_{actual_page}.png")
                text_file_path = os.path.join(pdf_text_folder, f"{pdf_name}_page_{actual_page}.txt")

                # Save image
                image.save(image_path, 'PNG')
                
                # Extract text
                text = pytesseract.image_to_string(image)
                
                with open(text_file_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(text)
                
                pages_processed += 1
                
                # Force garbage collection to free memory
                del image
                del text
            
            # Clear batch images from memory
            del batch_images
            gc.collect()
        
        success_count[0] += 1
        total_pages[0] += total_page_count
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        error_files.append(pdf_name)
        return

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
    pdf_folder = "datasets/pdfs"  
    image_folder = "datasets/images"  
    text_folder = "datasets/raw_texts" 
    
    process_pdf_folder(pdf_folder, image_folder, text_folder)
