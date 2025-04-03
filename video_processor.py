from multiprocessing.spawn import old_main_modules

import cv2
import numpy as np
from new_dot_sorter import MegaSorter
class VideoProcessor:
    def __init__(self, plot):
        self.cap = None
        self.running = False
        self.object_det = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)
        self.dominant_color = ""
        self.counter = 0
        self.cords = []
        self.flag = 0
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.cords2 = []
        self.home_pos = []
        self.black_c = False
        self.old = 0
        self.new = 0
        self.plot = plot

    def load_video(self, file_path):
        self.cap = cv2.VideoCapture(file_path)

    def check_black_corners(self, frame):
        height, width, _ = frame.shape
        corners = [
            frame[0, 0],
            frame[0, width - 1],
            frame[height - 1, 0],
            frame[height - 1, width - 1]
        ]
        for corner in corners:
            r, g, b = corner
            if r > 10 or g > 10 or b > 10:
                return False
        return True
    def dm_color(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pixels = image.reshape(-1, 3)
        pixels = np.float32(pixels)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = 3
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        second_dominant_color = centers[1]
        def get_color_name(rgb_color):
            r, g, b = rgb_color
            if r > g and r > b:
                return "1"
            elif g > r and g > b:
                return "2"
            elif b > r and b > g:
                return "3"

        color_name = get_color_name(second_dominant_color)
        return color_name

    def process_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        frame_cords = []
        if not ret:
            self.running = False
            return None
        if  not self.black_c:
            self.black_c = self.check_black_corners(frame)
        if self.black_c:
            if self.flag == 0:
                self.dominant_color = self.dm_color(frame)
            if self.dominant_color == "1":
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower_red1 = np.array([150, 100, 100])
                upper_red1 = np.array([180, 255, 255])
                lower_red2 = np.array([170, 120, 70])
                upper_red2 = np.array([180, 255, 255])
                mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                mask = mask1 + mask2
            elif self.dominant_color == "2":
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower_green = np.array([40, 50, 50])
                upper_green = np.array([100, 255, 255])
                mask = cv2.inRange(hsv, lower_green, upper_green)
            elif self.dominant_color == "3":
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower_blue = np.array([100, 100, 50])
                upper_blue = np.array([140, 255, 255])
                mask = cv2.inRange(hsv, lower_blue, upper_blue)
            _, mask = cv2.threshold(mask, 120, 255, cv2.THRESH_BINARY)
            cv2.imshow("mask", mask)
            if self.flag<=12:
                tracked_centers = []
                blurred = cv2.GaussianBlur(mask, (5, 5), 0)

                _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)

                circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=30, minRadius=50, maxRadius=500)

                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    x, y, r = circles[0][0]

                    square_side = int(r * np.sqrt(2) / 2)
                    x1, y1 = x - square_side, y - square_side
                    x2, y2 = x + square_side, y + square_side

                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    for cnt in contours:
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])

                            if x1 <= cx <= x2 and y1 <= cy <= y2:
                                tracked_centers.append((cx, cy))

                    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # Круг
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Квадрат

                    for cx, cy in tracked_centers:
                        cv2.circle(frame, (cx, cy), 3, (0, 255, 255), -1)
                    self.cords2.append([len(tracked_centers), x1, y1, x2, y2])
                    self.home_pos.append([len(tracked_centers), tracked_centers])
                    self.flag +=1
            if self.flag==13:
                self.cords2.sort(key=lambda x: x[0], reverse=True)
                self.x1 = self.cords2[0][1]
                self.y1 = self.cords2[0][2]
                self.x2 = self.cords2[0][3]
                self.y2 = self.cords2[0][4]

            if self.flag>=13:
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                if self.flag:
                    cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (255, 0, 0), 5)
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area > 35:
                        x, y, w, h = cv2.boundingRect(cnt)
                        frame_cords.append((x + (w / 2), y + (h / 2)))
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 3)

                sorter = MegaSorter(self.home_pos, frame_cords)
                self.old, self.new = sorter.process()
                self.plot.update_data(self.old, self.new)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame