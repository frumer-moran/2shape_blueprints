import cv2

def main():
    img = cv2.imread("p1_left.png")
    
    # Crop around C118 (236, 1829)
    x, y, r = 236, 1829, 30
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c118.jpg", crop)
    print("Saved crop_c118.jpg")
    
    # Crop around C122 (1195, 1803)
    x, y, r = 1195, 1803, 30
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c122.jpg", crop)
    print("Saved crop_c122.jpg")

if __name__ == "__main__":
    main()
