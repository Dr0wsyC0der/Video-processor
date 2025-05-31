# import sys
# import cv2
# import numpy as np
# from PyQt6 import QtCore, QtGui, QtWidgets
# from PyQt6.QtWidgets import QFileDialog, QMessageBox
# from PyQt6.QtGui import QImage, QPixmap
# from camera import CameraSelectionDialog
#
#
# class Ui_Video_Processor:
#     def __init__(self, processor):
#         self.processor = processor
#         self.sharpness_value = 0
#         self.contrast_value = 1
#         self.brightness_value = 0
#         self.noise_value = 0
#         self.video_path = None
#         self.is_paused = False
#         self.cam_cap = None
#         self.selected_index = None
#
#     def setupUi(self, Video_Processor):
#         Video_Processor.setObjectName("Video_Processor")
#         Video_Processor.resize(800, 600)
#         Video_Processor.move(100, 100)
#         Video_Processor.setStyleSheet("background-color: rgb(216, 250, 255); color: black;")
#
#         self.button_style_red = """
#         QPushButton {
#             background-color: rgb(255, 0, 0);
#             color: white;
#             border-radius: 5px;
#             padding: 6px;
#         }
#         QPushButton:hover {
#             background-color: rgb(200, 0, 0);
#         }
#         """
#
#         button_style_white = """
#         QPushButton {
#             background-color: rgb(255, 255, 255);
#             color: black;
#             border-radius: 5px;
#             padding: 6px;
#         }
#         QPushButton:hover {
#             background-color: rgb(230, 230, 230);
#         }
#         """
#
#         self.button_style_green = """
#         QPushButton {
#             background-color: rgb(0, 255, 0);
#             color: black;
#             border-radius: 5px;
#             padding: 6px;
#         }
#         QPushButton:hover {
#             background-color: rgb(0, 200, 0);
#         }
#         """
#
#         self.centralwidget = QtWidgets.QWidget(parent=Video_Processor)
#         self.centralwidget.setObjectName("centralwidget")
#
#         self.frame = QtWidgets.QLabel(parent=self.centralwidget)
#         self.frame.setGeometry(QtCore.QRect(10, 9, 521, 281))
#         self.frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
#         self.frame.setObjectName("frame")
#         self.frame.setStyleSheet("background-color: white")
#         self.frame.setScaledContents(True)
#         pixmap = QPixmap('vid_pic.png')
#         self.frame.setPixmap(pixmap)
#
#         self.mask = QtWidgets.QLabel(parent=self.centralwidget)
#         self.mask.setGeometry(QtCore.QRect(10, 310, 521, 250))
#         self.mask.setFrameShape(QtWidgets.QFrame.Shape.Box)
#         self.mask.setObjectName("mask")
#         self.mask.setScaledContents(True)
#
#         self.brt_slide = QtWidgets.QSlider(parent=self.centralwidget)
#         self.brt_slide.setGeometry(QtCore.QRect(550, 80, 160, 16))
#         self.brt_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
#         self.brt_slide.setObjectName("brt_slide")
#
#         self.cntr_slide = QtWidgets.QSlider(parent=self.centralwidget)
#         self.cntr_slide.setGeometry(QtCore.QRect(550, 130, 160, 16))
#         self.cntr_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
#         self.cntr_slide.setObjectName("cntr_slide")
#
#         self.shrrp_slide = QtWidgets.QSlider(parent=self.centralwidget)
#         self.shrrp_slide.setGeometry(QtCore.QRect(550, 180, 160, 16))
#         self.shrrp_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
#         self.shrrp_slide.setObjectName("shrrp_slide")
#
#
#         self.start = QtWidgets.QPushButton(parent=self.centralwidget)
#         self.start.setGeometry(QtCore.QRect(550, 350, 221, 41))
#         self.start.setStyleSheet(self.button_style_red)
#         self.start.setObjectName("start")
#         self.start.clicked.connect(self.start_processing)
#
#         self.brightness = QtWidgets.QLabel(parent=self.centralwidget)
#         self.brightness.setGeometry(QtCore.QRect(720, 80, 60, 13))
#         self.brightness.setObjectName("brightness")
#
#         self.contrast = QtWidgets.QLabel(parent=self.centralwidget)
#         self.contrast.setGeometry(QtCore.QRect(720, 130, 60, 13))
#         self.contrast.setObjectName("contrast")
#
#         self.sharpness = QtWidgets.QLabel(parent=self.centralwidget)
#         self.sharpness.setGeometry(QtCore.QRect(720, 180, 60, 13))
#         self.sharpness.setObjectName("sharpness")
#
#         self.label_6 = QtWidgets.QLabel(parent=self.centralwidget)
#         self.label_6.setGeometry(QtCore.QRect(550, 60, 101, 16))
#         self.label_6.setObjectName("label_6")
#
#         self.label_7 = QtWidgets.QLabel(parent=self.centralwidget)
#         self.label_7.setGeometry(QtCore.QRect(550, 110, 101, 16))
#         self.label_7.setObjectName("label_7")
#
#         self.label_8 = QtWidgets.QLabel(parent=self.centralwidget)
#         self.label_8.setGeometry(QtCore.QRect(550, 160, 101, 16))
#         self.label_8.setObjectName("label_8")
#
#         self.label_9 = QtWidgets.QLabel(parent=self.centralwidget)
#         self.label_9.setGeometry(QtCore.QRect(550, 210, 101, 16))
#         self.label_9.setObjectName("label_6")
#
#         self.noise_slide = QtWidgets.QSlider(parent=self.centralwidget)
#         self.noise_slide.setGeometry(QtCore.QRect(550, 230, 160, 20))
#         self.noise_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
#         self.noise_slide.setObjectName("noise_slide")
#
#         self.noise = QtWidgets.QLabel(parent=self.centralwidget)
#         self.noise.setGeometry(QtCore.QRect(720, 240, 60, 13))
#         self.noise.setObjectName("noise")
#
#         self.default_btn = QtWidgets.QPushButton(parent=self.centralwidget)
#         self.default_btn.setGeometry(QtCore.QRect(550, 270, 221, 25))
#         self.default_btn.setStyleSheet(button_style_white)
#         self.default_btn.setObjectName("default_btn")
#         self.set_default_slider_values()
#         self.default_btn.clicked.connect(self.set_default_slider_values)
#
#         self.pause = QtWidgets.QPushButton(parent=self.centralwidget)
#         self.pause.setGeometry(QtCore.QRect(550, 430, 221, 41))
#         self.pause.setStyleSheet(self.button_style_red)
#         self.pause.setObjectName("pause")
#         self.pause.clicked.connect(self.toggle_pause)
#         self.pause.hide()
#
#         self.file = QtWidgets.QPushButton(parent=self.centralwidget)
#         self.file.setGeometry(QtCore.QRect(550, 310, 221, 25))
#         self.file.setStyleSheet(self.button_style_red)
#         self.file.setObjectName("file")
#         self.file.clicked.connect(self.openFileDialog)
#
#         self.source_selector = QtWidgets.QComboBox(parent=self.centralwidget)
#         self.source_selector.setGeometry(QtCore.QRect(550, 400, 221, 25))
#         self.source_selector.addItems(["Файл", "Камера"])
#         self.source_selector.setObjectName("source_selector")
#
#         self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
#         self.label_4.setGeometry(QtCore.QRect(550, 10, 221, 31))
#         self.label_4.setObjectName("label_4")
#
#         self.video_time = QtWidgets.QLabel(parent=self.centralwidget)
#         self.video_time.setGeometry(QtCore.QRect(620, 530, 100, 13))
#         self.video_time.setObjectName("video_time")
#
#         Video_Processor.setCentralWidget(self.centralwidget)
#         self.retranslateUi(Video_Processor)
#         QtCore.QMetaObject.connectSlotsByName(Video_Processor)
#
#         self.brt_slide.valueChanged.connect(self.update_brightness)
#         self.cntr_slide.valueChanged.connect(self.update_contrast)
#         self.shrrp_slide.valueChanged.connect(self.update_sharpness)
#         self.noise_slide.valueChanged.connect(self.update_noise)
#         self.source_selector.currentTextChanged.connect(self.update_select_btn)
#
#         self.cntr_slide.setValue(1)
#
#         self.brt_slide.setRange(-100, 100)
#         self.cntr_slide.setRange(-15, 15)
#         self.shrrp_slide.setRange(0, 100)
#         self.noise_slide.setRange(0, 100)
#
#         self.cntr_slide.setSingleStep(2)
#
#         self.cap = None
#         self.total_frames = 0
#         self.current_frame_index = 0
#         self.timer = QtCore.QTimer()
#         self.set_default_slider_values()
#
#     def retranslateUi(self, Video_Processor):
#         _translate = QtCore.QCoreApplication.translate
#         Video_Processor.setWindowTitle(_translate("Video_Processor", "Video Processor"))
#         self.start.setText(_translate("Video_Processor", "Начать обработку"))
#         self.brightness.setText(_translate("Video_Processor", "0"))
#         self.contrast.setText(_translate("Video_Processor", "0"))
#         self.sharpness.setText(_translate("Video_Processor", "0"))
#         self.label_6.setText(_translate("Video_Processor", "Яркость"))
#         self.label_7.setText(_translate("Video_Processor", "Контрастность"))
#         self.label_8.setText(_translate("Video_Processor", "Резкость"))
#         self.label_9.setText(_translate("Video_Processor", "Шум"))
#         self.noise.setText(_translate("Video_Processor", "0"))
#         self.default_btn.setText(_translate("Video_Processor", "По умолчанию"))
#         self.file.setText(_translate("Video_Processor", "ВЫБРАТЬ ФАЙЛ"))
#         self.label_4.setText(_translate("Video_Processor", "                             ФИЛЬТРЫ"))
#         self.video_time.setText(_translate("Video_Processor", "00:00 / 00:00"))
#         self.pause.setText(_translate("Video_Processor", 'Пауза'))
#
#     def openFileDialog(self):
#         if self.source_selector.currentText()=='Файл':
#             file_dialog = QFileDialog()
#             file_path, _ = file_dialog.getOpenFileName(
#                 None,
#                 "Выберите видеофайл",
#                 "",
#                 "Видео файлы (*.mp4 *.avi *.mov *.mkv);;Все файлы (*)"
#             )
#             if file_path:
#                 valid_extensions = (".mp4", ".avi", ".mov", ".mkv")
#                 if not file_path.lower().endswith(valid_extensions):
#                     msg = QMessageBox()
#                     msg.setIcon(QMessageBox.Icon.Warning)
#                     msg.setWindowTitle("Ошибка")
#                     msg.setText("Выбранный файл не является видео.")
#                     msg.setStandardButtons(QMessageBox.StandardButton.Ok)
#                     msg.exec()
#                     return
#
#                 self.cap = cv2.VideoCapture(file_path)
#                 self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
#                 self.current_frame_index = 0
#                 self.show_frame(self.current_frame_index)
#                 self.file.setText("Файл выбран")
#                 self.file.setStyleSheet(self.button_style_green)
#                 self.video_path = file_path
#
#     def show_frame(self, index):
#         if self.cap and self.cap.isOpened():
#             self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
#             ret, frame = self.cap.read()
#             if ret:
#                 frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 h, w, ch = frame_rgb.shape
#                 bytes_per_line = ch * w
#                 qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
#                 pixmap = QPixmap.fromImage(qt_img)
#                 self.frame.setPixmap(pixmap)
#                 self.update_time_label(index)
#
#     def update_time_label(self, frame_index):
#         fps = self.cap.get(cv2.CAP_PROP_FPS) if self.cap else 25
#         total_seconds = self.total_frames / fps
#         current_seconds = frame_index / fps
#
#         def format_time(secs):
#             mins = int(secs) // 60
#             secs = int(secs) % 60
#             return f"{mins:02}:{secs:02}"
#
#         self.video_time.setText(f"{format_time(current_seconds)} / {format_time(total_seconds)}")
#
#     def play_video_frame(self):
#         if self.cap and self.cap.isOpened() and self.current_frame_index < self.total_frames:
#             self.show_frame(self.current_frame_index)
#             self.current_frame_index += 1
#         else:
#             self.timer.stop()
#
#     def start_processing(self):
#         self.pause.show()
#         if self.source_selector.currentText() == 'Камера':
#             self.cam_cap = cv2.VideoCapture(self.selected_index)
#             self.timer.timeout.connect(lambda: self.update_frame_cam(True))
#             self.timer.start(30)
#             self.processor.running = True
#         elif self.source_selector.currentText() == 'Файл':
#             if not self.cap or not hasattr(self.processor, 'load_video') or not hasattr(self.processor, 'process_frame'):
#             # if not self.cap and not self.is_paused:
#                 msg = QMessageBox()
#                 msg.setIcon(QMessageBox.Icon.Warning)
#                 msg.setWindowTitle("Ошибка")
#                 msg.setText("Не выбрано видео или отсутствует обработчик!")
#                 msg.setStandardButtons(QMessageBox.StandardButton.Ok)
#                 msg.exec()
#                 return
#             self.processor.load_video(self.video_path)
#             self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value, self.noise_value)
#             try:
#                 self.timer.timeout.disconnect(self.play_video_frame)
#             except TypeError:
#                 pass
#
#             self.timer.timeout.connect(self.update_processed_frame)
#             self.timer.start(33)  # ≈30 FPS
#
#     def update_frame(self):
#         if not self.cap or self.current_frame_index >= self.total_frames:
#             return
#
#         self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_index)
#         ret, frame = self.cap.read()
#
#         if not ret:
#             return
#
#         frame = self.apply_filters(frame)
#
#         if frame is not None:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             h, w, ch = frame.shape
#             bytes_per_line = ch * w
#             qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
#             pixmap = QPixmap.fromImage(qt_img)
#             self.frame.setPixmap(pixmap)
#
#         self.update_time_label(self.current_frame_index)
#
#     def apply_filters(self, frame):
#         frame = cv2.convertScaleAbs(frame, alpha=self.contrast_value, beta=self.brightness_value)
#
#         shr = self.sharpness_value
#         if shr > 0:
#             base_kernel = np.array([[0, -1, 0],
#                                     [-1, 5 + shr * 2, -1],
#                                     [0, -1, 0]])
#             frame = cv2.filter2D(frame, -1, base_kernel)
#
#         ns = self.noise_value
#         if ns > 0:
#             kernel_size = int(ns)
#             if kernel_size % 2 == 0:
#                 kernel_size += 1
#             frame = cv2.medianBlur(frame, kernel_size)
#
#         return frame
#
#     def update_brightness(self, value):
#         self.brightness.setText(str(value))
#         self.brightness_value = value
#         self.update_frame()
#
#     def update_contrast(self, value):
#         self.contrast.setText(str(value))
#         self.contrast_value = value*0.5
#         self.update_frame()
#
#     def update_sharpness(self, value):
#         self.sharpness.setText(str(value))
#         self.sharpness_value = value*0.1
#         self.update_frame()
#
#     def update_noise(self, value):
#         self.noise.setText(str(value))
#         self.noise_value = value
#         self.update_frame()
#     def update_select_btn(self, text=None):
#         if text is None:
#             text = self.source_selector.currentText()
#         if text == 'Камера':
#             self.file.setText("Файл выбран")
#             self.file.setStyleSheet(self.button_style_green)
#             dialog = CameraSelectionDialog()
#             self.selected_index = dialog.get_selected_camera_index()
#             self.cam_cap = cv2.VideoCapture(self.selected_index)
#             self.timer.timeout.connect(self.update_frame_cam)
#             self.timer.start(30)
#
#         elif text=='Файл':
#             self.file.setText('ВЫБРАТЬ ФАЙЛ')
#             self.file.setStyleSheet(self.button_style_red)
#
#
#     def set_default_slider_values(self):
#         self.brt_slide.setValue(0)
#         self.cntr_slide.setValue(1)
#         self.shrrp_slide.setValue(0)
#         self.noise_slide.setValue(0)
#
#         self.brightness.setText("0")
#         self.contrast.setText("1")
#         self.sharpness.setText("0")
#         self.noise.setText("0")
#
#     def update_processed_frame(self):
#         if self.current_frame_index >= self.total_frames:
#             # Если видео закончилось, остановим таймер
#             self.timer.stop()
#             self.reset_video_state()
#             self.return_defaut_params()# Восстановить состояние после окончания видео
#             return
#
#         try:
#             frame, mask = self.processor.process_frame()  # Обработка кадра
#             if frame is not None:
#                 h, w, ch = frame.shape
#                 bytes_per_line = ch * w
#                 qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
#                 pixmap = QPixmap.fromImage(qt_img)
#                 self.frame.setPixmap(pixmap)
#
#             if mask is not None:
#                 qimg = QImage(mask.data, mask.shape[1], mask.shape[0], mask.shape[1], QImage.Format.Format_Grayscale8)
#                 pixmap = QPixmap.fromImage(qimg)
#                 self.mask.setPixmap(pixmap)
#
#         except Exception as e:
#             print(f"Ошибка при обработке кадра: {e}")
#             self.timer.stop()
#             self.video_path = None
#             self.update_select_btn('Файл')
#             pixmap = QPixmap('vid_pic.png')
#             self.frame.setPixmap(pixmap)
#             self.processor.return_default_params()
#
#     def reset_video_state(self):
#         self.current_frame_index = 0
#         self.video_time.setText("00:00 / 00:00")
#         self.file.setText("Выбрать файл")
#         self.file.setStyleSheet(self.button_style_white)
#         self.set_default_slider_values()
#         self.processor.running = False
#
#
#     def update_frame_cam(self, flag = False):
#         ret, frame = self.cam_cap.read()
#         mask = None
#         frame_2 = None
#
#         if ret:
#             try:
#                 if not flag:
#                     frame_2 = self.processor.pre_process_frame(frame)
#                     self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value,
#                                               self.noise_value)
#                 elif flag:
#                     frame_2, mask = self.processor.process_frame2(frame, ret)
#                     self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value,
#                                               self.noise_value)
#
#                 if frame_2 is not None:
#                     frame_2 = cv2.cvtColor(frame_2, cv2.COLOR_BGR2RGB)
#                     h, w, ch = frame_2.shape
#                     image = QImage(frame_2.data, w, h, ch * w, QImage.Format.Format_RGB888)
#                     self.frame.setPixmap(QPixmap.fromImage(image))
#                 else:
#                     self.return_defaut_params()
#
#                 if mask is not None:
#                     qimg = QImage(mask.data, mask.shape[1], mask.shape[0], mask.shape[1],
#                                   QImage.Format.Format_Grayscale8)
#                     pixmap = QPixmap.fromImage(qimg)
#                     self.mask.setPixmap(pixmap)
#
#             except Exception as e:
#                 print(f"Ошибка при обработке кадра: {e}")
#
#     def return_default_params(self):
#         self.video_path = None
#         self.is_paused = False
#         self.cam_cap = None
#         self.selected_index = None
#         pixmap = QPixmap('vid_pic.png')
#         self.frame.setPixmap(pixmap)
#
#     def toggle_pause(self):
#         # self.is_paused = True
#         # if self.timer.isActive():
#         #     self.timer.stop()
#         #     self.pause.setText("Продолжить")
#         # else:
#         #     self.timer.start(30)
#         #     self.pause.setText("Пауза")
#         pass
#
#



from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtCore, QtGui, QtWidgets
import sys
import cv2
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QImage, QPixmap
from camera import CameraSelectionDialog
import numpy as np

class VideoProcessorWindow(QMainWindow):
    def __init__(self, processor):
        super().__init__()
        self.timer = QtCore.QTimer()
        self.current_frame_index = 0
        self.total_frames = 0
        self.total_seconds = 0
        self.cap = None
        self.fps = None
        uic.loadUi("ui1.ui", self)
        self.move(100, 100)
        self.processor = processor
        self.video_path = None
        self.is_paused = False
        self.cam_cap = None
        self.selected_index = None
        self.sharpness_value = 0
        self.contrast_value = 1
        self.brightness_value = 0
        self.noise_value = 0
        #Стили кнопок
        self.button_style_red = """
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

        self.button_style_white = """
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

        self.setup_custom_logic()

    def setup_custom_logic(self):
        #Фреймы
        pixmap = QPixmap('vid_pic.png')
        self.frame.setPixmap(pixmap)
        self.mask.setPixmap(pixmap)
        #Кнопки и окна
        self.start.clicked.connect(self.start_processing)
        self.start.setStyleSheet(self.button_style_red)
        self.default_btn.clicked.connect(self.set_default_slider_values)
        self.default_btn.setStyleSheet(self.button_style_red)
        self.pause.clicked.connect(self.toggle_pause)
        self.pause.setStyleSheet(self.button_style_red)
        self.pause.hide()
        self.file.clicked.connect(self.openFileDialog)
        self.file.setStyleSheet(self.button_style_red)
        #Слайдеры
        self.brt_slide.valueChanged.connect(self.update_brightness)
        self.cntr_slide.valueChanged.connect(self.update_contrast)
        self.cntr_slide.setValue(1)
        self.shrrp_slide.valueChanged.connect(self.update_sharpness)
        self.noise_slide.valueChanged.connect(self.update_noise)
        self.source_selector.currentTextChanged.connect(self.update_select_btn)
        self.brt_slide.setRange(-100, 100)
        self.cntr_slide.setRange(-15, 15)
        self.cntr_slide.setSingleStep(2)
        self.shrrp_slide.setRange(0, 100)
        self.noise_slide.setRange(0, 100)
        self.video_scroll.valueChanged.connect(self.video_rewind)
        self.video_scroll.hide()
        #Прочее
        self.set_default_slider_values()
        self.video_time.hide()

    def openFileDialog(self):
        if self.source_selector.currentText()=='Файл':
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                None,
                "Выберите видеофайл",
                "",
                "Видео файлы (*.mp4 *.avi *.mov *.mkv);;Все файлы (*)"
            )
            if file_path:
                valid_formats = (".mp4", ".avi", ".mov", ".mkv")
                if not file_path.lower().endswith(valid_formats):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setWindowTitle("Ошибка")
                    msg.setText("Выбранный файл не является видео.")
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.exec()
                    return

                self.cap = cv2.VideoCapture(file_path)
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.total_seconds = int(self.total_frames / self.fps)
                self.video_scroll.setMaximum(self.total_seconds)
                self.show_frame(self.current_frame_index)
                self.file.setText("Файл выбран")
                self.file.setStyleSheet(self.button_style_green)
                self.video_path = file_path
                self.video_time.show()
                self.video_scroll.show()

    def show_frame(self, index):
        if self.cap and self.cap.isOpened():
            self.video_scroll.setValue(0)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ret, frame = self.cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_img)
                self.frame.setPixmap(pixmap)
                self.update_time_label(index)
            if mask is not None:
                qimg = QImage(mask.data, mask.shape[1], mask.shape[0], mask.shape[1], QImage.Format.Format_Grayscale8)
                pixmap = QPixmap.fromImage(qimg)
                self.mask.setPixmap(pixmap)

    def update_time_label(self, frame_index):
        current_seconds = frame_index / self.fps

        def format_time(secs):
            mins = int(secs) // 60
            secs = int(secs) % 60
            return f"{mins:02}:{secs:02}"

        self.video_time.setText(f"{format_time(current_seconds)} / {format_time(self.total_seconds)}")

    def update_scroll(self, frame_index):
        current_seconds = frame_index / self.fps
        self.video_scroll.setValue(int(current_seconds))

    def start_processing(self):
        if self.source_selector.currentText() == 'Камера':
            self.cam_cap = cv2.VideoCapture(self.selected_index)
            self.timer.timeout.connect(lambda: self.update_frame_cam(True))
            self.timer.start(30)
            self.processor.running = True
        elif self.source_selector.currentText() == 'Файл':
            if not self.cap or not hasattr(self.processor, 'load_video') or not hasattr(self.processor, 'process_frame'):
            # if not self.cap and not self.is_paused:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Ошибка")
                msg.setText("Не выбрано видео или отсутствует обработчик!")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return

            self.video_scroll.setValue(0)
            self.current_frame_index = 0
            self.pause.show()
            self.pause.setText("Pause")
            self.processor.load_video(self.video_path)
            self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value, self.noise_value)
            try:
                self.timer.timeout.disconnect(self.play_video_frame)
            except TypeError:
                pass

            self.timer.timeout.connect(self.update_processed_frame)
            self.timer.start(33)

    def display_frame(self, index):
        if not self.cap or index >= self.total_frames:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self.cap.read()

        if not ret:
            return

        frame = self.apply_filters(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_img)
            self.frame.setPixmap(pixmap)
        if mask is not None:
            qimg = QImage(mask.data, mask.shape[1], mask.shape[0], mask.shape[1], QImage.Format.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimg)
            self.mask.setPixmap(pixmap)

        self.update_time_label(index)

    def update_frame(self):
        self.display_frame(self.current_frame_index)

    def play_video_frame(self):
        if self.cap and self.cap.isOpened() and self.current_frame_index < self.total_frames:
            self.display_frame(self.current_frame_index)
            self.current_frame_index += 1
        else:
            self.timer.stop()

    def apply_filters(self, frame):
        frame = cv2.convertScaleAbs(frame, alpha=self.contrast_value, beta=self.brightness_value)

        shr = self.sharpness_value
        if shr > 0:
            base_kernel = np.array([[0, -1, 0],
                                    [-1, 5 + shr * 2, -1],
                                    [0, -1, 0]])
            frame = cv2.filter2D(frame, -1, base_kernel)

        ns = self.noise_value
        if ns > 0:
            kernel_size = int(ns)
            if kernel_size % 2 == 0:
                kernel_size += 1
            frame = cv2.medianBlur(frame, kernel_size)

        return frame

    def update_brightness(self, value):
        self.brt_value.setText(str(value))
        self.brightness_value = value
        self.update_frame()

    def update_contrast(self, value):
        self.cntr_value.setText(str(value))
        self.contrast_value = value*0.5
        self.update_frame()

    def update_sharpness(self, value):
        self.shrrp_value.setText(str(value))
        self.sharpness_value = value*0.1
        self.update_frame()

    def update_noise(self, value):
        self.noise_val.setText(str(value))
        self.noise_value = value
        self.update_frame()
    def update_select_btn(self, text=None):
        if text is None:
            text = self.source_selector.currentText()
        if text == 'Камера':
            self.file.setText("Файл выбран")
            self.file.setStyleSheet(self.button_style_green)
            dialog = CameraSelectionDialog()
            self.selected_index = dialog.get_selected_camera_index()
            self.cam_cap = cv2.VideoCapture(self.selected_index)
            self.timer.timeout.connect(self.update_frame_cam)
            self.timer.start(30)

        elif text=='Файл':
            self.file.setText('ВЫБРАТЬ ФАЙЛ')
            self.file.setStyleSheet(self.button_style_red)


    def set_default_slider_values(self):
        self.brt_slide.setValue(0)
        self.cntr_slide.setValue(1)
        self.shrrp_slide.setValue(0)
        self.noise_slide.setValue(0)

        self.brt_value.setText("0")
        self.cntr_value.setText("1")
        self.shrrp_value.setText("0")
        self.noise_val.setText("0")

    def update_processed_frame(self):
        if self.current_frame_index >= self.total_frames:
            self.timer.stop()
            self.reset_video_state()
            self.return_default_params()
            return

        try:
            frame, mask = self.processor.process_frame()  # Обработка кадра
            if frame is not None:
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_img)
                self.frame.setPixmap(pixmap)

            if mask is not None:
                qimg = QImage(mask.data, mask.shape[1], mask.shape[0], mask.shape[1], QImage.Format.Format_Grayscale8)
                pixmap = QPixmap.fromImage(qimg)
                self.mask.setPixmap(pixmap)

            self.update_time_label(self.current_frame_index)
            self.update_scroll(self.current_frame_index)
            self.current_frame_index += 1



        except Exception as e:
            print(f"Ошибка при обработке кадра: {e}")
            self.timer.stop()
            self.video_path = None
            self.update_select_btn('Файл')
            pixmap = QPixmap('vid_pic.png')
            self.frame.setPixmap(pixmap)
            self.processor.return_default_params()

    def reset_video_state(self):
        self.current_frame_index = 0
        self.video_time.setText("00:00 / 00:00")
        self.file.setText("Выбрать файл")
        self.file.setStyleSheet(self.button_style_white)
        self.set_default_slider_values()
        self.processor.running = False


    def update_frame_cam(self, flag = False):
        ret, frame = self.cam_cap.read()
        mask = None
        frame_2 = None

        if ret:
            try:
                if not flag:
                    frame_2, mask = self.processor.pre_process_frame(frame)
                    self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value,
                                              self.noise_value)
                elif flag:
                    frame_2, mask = self.processor.process_frame2(frame, ret)
                    self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value,
                                              self.noise_value)

                if frame_2 is not None:
                    frame_2 = cv2.cvtColor(frame_2, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame_2.shape
                    image = QImage(frame_2.data, w, h, ch * w, QImage.Format.Format_RGB888)
                    self.frame.setPixmap(QPixmap.fromImage(image))
                else:
                    self.return_defaut_params()

                if mask is not None:
                    qimg = QImage(mask.data, mask.shape[1], mask.shape[0], mask.shape[1],
                                  QImage.Format.Format_Grayscale8)
                    pixmap = QPixmap.fromImage(qimg)
                    self.mask.setPixmap(pixmap)

            except Exception as e:
                print(f"Ошибка при обработке кадра: {e}")

    def return_default_params(self):
        self.video_path = None
        self.is_paused = False
        self.cam_cap = None
        self.selected_index = None
        pixmap = QPixmap('vid_pic.png')
        self.frame.setPixmap(pixmap)
        self.mask.setPixmap(pixmap)
        self.pause.hide()
        self.video_time.hide()
        self.video_scroll.hide()

    def toggle_pause(self):
        if not self.cap:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.timer.stop()
            self.pause.setText("Play")
        else:
            self.timer.start(33)
            self.pause.setText("Pause")

    def video_rewind(self):
        if self.cap and self.cap.isOpened() and not self.timer.isActive():
            current_time = self.video_scroll.value()
            self.current_frame_index = self.fps*current_time
            self.update_frame()




