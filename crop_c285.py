import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop around C285 (1574, 2683)
    x, y, r = 1574, 2683, 21
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c285.jpg", crop)
    print("Saved crop_c285.jpg")

if __name__ == "__main__":
    main()
