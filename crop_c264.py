import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop around C264 (1621, 2497)
    x, y, r = 1621, 2497, 44
    crop = img[y-100:y+100, x-100:x+100]
    cv2.rectangle(crop, (100-r, 100-r), (100+r, 100+r), (0, 0, 255), 2)
    cv2.imwrite("crop_c264.jpg", crop)
    print("Saved crop_c264.jpg")

if __name__ == "__main__":
    main()
