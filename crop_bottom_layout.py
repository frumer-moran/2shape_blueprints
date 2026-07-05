import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop the bottom-middle section of Left Wing: x from 1000 to 2500, y from 2000 to 3000
    crop = img[2000:3000, 1000:2500]
    cv2.imwrite("cache/left_bottom_layout.jpg", crop)
    print("Saved cache/left_bottom_layout.jpg")

if __name__ == "__main__":
    main()
