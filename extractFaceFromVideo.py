# Face detection code with sanity check
import numpy as np 
import cv2 

# Load test image
# im = cv2.imread("test.jpg")

## Mount to google drive
from google.colab import drive
drive.mount('/content/drive')


det = cv2.CascadeClassifier("drive/MyDrive/Colab Notebooks/haarcascade_frontalface_default.xml")

vName = "drive/MyDrive/video1.mp4"
cap = cv2.VideoCapture(vName)

# Check if camera opened successfully

if (cap.isOpened()== False):
    print("Error opening video stream or file")

# Read until video is completed
idx = 0
while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        # process the image
        idx = idx + 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = det.detectMultiScale(gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(100, 100), # adjust to your image size, maybe smaller, maybe larger?
            flags=cv2.CASCADE_SCALE_IMAGE)

        for (x, y, w, h) in rects:
            # x: x location
            # y: y location
            # w: width of the rectangle 
            # h: height of the rectangle
            # Remember, order in images: [y, x, channel]
            # cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 20)
            crop_img = frame[y:y+h, x:x+w]
            fileName = "JF-faces/img" + str(idx) + ".jpg"
            crop_img = cv2.resize(crop_img, (128, 128))
            cv2.imwrite(fileName, crop_img)
