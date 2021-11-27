import websocket
import cv2
import numpy as np
import sys
from IPython.display import display
from PIL import Image

host = "192.168.245.23"
port = 8887

socket_address = f"ws://{host}:{port}/wsDrive"
video_address = f"http://{host}:{port}/video"

def show_hough(frame):
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

    if type(lines) is np.ndarray:
        print(lines)
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv2.line(line_image,(x1,y1),(x2,y2),(0,0,255),1)
                cv2.circle(line_image, (x1,y1), radius=2, color=(255, 0, 0), thickness=3)
                cv2.circle(line_image, (x2,y2), radius=2, color=(255, 0, 0), thickness=3)
                pass
        
        display(Image.fromarray(line_image))

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
                show_hough(frame)
            angle = 0
            throttle = 0

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
