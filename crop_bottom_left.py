import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop bottom-left quadrant: x from 0 to 1200, y from 2000 to 3000
    crop = img[2000:3000, 0:1200]
    cv2.imwrite("cache/left_bottom_left.jpg", crop)
    print("Saved cache/left_bottom_left.jpg")

if __name__ == "__main__":
    main()
