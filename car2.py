from numpy.lib import angle
import websocket
import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt

host = "192.168.245.23"
port = 8887
deadband = np.pi/10
lower_bound = 0.4
max_throttle = 0.2
trim = -0.4

socket_address = f"ws://{host}:{port}/wsDrive"
video_address = f"http://{host}:{port}/video"

def middle_alg(frame):
    fov = 90
    lines = get_hough_lines(frame, fov, True)
    left_x = 0
    right_x = 160
    left_set = False
    right_set = False
    middle = 160/2
    for line in lines:
        for x1,y1,x2,y2 in line:
            if x1 < middle and x1>left_x:
                left_x = x1
                left_set = True
            elif x1 > middle and x1<right_x:
                right_x = x1
                right_set = True
            if x2 < middle and x2>left_x:
                left_x = x2
                left_set = True
            elif x2 > middle and x2<right_x:
                right_x = 2
                right_set = True

    
    if not left_set and not right_set:
        angle = trim
        throttle = -max_throttle
    elif not left_set: # If left line lost
        angle = -1
    elif not right_set :
        angle = 1

    mid_dev = middle - ((right_x - left_x)/2+left_x)
    angle = (-mid_dev/20) + trim
    print('mid dev',angle-trim)
    #print('angle',angle)
    throttle = max_throttle
    return [angle, throttle]



def vector_alg(frame):
    lines = get_hough_lines(frame, 90, True)
    vectors = get_vectors(lines)
    angle = trim
    throttle = max_throttle
    if len(vectors) != 0:

        #plt.quiver(*origin, vectors[:,0], vectors[:,1], color=['r','b','g'], scale=1)
        dir = np.sum(vectors, 0)    
        theta = np.arctan2(dir[1],dir[0])
        if abs(np.pi/2-theta) > deadband:
            angle = 1 - (1-lower_bound) * abs(np.cos(theta))
            angle *= np.sign(np.pi/2-theta)
            angle += trim
        else:
            angle = trim

        #throttle = max_throttle#*np.sin(theta)
    return [angle, throttle]

def get_vectors(lines):
    vectors = []
    for line in lines:
        for x1,y1,x2,y2 in line:
            if y1 > y2:
                vectors.append([x2-x1, y1-y2])
            else:
                vectors.append([x1-x2, y2-y1])
    return np.array(vectors)


def get_hough_lines(frame, fov, draw):
    frame = frame[fov:120,:,:]#frame[40:120,:,:]
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    kernel_size = 5
    blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)
    low_threshold = 190
    high_threshold = 200
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 20  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 10  # minimum number of pixels making up a line
    max_line_gap = 10  # maximum gap in pixels between connectable line segments
    line_image = np.copy(frame) * 0  # creating a blank to draw lines on

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                        min_line_length, max_line_gap)

    if type(lines) is np.ndarray:
        #print(lines)
        if draw:
            for line in lines:
                for x1,y1,x2,y2 in line:
                        cv2.line(line_image,(x1,y1),(x2,y2),(0,0,255),1)
                        cv2.circle(line_image, (x1,y1), radius=2, color=(255, 0, 0), thickness=2)
                        cv2.circle(line_image, (x2,y2), radius=2, color=(255, 0, 0), thickness=2)
                    
            lines_edges = cv2.addWeighted(frame, 0.8, line_image, 1, 0)
            cv2.imshow('video', lines_edges)
        return lines
    return np.array([])

def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)
    angle = 0.0
    throttle = 0.0
    message = f"{{\"angle\":{angle},\"throttle\":{throttle},\"drive_mode\":\"user\",\"recording\":false}}"
    ws.send(message)
    sys.exit()

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    cap = cv2.VideoCapture(video_address)

    ret, frame = cap.read()
    height = frame.shape[0]
    width = frame.shape[1]

    while True:
        try:
            ret, frame = cap.read()
            if ret:
                #angle, throttle = vector_alg(frame)
                angle, throttle = middle_alg(frame)
                #origin = np.array([[0]*len(vectors),[0]*len(vectors)]) # origin point
                #print('Theta:',np.rad2deg(theta))
                #print('Angle val:',angle)
                #plt.quiver(*origin, dir[0], dir[1], color=['r','b','g'], scale=1)
                #plt.show()
                if cv2.waitKey(1) == 27: 
                    break  # esc to quit
            #angle = 0
            #throttle = 0

            message = f"{{\"angle\":{angle},\"throttle\":{throttle},\"drive_mode\":\"user\",\"recording\":false}}"
            ws.send(message)
            #print(message)
        except Exception as error:
            on_error(ws, error)


if __name__ == "__main__":  
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(socket_address,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
