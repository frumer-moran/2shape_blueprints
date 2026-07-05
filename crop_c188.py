import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop around C188 (3209, 2015)
    x, y, r = 3209, 2015, 30
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c188.jpg", crop)
    print("Saved crop_c188.jpg")

if __name__ == "__main__":
    main()
