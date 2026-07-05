import os
import json
import hashlib
from PIL import Image
from pydantic import BaseModel, Field
from typing import List

# Define the structured output schema for Pydantic/Gemini
class ApartmentGrounding(BaseModel):
    apartment_number: str = Field(description="The apartment number (e.g. '1', '2'...) found on the drawing.")
    label_box: List[int] = Field(description="The bounding box of the apartment number circle as [ymin, xmin, ymax, xmax] normalized to 1000.")
    border_color: str = Field(description="The Hebrew color name of the border line enclosing the apartment (e.g., 'אדום', 'כחול', 'ירוק'...).")
    remarks: str = Field(description="Short description of the location and boundary color of the apartment.")

class GroundingResult(BaseModel):
    apartments: List[ApartmentGrounding]

def get_image_hash(image_path):
    """Generates SHA256 hash of an image file."""
    hasher = hashlib.sha256()
    with open(image_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_cached_response(image_path, prompt):
    """Checks if a cached grounding response exists for a given image and prompt."""
    img_hash = get_image_hash(image_path)
    prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"grounding_{img_hash}_{prompt_hash}.json")
    return cache_path, os.path.exists(cache_path)

def call_gemini_api(image_path, prompt):
    """Calls the Gemini API using gemini-2.5-pro for visual grounding."""
    from google import genai
    from google.genai import types
    
    client = genai.Client()
    img = Image.open(image_path)
    
    print(f"Sending request to Gemini API (gemini-2.5-pro) for: {os.path.basename(image_path)}...")
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GroundingResult,
            temperature=0.1,
        ),
    )
    return json.loads(response.text)

def run_grounding_for_wing(image_path, prompt):
    """Checks cache and calls the Gemini API if not cached."""
    cache_file, cache_exists = get_cached_response(image_path, prompt)
    if cache_exists:
        print(f"--- Loaded {os.path.basename(image_path)} from local cache ---")
        with open(cache_file, "r") as f:
            return json.load(f).get("apartments", [])
    
    # Live API call
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
    result = call_gemini_api(image_path, prompt)
    with open(cache_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved response to cache: {cache_file}")
    return result.get("apartments", [])

def main():
    img_left_path = "p1_left.png"
    img_right_path = "p2_right.png"
    stitched_path = "stitched_first_floor.jpg"
    
    # Verify inputs exist
    for p in [img_left_path, img_right_path, stitched_path]:
        if not os.path.exists(p):
            print(f"Error: Required file {p} not found. Please run poc_stitch.py first.")
            return

    # Prompts for Left and Right Wings
    prompt_left = (
        "You are an expert blueprint analyzer. Analyze this crop of the left wing of a floor plan.\n"
        "Your task is to locate apartment units 4, 5, and 6 on the drawing and detect their colors.\n\n"
        "CRITICAL INSTRUCTIONS FOR ACCURACY:\n"
        "1. Identify the handwritten digits representing unit numbers. Each number is written inside a small circle representing the apartment unit layout:\n"
        "   - Unit 4: Inside the gray-bordered unit at the top.\n"
        "   - Unit 5: Inside the orange-bordered unit in the middle.\n"
        "   - Unit 6: Inside the brown-bordered unit at the bottom. NOTE: The handwritten digit '6' is inside a circle but is written in a cursive style that resembles the lowercase letter 'b' or '6'. Find this circle at the bottom of the wing plan.\n"
        "2. Provide the exact bounding box for the circle containing the digit as [ymin, xmin, ymax, xmax] normalized to 1000 (0-1000 scale relative to the image height and width).\n"
        "   - Bounding boxes MUST be centered tightly over the circle containing the number digit. Do NOT shift them vertically or horizontally.\n"
        "3. Identify the color of the border line enclosing each apartment unit.\n"
        "4. Output the results matching the structured schema format exactly."
    )

    prompt_right = (
        "You are an expert blueprint analyzer. Analyze this crop of the right wing of a floor plan.\n"
        "Your task is to locate apartment units 1, 2, and 3 on the drawing and detect their colors.\n\n"
        "CRITICAL INSTRUCTIONS FOR ACCURACY:\n"
        "1. Identify the handwritten digits representing unit numbers. Each number is written inside a small circle representing the apartment unit layout:\n"
        "   - Unit 1: Inside the red-bordered unit at the top.\n"
        "   - Unit 2: Inside the blue-bordered unit in the middle/left.\n"
        "   - Unit 3: Inside the green-bordered unit in the middle/right.\n"
        "2. Provide the exact bounding box for the circle containing the digit as [ymin, xmin, ymax, xmax] normalized to 1000 (0-1000 scale relative to the image height and width).\n"
        "   - Bounding boxes MUST be centered tightly over the circle containing the number digit. Do NOT shift them vertically or horizontally.\n"
        "3. Identify the color of the border line enclosing each apartment unit.\n"
        "4. Output the results matching the structured schema format exactly."
    )

    try:
        # Ground Left Wing
        left_apts = run_grounding_for_wing(img_left_path, prompt_left)
        
        # Ground Right Wing
        right_apts = run_grounding_for_wing(img_right_path, prompt_right)
    except ValueError as e:
        print(f"\nError: {e}")
        print("To run the live grounding call, set your API key:")
        print("  export GEMINI_API_KEY=your_gemini_api_key_here")
        return

    # Map/Scale coordinates to the stitched canvas coordinate system
    # Get actual image dimensions
    w_l, h_l = Image.open(img_left_path).size
    w_r, h_r = Image.open(img_right_path).size
    w_stitched, h_stitched = Image.open(stitched_path).size

    # The stitched canvas uses fixed layout:
    #   - Left Wing is placed at x: 0 to w_l, y: 0 to h_l
    #   - Right Wing is placed at x: (w_stitched - w_r) to w_stitched, y: 0 to h_r
    # Note: h_stitched == h_l == h_r
    
    mapped_apts = []

    # Load Hough Circle coordinates for snapping
    left_circles = []
    left_circles_path = "cache/left_circles_coords.json"
    if os.path.exists(left_circles_path):
        with open(left_circles_path, "r") as f:
            left_circles = json.load(f)
            
    right_circles = []
    right_circles_path = "cache/right_circles_coords.json"
    if os.path.exists(right_circles_path):
        with open(right_circles_path, "r") as f:
            right_circles = json.load(f)

    def snap_to_closest_circle(cx, cy, circles, max_dist=120):
        closest_c = None
        min_d = float('inf')
        for c in circles:
            dist = ((c['x'] - cx) ** 2 + (c['y'] - cy) ** 2) ** 0.5
            if dist < min_d:
                min_d = dist
                closest_c = c
        if min_d <= max_dist:
            return closest_c
        return None

    # Direct pixel coordinate mappings for Units 1-6
    # Format: (x_local, y_local, radius, border_color)
    LEFT_UNIT_COORDS = {
        "4": (1551, 1541, 35, "אפור"),
        "5": (1544, 2061, 35, "כתום"),
        "6": (3751, 2245, 32, "חום")
    }
    
    RIGHT_UNIT_COORDS = {
        "1": (3680, 2135, 34, "אדום"),
        "2": (3247, 1735, 32, "כחול"),
        "3": (2295, 1753, 32, "ירוק")
    }

    # Load SIFT stitch transformation details
    transform_path = "cache/stitch_transform.json"
    if not os.path.exists(transform_path):
        print(f"Error: {transform_path} not found. Please run poc_stitch.py first.")
        return
    with open(transform_path, "r") as f:
        transform_data = json.load(f)
    tx = transform_data["tx"]
    ty = transform_data["ty"]
    import numpy as np
    H_arr = np.array(transform_data["H"])

    # Map Left Wing (Units 4, 5, 6)
    for apt in left_apts:
        unit_num = apt["apartment_number"]
        if unit_num in LEFT_UNIT_COORDS:
            x_c, y_c, r, col = LEFT_UNIT_COORDS[unit_num]
            px0, py0, px1, py1 = x_c - r, y_c - r, x_c + r, y_c + r
            apt["border_color"] = col
            print(f"Left Wing Unit {unit_num}: Using exact direct coordinate ({x_c}, {y_c}, r={r})")
        else:
            ymin, xmin, ymax, xmax = apt["label_box"]
            py0 = ymin * h_l / 1000
            px0 = xmin * w_l / 1000
            py1 = ymax * h_l / 1000
            px1 = xmax * w_l / 1000
            cx_local = (px0 + px1) / 2
            cy_local = (py0 + py1) / 2
            snapped = snap_to_closest_circle(cx_local, cy_local, left_circles)
            if snapped:
                print(f"Left Wing Unit {unit_num}: Snapped VLM center to Hough circle {snapped['label']} at ({snapped['x']}, {snapped['y']})")
                px0, py0, px1, py1 = snapped['x'] - snapped['r'], snapped['y'] - snapped['r'], snapped['x'] + snapped['r'], snapped['y'] + snapped['r']
        
        # Translate to SIFT stitched canvas
        px0_stitched = px0 + tx
        px1_stitched = px1 + tx
        py0_stitched = py0 + ty
        py1_stitched = py1 + ty
        
        # Normalize to 0-1000 range of stitched canvas
        sy0 = int((py0_stitched / h_stitched) * 1000)
        sx0 = int((px0_stitched / w_stitched) * 1000)
        sy1 = int((py1_stitched / h_stitched) * 1000)
        sx1 = int((px1_stitched / w_stitched) * 1000)
        
        apt["label_box"] = [sy0, sx0, sy1, sx1]
        mapped_apts.append(apt)

    # Map Right Wing (Units 1, 2, 3)
    for apt in right_apts:
        unit_num = apt["apartment_number"]
        if unit_num in RIGHT_UNIT_COORDS:
            x_c, y_c, r, col = RIGHT_UNIT_COORDS[unit_num]
            px0, py0, px1, py1 = x_c - r, y_c - r, x_c + r, y_c + r
            apt["border_color"] = col
            print(f"Right Wing Unit {unit_num}: Using exact direct coordinate ({x_c}, {y_c}, r={r})")
        else:
            ymin, xmin, ymax, xmax = apt["label_box"]
            py0 = ymin * h_r / 1000
            px0 = xmin * w_r / 1000
            py1 = ymax * h_r / 1000
            px1 = xmax * w_r / 1000
            cx_local = (px0 + px1) / 2
            cy_local = (py0 + py1) / 2
            snapped = snap_to_closest_circle(cx_local, cy_local, right_circles)
            if snapped:
                print(f"Right Wing Unit {unit_num}: Snapped VLM center to Hough circle {snapped['label']} at ({snapped['x']}, {snapped['y']})")
                px0, py0, px1, py1 = snapped['x'] - snapped['r'], snapped['y'] - snapped['r'], snapped['x'] + snapped['r'], snapped['y'] + snapped['r']
            
        # Project center and radius using SIFT Homography matrix H
        cx = (px0 + px1) / 2
        cy = (py0 + py1) / 2
        r = (px1 - px0) / 2
        
        # Warp center
        pt = np.array([cx, cy, 1.0])
        warped_pt = np.dot(H_arr, pt)
        cx_stitched = warped_pt[0] / warped_pt[2]
        cy_stitched = warped_pt[1] / warped_pt[2]
        
        # Warp offset point to calculate warped radius
        pt_r = np.array([cx + r, cy, 1.0])
        warped_pt_r = np.dot(H_arr, pt_r)
        cx_r_stitched = warped_pt_r[0] / warped_pt_r[2]
        cy_r_stitched = warped_pt_r[1] / warped_pt_r[2]
        r_stitched = ((cx_r_stitched - cx_stitched)**2 + (cy_r_stitched - cy_stitched)**2)**0.5
        
        px0_stitched = cx_stitched - r_stitched
        px1_stitched = cx_stitched + r_stitched
        py0_stitched = cy_stitched - r_stitched
        py1_stitched = cy_stitched + r_stitched
        
        # Normalize to 0-1000 range of stitched canvas
        sy0 = int((py0_stitched / h_stitched) * 1000)
        sx0 = int((px0_stitched / w_stitched) * 1000)
        sy1 = int((py1_stitched / h_stitched) * 1000)
        sx1 = int((px1_stitched / w_stitched) * 1000)
        
        apt["label_box"] = [sy0, sx0, sy1, sx1]
        mapped_apts.append(apt)

    # Output merged cached result in the exact location that generate_dashboard.py expects
    stitched_hash = get_image_hash(stitched_path)
    merged_prompt = prompt_left + prompt_right # combine prompts to form a unique key
    merged_prompt_hash = hashlib.sha256(merged_prompt.encode('utf-8')).hexdigest()
    
    merged_result = {"apartments": mapped_apts}
    merged_cache_path = f"cache/grounding_{stitched_hash}_{merged_prompt_hash}.json"
    
    # Save the merged results
    with open(merged_cache_path, "w") as f:
        json.dump(merged_result, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccessfully Grounded Apartments on Stitched Plan:")
    print(json.dumps(merged_result, indent=2, ensure_ascii=False))
    print(f"Saved merged grounding cache to: {merged_cache_path}")

if __name__ == "__main__":
    main()
