import cv2

def main():
    img = cv2.imread("p1_left.png")
    h, w = img.shape[:2]
    
    # Slice the entire width (0 to w) of the Left Wing Page 1 crop
    # Region 1: y from 1000 to 2200
    cv2.imwrite("cache/left_full_mid.jpg", img[1000:2200, 0:w])
    
    # Region 2: y from 2200 to 3388 (bottom)
    cv2.imwrite("cache/left_full_bot.jpg", img[2200:h, 0:w])
    
    print(f"Saved full-width left wing slices. Width: {w}, Height: {h}")

if __name__ == "__main__":
    main()
