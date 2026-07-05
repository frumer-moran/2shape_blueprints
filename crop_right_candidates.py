import cv2

def main():
    img = cv2.imread("p2_right.png")
    
    # Crop C228 (2249, 2179)
    x, y, r = 2249, 2179, 34
    crop = img[y-100:y+100, x-100:x+100]
    cv2.imwrite("crop_c228.jpg", crop)
    print("Saved crop_c228.jpg")
    
    # Crop C127 (2295, 1753)
    x, y, r = 2295, 1753, 32
    crop = img[y-100:y+100, x-100:x+100]
    cv2.imwrite("crop_c127.jpg", crop)
    print("Saved crop_c127.jpg")
    
    # Crop C294 (3227, 2375)
    x, y, r = 3227, 2375, 28
    crop = img[y-100:y+100, x-100:x+100]
    cv2.imwrite("crop_c294.jpg", crop)
    print("Saved crop_c294.jpg")

if __name__ == "__main__":
    main()
