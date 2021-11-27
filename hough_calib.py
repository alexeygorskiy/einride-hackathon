import cv2
from PIL import Image
import numpy as np
from IPython.display import display

frame = cv2.imread('src.png')
frame = frame[60:120,10:140,:]
gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

kernel_size = 5
blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)
low_threshold = 190
high_threshold = 200
edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
rho = 1  # distance resolution in pixels of the Hough grid
theta = np.pi / 180  # angular resolution in radians of the Hough grid
threshold = 40  # minimum number of votes (intersections in Hough grid cell)
min_line_length = 40  # minimum number of pixels making up a line
max_line_gap = 10  # maximum gap in pixels between connectable line segments
line_image = np.copy(frame) * 0  # creating a blank to draw lines on

# Run Hough on edge detected image
# Output "lines" is an array containing endpoints of detected line segments
lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                    min_line_length, max_line_gap)
print(lines)
for line in lines:
    for x1,y1,x2,y2 in line:
        cv2.line(line_image,(x1,y1),(x2,y2),(0,0,255),1)
        pass


# Draw the lines on the  image
contours, hierarchy = cv2.findContours(image=edges, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

if contours is not None and len(contours) > 0:
    C = max(contours, key = cv2.contourArea)

    rect = cv2.minAreaRect(C)
    box = cv2.boxPoints(rect)
#cv2.drawContours(image=line_image, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
#print(contours)
#print(hierarchy)
#lines_edges = cv2.addWeighted(frame, 0.8, line_image, 1, 0)
#display(Image.fromarray(frame))
#display(Image.fromarray(gray))
#display(Image.fromarray(blur_gray))
#display(Image.fromarray(line_image))
display(Image.fromarray(line_image))