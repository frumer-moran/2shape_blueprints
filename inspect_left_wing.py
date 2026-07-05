import cv2

def main():
    img = cv2.imread("p1_left.png")
    h, w = img.shape[:2]
    
    # We will slice the left wing plan into 3 high-res vertical regions
    # (since the plan is vertically tall and spans from x: 1000 to 2500 in pixels)
    # Let's crop the active column: x from 1200 to 2400
    x0, x1 = 1200, 2400
    
    # Region 1: Top (y: 0 to 1200)
    cv2.imwrite("cache/left_top.jpg", img[0:1200, x0:x1])
    
    # Region 2: Middle (y: 1200 to 2300)
    cv2.imwrite("cache/left_mid.jpg", img[1200:2300, x0:x1])
    
    # Region 3: Bottom (y: 2300:3388)
    cv2.imwrite("cache/left_bot.jpg", img[2300:h, x0:x1])
    
    print("Saved left wing vertical slices to cache/left_top.jpg, cache/left_mid.jpg, cache/left_bot.jpg")

if __name__ == "__main__":
    main()
