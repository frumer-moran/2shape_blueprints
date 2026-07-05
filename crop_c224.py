import cv2

def main():
    img = cv2.imread("p2_right.png")
    # Crop around C224 (3680, 2135)
    x, y, r = 3680, 2135, 34
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c224.jpg", crop)
    print("Saved crop_c224.jpg")

if __name__ == "__main__":
    main()
