import websocket
import cv2
import numpy as np
import sys

host = "192.168.245.23"
port = 8887

socket_address = f"ws://{host}:{port}/wsDrive"
video_address = f"http://{host}:{port}/video"

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
            angle = 0
            throttle = 0.5

            message = f"{{\"angle\":{angle},\"throttle\":{throttle},\"drive_mode\":\"user\",\"recording\":false}}"
            ws.send(message)
            print(message)
        except Exception as error:
            on_error(ws, error)


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(socket_address,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
