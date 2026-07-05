import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop around C268 (61, 2516)
    x, y, r = 61, 2516, 20
    crop = img[y-100:y+100, x-50:x+150]
    cv2.circle(crop, (50, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c268.jpg", crop)
    print("Saved crop_c268.jpg")

if __name__ == "__main__":
    main()
