import sys
import cv2
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QImage, QPixmap


class Ui_Video_Processor:
    def __init__(self, processor):
        self.processor = processor
        self.sharpness_value = 0
        self.contrast_value = 0
        self.brightness_value = 0
        self.noise_value = 0
        self.video_path = None

    def setupUi(self, Video_Processor):
        Video_Processor.setObjectName("Video_Processor")
        Video_Processor.resize(800, 600)
        Video_Processor.setStyleSheet("background-color: rgb(216, 250, 255); color: black;")

        button_style_red = """
        QPushButton {
            background-color: rgb(255, 0, 0);
            color: white;
            border-radius: 5px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: rgb(200, 0, 0);
        }
        """

        button_style_white = """
        QPushButton {
            background-color: rgb(255, 255, 255);
            color: black;
            border-radius: 5px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: rgb(230, 230, 230);
        }
        """

        self.button_style_green = """
        QPushButton {
            background-color: rgb(0, 255, 0);
            color: black;
            border-radius: 5px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: rgb(0, 200, 0);
        }
        """

        self.centralwidget = QtWidgets.QWidget(parent=Video_Processor)
        self.centralwidget.setObjectName("centralwidget")

        self.frame = QtWidgets.QLabel(parent=self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(10, 9, 521, 281))
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.frame.setObjectName("frame")
        self.frame.setStyleSheet("background-color: white")
        self.frame.setScaledContents(True)

        self.mask = QtWidgets.QLabel(parent=self.centralwidget)
        self.mask.setGeometry(QtCore.QRect(10, 310, 250, 200))
        self.mask.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.mask.setObjectName("mask")
        self.mask.setScaledContents(True)

        self.video_scroll = QtWidgets.QSlider(parent=self.centralwidget)
        self.video_scroll.setGeometry(QtCore.QRect(10, 560, 771, 20))
        self.video_scroll.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.video_scroll.setObjectName("video_scroll")
        self.video_scroll.valueChanged.connect(self.update_frame_by_slider)

        self.brt_slide = QtWidgets.QSlider(parent=self.centralwidget)
        self.brt_slide.setGeometry(QtCore.QRect(550, 80, 160, 16))
        self.brt_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.brt_slide.setObjectName("brt_slide")

        self.cntr_slide = QtWidgets.QSlider(parent=self.centralwidget)
        self.cntr_slide.setGeometry(QtCore.QRect(550, 130, 160, 16))
        self.cntr_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.cntr_slide.setObjectName("cntr_slide")

        self.shrrp_slide = QtWidgets.QSlider(parent=self.centralwidget)
        self.shrrp_slide.setGeometry(QtCore.QRect(550, 180, 160, 16))
        self.shrrp_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.shrrp_slide.setObjectName("shrrp_slide")

        self.graph = QtWidgets.QFrame(parent=self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(280, 310, 250, 200))
        self.graph.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.graph.setObjectName("graph")

        self.start = QtWidgets.QPushButton(parent=self.centralwidget)
        self.start.setGeometry(QtCore.QRect(550, 350, 221, 41))
        self.start.setStyleSheet(button_style_red)
        self.start.setObjectName("start")
        self.start.clicked.connect(self.start_processing)

        self.brightness = QtWidgets.QLabel(parent=self.centralwidget)
        self.brightness.setGeometry(QtCore.QRect(720, 80, 60, 13))
        self.brightness.setObjectName("brightness")

        self.contrast = QtWidgets.QLabel(parent=self.centralwidget)
        self.contrast.setGeometry(QtCore.QRect(720, 130, 60, 13))
        self.contrast.setObjectName("contrast")

        self.sharpness = QtWidgets.QLabel(parent=self.centralwidget)
        self.sharpness.setGeometry(QtCore.QRect(720, 180, 60, 13))
        self.sharpness.setObjectName("sharpness")

        self.label_6 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(550, 60, 101, 16))
        self.label_6.setObjectName("label_6")

        self.label_7 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(550, 110, 101, 16))
        self.label_7.setObjectName("label_7")

        self.label_8 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(550, 160, 101, 16))
        self.label_8.setObjectName("label_8")

        self.noise_check = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.noise_check.setGeometry(QtCore.QRect(550, 210, 101, 17))
        self.noise_check.setObjectName("noise_check")

        self.noise_slide = QtWidgets.QSlider(parent=self.centralwidget)
        self.noise_slide.setGeometry(QtCore.QRect(550, 240, 160, 20))
        self.noise_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.noise_slide.setObjectName("noise_slide")

        self.noise = QtWidgets.QLabel(parent=self.centralwidget)
        self.noise.setGeometry(QtCore.QRect(720, 240, 60, 13))
        self.noise.setObjectName("noise")

        self.default_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.default_btn.setGeometry(QtCore.QRect(550, 270, 221, 25))
        self.default_btn.setStyleSheet(button_style_white)
        self.default_btn.setObjectName("default_btn")
        self.set_default_slider_values()
        self.default_btn.clicked.connect(self.set_default_slider_values)

        self.file = QtWidgets.QPushButton(parent=self.centralwidget)
        self.file.setGeometry(QtCore.QRect(550, 310, 221, 25))
        self.file.setStyleSheet(button_style_red)
        self.file.setObjectName("file")
        self.file.clicked.connect(self.openFileDialog)

        self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(550, 10, 221, 31))
        self.label_4.setObjectName("label_4")

        self.video_time = QtWidgets.QLabel(parent=self.centralwidget)
        self.video_time.setGeometry(QtCore.QRect(380, 530, 100, 13))
        self.video_time.setObjectName("video_time")

        Video_Processor.setCentralWidget(self.centralwidget)
        self.retranslateUi(Video_Processor)
        QtCore.QMetaObject.connectSlotsByName(Video_Processor)

        self.brt_slide.valueChanged.connect(self.update_brightness)
        self.cntr_slide.valueChanged.connect(self.update_contrast)
        self.shrrp_slide.valueChanged.connect(self.update_sharpness)
        self.noise_slide.valueChanged.connect(self.update_noise)

        self.cntr_slide.setValue(1)

        self.brt_slide.setRange(-255, 255)
        self.cntr_slide.setRange(-15, 15)
        self.shrrp_slide.setRange(0, 100)
        self.noise_slide.setRange(0, 100)

        self.cntr_slide.setSingleStep(2)

        self.cap = None
        self.total_frames = 0
        self.current_frame_index = 0
        self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.play_video_frame)

    def retranslateUi(self, Video_Processor):
        _translate = QtCore.QCoreApplication.translate
        Video_Processor.setWindowTitle(_translate("Video_Processor", "Video Processor"))
        self.start.setText(_translate("Video_Processor", "Начать обработку"))
        self.brightness.setText(_translate("Video_Processor", "0"))
        self.contrast.setText(_translate("Video_Processor", "0"))
        self.sharpness.setText(_translate("Video_Processor", "0"))
        self.label_6.setText(_translate("Video_Processor", "Яркость"))
        self.label_7.setText(_translate("Video_Processor", "Контрастность"))
        self.label_8.setText(_translate("Video_Processor", "Резкость"))
        self.noise_check.setText(_translate("Video_Processor", "Удалить шум"))
        self.noise.setText(_translate("Video_Processor", "0"))
        self.default_btn.setText(_translate("Video_Processor", "По умолчанию"))
        self.file.setText(_translate("Video_Processor", "ВЫБРАТЬ ФАЙЛ"))
        self.label_4.setText(_translate("Video_Processor", "                             ФИЛЬТРЫ"))
        self.video_time.setText(_translate("Video_Processor", "00:00 / 00:00"))

    def openFileDialog(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None,
            "Выберите видеофайл",
            "",
            "Видео файлы (*.mp4 *.avi *.mov *.mkv);;Все файлы (*)"
        )
        if file_path:
            valid_extensions = (".mp4", ".avi", ".mov", ".mkv")
            if not file_path.lower().endswith(valid_extensions):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Ошибка")
                msg.setText("Выбранный файл не является видео.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return

            self.cap = cv2.VideoCapture(file_path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_scroll.setMaximum(self.total_frames - 1)
            self.current_frame_index = 0
            self.show_frame(self.current_frame_index)
            self.file.setText("Файл выбран")
            self.file.setStyleSheet(self.button_style_green)
            self.video_path = file_path

    def show_frame(self, index):
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_img)
                self.frame.setPixmap(pixmap)
                self.update_time_label(index)

    def update_time_label(self, frame_index):
        fps = self.cap.get(cv2.CAP_PROP_FPS) if self.cap else 25
        total_seconds = self.total_frames / fps
        current_seconds = frame_index / fps

        def format_time(secs):
            mins = int(secs) // 60
            secs = int(secs) % 60
            return f"{mins:02}:{secs:02}"

        self.video_time.setText(f"{format_time(current_seconds)} / {format_time(total_seconds)}")

    def update_frame_by_slider(self):
        index = self.video_scroll.value()
        self.current_frame_index = index
        self.show_frame(index)

    def play_video_frame(self):
        if self.cap and self.cap.isOpened() and self.current_frame_index < self.total_frames:
            self.show_frame(self.current_frame_index)
            self.video_scroll.setValue(self.current_frame_index)
            self.current_frame_index += 1
        else:
            self.timer.stop()

    def start_processing(self):
        if not self.cap or not hasattr(self.processor, 'load_video') or not hasattr(self.processor, 'process_frame'):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Ошибка")
            msg.setText("Не выбрано видео или отсутствует обработчик!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

        self.processor.load_video(self.video_path)
        self.processor.running = True  # если у тебя такой флаг используется

        try:
            self.timer.timeout.disconnect(self.play_video_frame)
        except TypeError:
            pass

        self.timer.timeout.connect(self.update_processed_frame)
        self.timer.start(33)  # ≈30 FPS

    def update_brightness(self, value):
        self.brightness.setText(str(value))
        self.brightness_value = value

    def update_contrast(self, value):
        self.contrast.setText(str(value))
        self.contrast_value = value

    def update_sharpness(self, value):
        self.sharpness.setText(str(value))
        self.sharpness_value = value

    def update_noise(self, value):
        self.noise.setText(str(value))
        self.noise_value = value

    def set_default_slider_values(self):
        self.brt_slide.setValue(0)
        self.cntr_slide.setValue(1)
        self.shrrp_slide.setValue(1)
        self.noise_slide.setValue(1)

        self.brightness.setText("0")
        self.contrast.setText("1")
        self.sharpness.setText("1")
        self.noise.setText("1")

    def update_processed_frame(self):
        frame, mask = self.processor.process_frame()
        if frame is not None:
            # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_img)
            self.frame.setPixmap(pixmap)
        if mask is not None:
            qimg = QImage(mask.data, mask.shape[1], mask.shape[0], mask.shape[1], QImage.Format.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimg)
            self.mask.setPixmap(pixmap)
        else:
            self.timer.stop()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Video_Processor = QtWidgets.QMainWindow()
    ui = Ui_Video_Processor()
    ui.setupUi(Video_Processor)
    Video_Processor.show()
    sys.exit(app.exec())
