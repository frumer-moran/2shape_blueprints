import fitz  # PyMuPDF
import json

def inspect_page_text(pdf_path, page_num):
    print(f"\n--- Page {page_num + 1} Text Blocks ---")
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    
    # Extract text blocks with coordinates: (x0, y0, x1, y1, "text", block_no, block_type)
    blocks = page.get_text("blocks")
    
    # Sort blocks vertically by y0 coordinate
    blocks.sort(key=lambda b: b[1])
    
    for b in blocks:
        text = b[4].strip().replace("\n", " ")
        if text:
            # Print coordinate bounding box and text
            print(f"[{b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}] -> {text}")
            
    doc.close()

def main():
    pdf_path = "ostrovsky_31.pdf"
    inspect_page_text(pdf_path, 0) # Page 1
    inspect_page_text(pdf_path, 1) # Page 2

if __name__ == "__main__":
    main()
