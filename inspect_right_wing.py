import os
from PIL import Image

def main():
    from google import genai
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set.")
        return
        
    client = genai.Client()
    img = Image.open("p2_right.png")
    
    prompt = (
        "Analyze this crop of the right wing of a floor plan (p2_right.png).\n"
        "Locate the circles containing the apartment unit numbers 1, 2, and 3.\n"
        "For each unit, tell me:\n"
        "1. The digit/number written inside the circle.\n"
        "2. The exact pixel coordinate (X, Y) of the center of that circle in this image (which has width 1324 and height 1247 pixels in PDF points, but at 200 DPI it is width 3680, height 3464 pixels. Please use pixel coordinates corresponding to the 200 DPI image size: width 3680, height 3464).\n"
        "3. The color of the unit border line.\n"
        "Be extremely careful. Find where the numbers 1, 2, 3 are written inside circles."
    )
    
    print("Calling Gemini Pro for right wing audit...")
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=[img, prompt]
    )
    print("\n--- Gemini response ---")
    print(response.text)

if __name__ == "__main__":
    main()
