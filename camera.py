import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QWidget
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt

def get_available_cameras(max_cameras=5):
    available = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return available

class CameraSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор камеры")
        self.setFixedSize(320, 300)

        self.selected_index = None
        self.camera_index = 0
        self.cap = None

        self.label = QLabel("Загрузка камеры...", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(300, 225)

        self.combo = QComboBox(self)
        self.cameras = get_available_cameras()
        for index in self.cameras:
            self.combo.addItem(f"Камера {index}", index)
        self.combo.currentIndexChanged.connect(self.change_camera)

        self.btn_ok = QPushButton("ОК", self)
        self.btn_ok.clicked.connect(self.on_accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.combo)
        layout.addWidget(self.label)
        layout.addWidget(self.btn_ok)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.change_camera(0)

    def change_camera(self, index):
        if self.cap:
            self.cap.release()
        self.camera_index = self.combo.itemData(index)
        self.cap = cv2.VideoCapture(self.camera_index)

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (300, 225))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                image = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(image))

    def on_accept(self):
        self.selected_index = self.camera_index
        self.close()

    def get_selected_camera_index(self):
        self.exec()
        if self.cap:
            self.cap.release()
        return self.selected_index


