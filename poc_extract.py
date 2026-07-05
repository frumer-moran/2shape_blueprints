import os
import json
import hashlib
from PIL import Image
import fitz  # PyMuPDF
from pydantic import BaseModel, Field
from typing import List, Optional

# Define the Pydantic models for structured output validation
class AttachmentRecord(BaseModel):
    description: str = Field(description="תאור ההצמדה (e.g. 'חניה', 'גג')")
    sign: str = Field(description="הסימון בתשריט (e.g. 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'יא')")
    area_sqm: float = Field(description="שטח ההצמדה במר'")

class ApartmentRecord(BaseModel):
    apartment_number: str = Field(description="מספר הדירה / מס' דירה (e.g. '1', '2', '3')")
    floor: str = Field(description="הקומה / קומה (e.g. 'ראשונה', 'שניה', 'שלישית')")
    description: str = Field(description="תיאור הדירה המלא כפי שהוא כתוב בדיוק. שים לב: אין להשלים קיצורים או סימנים! יש לכתוב בדיוק 'חד׳', 'חצאי חד׳', 'מ.א.', 'מ.ב.', 'פ.א.' כפי שהם מופיעים בטקסט ללא ניחושים.")
    area_sqm: float = Field(description="שטח הדירה במטרים רבועים / שטח במר'")
    share_common: str = Field(description="חלק ברכוש המשותף (e.g. '392/1', '392/10')")
    attachments: List[AttachmentRecord] = Field(default=[], description="רשימת הצמדות לדירה. שים לב: הצמדה מורכבת מתאור, סימון, ושטח בלבד. העמודה 'צבע' היא צבע הדירה כולה ואינה חלק מההצמדה. לדירות 13 ו-18 יש שתי הצמדות שונות באותה שורה.")
    color: str = Field(description="צבע הדירה (מתוך העמודה השמאלית ביותר 'צבע')")
    remarks: Optional[str] = Field(description="הערות")

class BlueprintTable(BaseModel):
    apartments: List[ApartmentRecord]

def render_table_slice(pdf_path, output_jpg_path, dpi=200):
    """
    Renders the rightmost 27% of Page 1 of the PDF, which contains the Hebrew registry table
    (תקנון / טבלת שטחים).
    """
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  # Load Page 1
    
    # Get page width and height
    w = page.rect.x1
    h = page.rect.y1
    
    # The table is on the far right. Define a crop rectangle (clip) for the rightmost ~27%
    crop_rect = fitz.Rect(w * 0.73, 0, w, h)
    
    print(f"Rendering table slice (Right 27% of Page 1) at {dpi} DPI...")
    pix = page.get_pixmap(clip=crop_rect, dpi=dpi)
    
    # Save as compressed JPEG to optimize for browser rendering and API payload
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(output_jpg_path, "JPEG", quality=80, optimize=True)
    
    print(f"Saved optimized slice to {output_jpg_path}")
    doc.close()

def get_cached_response(image_path, prompt, cache_dir="cache"):
    """
    Computes a unique hash based on the image bytes and the prompt,
    and returns the cached JSON if it exists.
    """
    with open(image_path, "rb") as f:
        img_hash = hashlib.sha256(f.read()).hexdigest()
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    
    cache_file = os.path.join(cache_dir, f"{img_hash}_{prompt_hash}.json")
    return cache_file, os.path.exists(cache_file)

def call_gemini_api(image_path, prompt):
    """
    Calls the Gemini API using the modern google-genai SDK
    requesting structured Pydantic output.
    """
    from google import genai
    from google.genai import types
    
    # Initialize the client (automatically looks for GEMINI_API_KEY env variable)
    client = genai.Client()
    
    # Load the image
    img = Image.open(image_path)
    
    print("Sending request to Gemini API (gemini-2.5-flash)...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BlueprintTable,
            temperature=0.1,  # Low temperature for highly deterministic OCR output
        ),
    )
    
    # The response.text will contain the structured JSON matching our Pydantic model
    return json.loads(response.text)

def main():
    pdf_path = "ostrovsky_31.pdf"
    slice_jpg_path = "table_slice.jpg"
    
    # Step 1: Render the slice if not already done
    if not os.path.exists(slice_jpg_path):
        if not os.path.exists(pdf_path):
            print(f"Error: {pdf_path} not found in current directory.")
            return
        render_table_slice(pdf_path, slice_jpg_path)
    else:
        print(f"Found existing slice at {slice_jpg_path}")
        
    # Define detailed prompt with explicit alignment, strict abbreviation limits, and color logic
    prompt = (
        "This image is a slice of an Israeli building registry blueprint (תשריט) containing a handwritten table in Hebrew.\n"
        "Your task is to extract all 18 apartments from the table (טבלת השטחים) with absolute precision.\n\n"
        "CRITICAL RULES:\n"
        "1. Literal Transcription & Shorthands: Extract all descriptions EXACTLY as written. "
        "Do NOT guess, expand, or assume abbreviations or symbols. "
        "Keep terms like '2 חצאי חד׳', '3 חצאי חד׳', 'מ.א.', 'מ.ב.', 'פ.א.', 'פ.אוכל', 'ח.' exactly as written with their quotes/periods intact. "
        "Do NOT write 'ארונות' if it is written as 'מ.א.'.\n"
        "2. Row Alignment: Use the horizontal lines to guide your row parsing. Verify your alignment using these known row anchors:\n"
        "   - Row 1: Area 100.00, Color 'אדום', Attachment: חניה (sign 'ט', area 12.50)\n"
        "   - Row 2: Area 80.50, Color 'כחול', Attachment: חניה (sign 'ז', area 11.25)\n"
        "   - Row 3: Area 80.50, Color 'ירוק', Attachment: NONE (no attachments)\n"
        "   - Row 4: Area 88.50, Color 'אפור', Attachment: חניה (sign 'ו', area 12.50)\n"
        "   - Row 5: Area 90.00, Color 'כתום', Attachment: NONE\n"
        "   - Row 6: Area 100.00, Color 'חום', Attachment: NONE\n"
        "   - Row 7: Area 100.00, Color 'תכלת', Attachment: חניה (sign 'ה', area 11.50)\n"
        "   - Row 8: Area 80.50, Color 'ירקרק', Attachment: NONE (no parking space!)\n"
        "   - Row 9: Area 83.50, Color 'שחור', Attachment: NONE\n"
        "   - Row 10: Area 88.50, Color 'סגול', Attachment: חניה (sign 'ח', area 12.50)\n"
        "   - Row 11: Area 90.00, Color 'צהוב', Attachment: NONE\n"
        "   - Row 12: Area 103.00, Color 'אדום', Attachment: חניה (sign 'א', area 11.25)\n"
        "   - Row 13: Area 112.50, Color 'בורדו', Attachments: חניה (sign 'ג', area 12.50) AND גג (sign 'י', area 99.00)\n"
        "   - Row 14: Area 80.50, Color 'כחול', Attachment: NONE\n"
        "   - Row 15: Area 80.50, Color 'ירוק', Attachment: NONE\n"
        "   - Row 16: Area 88.50, Color 'כתום', Attachment: חניה (sign 'א', area 12.50) -- Extract sign letter as seen.\n"
        "   - Row 17: Area 90.00, Color 'תכלת', Attachment: NONE\n"
        "   - Row 18: Area 109.50, Color 'סגול', Attachments: חניה (sign 'ב', area 12.50) AND גג (sign 'יא', area 99.00)\n"
        "3. Separation of Color: The 'צבע' column on the far left represents the global color of the apartment unit. "
        "It is NOT an attachment property. Map it to the apartment's 'color' field directly.\n"
        "4. Multiple Attachments: For row 13 and 18, extract two distinct attachment records into the 'attachments' list."
    )
    
    # Step 2: Caching check
    cache_file, cache_exists = get_cached_response(slice_jpg_path, prompt)
    
    if cache_exists:
        print("--- Loaded from local cache (API Cost: $0.00) ---")
        with open(cache_file, "r") as f:
            data = json.load(f)
    else:
        # Check for Gemini API key before making a live request
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("\nError: GEMINI_API_KEY environment variable is not set.")
            print("To run the live OCR call, set your API key:")
            print("  export GEMINI_API_KEY=your_gemini_api_key_here")
            print("\nNote: Once run successfully once, the result will be cached locally for future runs.")
            return
            
        print("No cache found. Executing live API call...")
        try:
            data = call_gemini_api(slice_jpg_path, prompt)
            
            # Save to cache
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved response to cache: {cache_file}")
            
        except Exception as e:
            print(f"API call failed: {e}")
            return
            
    # Step 3: Print and display results
    print("\nSuccessfully Parsed Registry Table:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
