import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop around C163 (589, 1916)
    x, y, r = 589, 1916, 30
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c163.jpg", crop)
    print("Saved crop_c163.jpg")

if __name__ == "__main__":
    main()
