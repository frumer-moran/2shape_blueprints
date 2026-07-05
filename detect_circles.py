import cv2
import numpy as np

def main():
    img_path = "stitched_first_floor.jpg"
    img = cv2.imread(img_path)
    if img is None:
        print("Error: Could not load image.")
        return
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Hough Circles Transform
    # Parameters need to be tuned for blueprint circle sizes
    # Circles containing unit numbers are usually small (radius between 15 to 40 pixels on 200 DPI image)
    # We can detect them by specifying minRadius and maxRadius
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=50,
        param1=50,
        param2=30,
        minRadius=15,
        maxRadius=45
    )
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        print(f"Detected {len(circles)} circles in total.")
        
        # Draw detected circles on a copy
        output = img.copy()
        for (x, y, r) in circles[:30]: # print first 30
            print(f"Circle at x: {x}, y: {y}, radius: {r}")
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            
        cv2.imwrite("detected_circles.jpg", output)
        print("Saved visualization to detected_circles.jpg")
    else:
        print("No circles detected.")

if __name__ == "__main__":
    main()
