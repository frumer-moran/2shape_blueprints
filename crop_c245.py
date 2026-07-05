import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop around C245 (3751, 2242)
    x, y, r = 3751, 2242, 34
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c245.jpg", crop)
    print("Saved crop_c245.jpg")

if __name__ == "__main__":
    main()
