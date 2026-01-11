"""
Модуль графического интерфейса для обработки видео.

Предоставляет класс VideoProcessorWindow для управления интерфейсом
приложения обработки видео с возможностью выбора источника (файл/камера),
настройки фильтров и визуализации результатов.
"""

import sys
import os
from typing import Optional, TYPE_CHECKING
from pathlib import Path
import cv2
import numpy as np

from PyQt6 import uic

# Получение базовой директории проекта
BASE_DIR = Path(__file__).parent.parent
RESOURCES_DIR = BASE_DIR / "resources"
UI_DIR = RESOURCES_DIR / "ui"
IMAGES_DIR = RESOURCES_DIR / "images"
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QLabel
)
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QCloseEvent, QMouseEvent
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer

from camera import CameraSelectionDialog
from autoParams import AutoParams

if TYPE_CHECKING:
    from video_processor import VideoProcessor
    import threading
    import numpy.typing as npt

class VideoProcessorWindow(QMainWindow):
    """
    Главное окно приложения для обработки видео.

    Предоставляет графический интерфейс для работы с видео:
    - Выбор источника (файл или камера)
    - Настройка фильтров (яркость, контраст, резкость, шумоподавление)
    - Предпросмотр и обработка видео
    - Выбор области обрезки
    """

    def __init__(
        self,
        processor: "VideoProcessor",
        vispy_thread: "threading.Thread"
    ) -> None:
        """
        Инициализация главного окна приложения.

        Args:
            processor: Экземпляр класса VideoProcessor для обработки видео
            vispy_thread: Поток для визуализации в 3D
        """
        super().__init__()
        self.vispy_thread = vispy_thread
        self.timer = QTimer()
        self.current_frame_index = 0
        self.total_frames = 0
        self.total_seconds = 0
        self.cap = None
        self.fps = None
        self.dont_show_msg = False
        ui_path = UI_DIR / "ui1.ui"
        uic.loadUi(str(ui_path), self)
        old_frame = self.findChild(QLabel, "vid_frame")
        self.frame = ImageLabel()
        self.frame.setObjectName(old_frame.objectName())
        self.frame.setGeometry(old_frame.geometry())
        self.frame.setParent(old_frame.parent())
        self.frame.setFrameShape(old_frame.frameShape())
        self.frame.setFrameShadow(old_frame.frameShadow())
        self.frame.setLineWidth(old_frame.lineWidth())
        self.frame.show()
        self.frame.selectionFinished.connect(self.update_frame)
        old_frame.hide()

        self.move(100, 100)
        self.processor = processor
        self.video_path = None
        self.is_paused = False
        self.frame_is_resized = False
        self.actual_frame = None
        self.update_flag = False
        self.cam_cap = None
        self.new_size = None
        self.selected_index = None
        self.sharpness_value = 0
        self.contrast_value = 1
        self.brightness_value = 1
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

    def setup_custom_logic(self) -> None:
        """
        Настройка пользовательской логики интерфейса.

        Инициализирует подключения сигналов к слотам, настраивает слайдеры,
        кнопки и другие элементы интерфейса.
        """
        # Фреймы
        image_path = IMAGES_DIR / "vid_pic.png"
        pixmap = QPixmap(str(image_path))
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
        self.start_over.clicked.connect(self.default_start_over)
        self.start_over.setStyleSheet(self.button_style_red)
        self.start_over.hide()
        self.auto_filter_check.clicked.connect(self.change_slider_state)


        #Слайдеры
        self.brt_slide.valueChanged.connect(self.update_brightness)
        self.cntr_slide.valueChanged.connect(self.update_contrast)
        self.cntr_slide.setValue(1)
        self.shrrp_slide.valueChanged.connect(self.update_sharpness)
        self.noise_slide.valueChanged.connect(self.update_noise)
        self.source_selector.currentTextChanged.connect(self.update_select_btn)
        self.brt_slide.setRange(-100, 100)
        self.cntr_slide.setRange(-15, 15)
        self.shrrp_slide.setRange(0, 100)
        self.noise_slide.setRange(0, 100)
        self.video_scroll.valueChanged.connect(self.video_rewind)
        self.video_scroll.hide()
        #Прочее
        self.set_default_slider_values()
        self.video_time.hide()
        self.sliders_is_active(False)

    def openFileDialog(self) -> None:
        """
        Открывает диалоговое окно для выбора видеофайла.

        Позволяет пользователю выбрать видеофайл, загружает его
        и инициализирует интерфейс для работы с видео.
        """
        if self.source_selector.currentText() == 'Файл':
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
                self.sliders_is_active(True)
                self.set_default_slider_values()
                self.frame.drawingSwitch(True)
                self.file.setStyleSheet(self.button_style_green)
                self.video_path = file_path
                self.video_time.show()
                self.video_scroll.show()
                if not self.dont_show_msg:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("Выбор фрагмента")
                    msg.setText("Добавлена возможность выбора фрагмента на изображении.\nВы можете сделать это удержав левую кнопку мыши и растянув прямоугольник.")
                    checkbox = QCheckBox("Больше не показывать")
                    msg.setCheckBox(checkbox)
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.exec()
                    if checkbox.isChecked():
                        self.dont_show_msg = True

    def show_frame(self, index):
        if self.cap and self.cap.isOpened():
            self.video_scroll.setValue(0)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ret, frame = self.cap.read()
            self.frame.actual_frame = frame.copy()
            frame = cv2.resize(frame, (960, 540), interpolation=cv2.INTER_LINEAR)
            self.actual_frame = frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
            # mask = cv2.adaptiveThreshold(gray, 255,
            #                              cv2.ADAPTIVE_THRESH_MEAN_C,
            #                              cv2.THRESH_BINARY_INV, 11, 2)

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
            if self.start.text() == 'Остановить обработку':
                self.frame.new_size = None
                self.timer.stop()
                self.cam_cap = cv2.VideoCapture(self.selected_index)
                self.timer.timeout.connect(self.update_frame_cam)
                self.timer.start(30)
                self.start.setStyleSheet(self.button_style_green)
                self.processor.return_default_params()
                self.start.setText('Начать обработку')
            else:
                self.start.setStyleSheet(self.button_style_red)
                self.start.setText('Остановить обработку')
                self.cam_cap = cv2.VideoCapture(self.selected_index)
                self.timer.timeout.connect(lambda: self.update_frame_cam(True))
                self.timer.start(30)
        elif self.source_selector.currentText() == 'Файл':
            if not self.cap or not hasattr(self.processor, 'load_video') or not hasattr(self.processor, 'process_frame'):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Ошибка")
                msg.setText("Не выбрано видео или отсутствует обработчик!")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return
            self.frame.drawingSwitch(False)
            self.video_scroll.setValue(0)
            self.current_frame_index = 0
            self.pause.show()
            self.pause.setText("Pause")
            self.processor.load_video(self.video_path)
            self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value, self.noise_value)
            self.mask.hide()
            self.frame.resize(520, 520)
            self.start_over.show()
            try:
                self.timer.timeout.disconnect(self.play_video_frame)
            except TypeError:
                pass

            self.timer.timeout.connect(self.update_processed_frame)
            self.timer.start(33)

    def  display_frame(self, index):
        if not self.cap or index >= self.total_frames:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = self.apply_filters(frame)
        crop_coords = self.frame.new_size
        if crop_coords is not None:
            y1, y2, x1, x2 = crop_coords
            frame = frame[y1:y2, x1:x2]
            print(y1, y2, x1, x2)
        if not hasattr(self.__class__.display_frame, "already_run"):
            self.actual_frame = frame
            self.__class__.display_frame.already_run = True

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # изменение размера после обрезки
        frame = cv2.resize(frame, (960, 540), interpolation=cv2.INTER_LINEAR)

        # _, mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # mask = cv2.adaptiveThreshold(gray, 255,
        #                                  cv2.ADAPTIVE_THRESH_MEAN_C,
        #                                  cv2.THRESH_BINARY_INV, 11, 2)
        kernel = np.ones((3, 3), np.uint8)
        # mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=1)

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
        self.brt_value.setText(str(round(value, 2)))
        self.brightness_value = value
        self.update_frame()

    def update_contrast(self, value):
        self.cntr_value.setText(str(round(value, 2)))
        self.contrast_value = value
        self.update_frame()

    def update_sharpness(self, value):
        self.shrrp_value.setText(str(round(value, 2)))
        self.sharpness_value = value*0.1
        self.update_frame()

    def update_noise(self, value):
        self.noise_val.setText(str(round(value, 2)))
        self.noise_value = value
        self.update_frame()
    def update_select_btn(self, text=None):
        if text is None:
            text = self.source_selector.currentText()
        if text == 'Камера':
            self.file.setText("Файл выбран")
            self.start.setStyleSheet(self.button_style_green)
            self.file.setStyleSheet(self.button_style_green)
            dialog = CameraSelectionDialog()
            self.selected_index = dialog.get_selected_camera_index()
            self.cam_cap = cv2.VideoCapture(self.selected_index)
            self.timer.timeout.connect(self.update_frame_cam)
            self.timer.start(30)

            self.frame.drawingSwitch(True)

        elif text=='Файл':
            self.file.setText('ВЫБРАТЬ ФАЙЛ')
            self.file.setStyleSheet(self.button_style_red)


    def set_default_slider_values(self, brt = 1, cntr = 1, shrrp = 0, noise = 0):
        self.brt_slide.setValue(int(brt))
        self.cntr_slide.setValue(int(cntr))
        self.shrrp_slide.setValue(int(shrrp))
        self.noise_slide.setValue(int(noise))

        self.brt_value.setText(str(brt))
        self.cntr_value.setText(str(cntr))
        self.shrrp_value.setText(str(shrrp))
        self.noise_val.setText(str(noise))

        self.update_brightness(brt)
        self.update_contrast(cntr)
        self.update_sharpness(shrrp)
        self.update_noise(noise)


        print(self.brightness_value, self.contrast_value, self.sharpness_value, self.noise_value)
        self.update_frame()

    def update_processed_frame(self):
        if self.current_frame_index >= self.total_frames:
            self.timer.stop()
            self.reset_video_state()
            self.return_default_params()
            self.processor.return_default_params()
            return

        try:
            self.processor.get_crop_coords(self.frame.new_size)
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
            image_path = IMAGES_DIR / "vid_pic.png"
            pixmap = QPixmap(str(image_path))
            self.frame.setPixmap(pixmap)
            self.processor.return_default_params()

    def reset_video_state(self):
        self.sliders_is_active(False)
        self.current_frame_index = 0
        self.video_time.setText("00:00 / 00:00")
        self.file.setText("ВЫБРАТЬ ФАЙЛ")
        self.file.setStyleSheet(self.button_style_red)
        self.set_default_slider_values()
        self.processor.running = False


    def update_frame_cam(self, flag = False):
        ret, frame = self.cam_cap.read()
        mask = None
        frame_2 = None


        if ret:
            try:
                if not flag:
                    self.frame.actual_frame = frame.copy()
                    crop_coords = self.frame.new_size
                    if crop_coords is not None:
                        y1, y2, x1, x2 = crop_coords
                        frame = frame[y1:y2, x1:x2]
                    frame_2, mask = self.processor.pre_process_frame(frame)
                    self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value,
                                              self.noise_value)
                    frame_2 = cv2.cvtColor(frame_2, cv2.COLOR_BGR2RGB)
                    self.frame.actual_frame = frame.copy()
                elif flag:
                    crop_coords = self.frame.new_size
                    if crop_coords is not None:
                        y1, y2, x1, x2 = crop_coords
                        frame = frame[y1:y2, x1:x2]
                    frame_2, mask = self.processor.process_frame(frame, ret)
                    self.processor.get_params(self.brightness_value, self.contrast_value, self.sharpness_value,
                                              self.noise_value)


                if frame_2 is not None:
                    h, w, ch = frame_2.shape
                    image = QImage(frame_2.data, w, h, ch * w, QImage.Format.Format_RGB888)
                    self.frame.setPixmap(QPixmap.fromImage(image))
                else:
                    self.return_default_params()

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
        image_path = IMAGES_DIR / "vid_pic.png"
        pixmap = QPixmap(str(image_path))
        self.frame.resize(520, 280)
        self.frame.setPixmap(pixmap)
        self.mask.show()
        self.mask.setPixmap(pixmap)
        self.pause.hide()
        self.start_over.hide()
        self.video_time.hide()
        self.video_scroll.hide()

    def default_start_over(self):
        self.timer.stop()
        self.video_scroll.setValue(0)
        self.frame.new_size = None
        self.update_frame()
        self.is_paused = False
        self.cam_cap = None
        self.selected_index = None
        self.frame.resize(520, 280)
        self.mask.show()
        self.pause.hide()
        self.start_over.hide()
        self.processor.return_default_params(False)
        self.frame.drawingSwitch(True)


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

    def sliders_is_active(self, status):
        self.brt_slide.setEnabled(status)
        self.cntr_slide.setEnabled(status)
        self.shrrp_slide.setEnabled(status)
        self.noise_slide.setEnabled(status)

    def change_slider_state(self):
        self.set_default_slider_values()
        status = not self.brt_slide.isEnabled()
        self.default_btn.setEnabled(status)
        self.sliders_is_active(status)
        if self.auto_filter_check.isChecked():
            if self.actual_frame is not None:
                auto = AutoParams(self.actual_frame)
                best = auto.get_params()
                print(best)
                self.set_default_slider_values(best["brightness"]*255, best["contrast"], 0, best["noise"])


    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Обработчик события закрытия окна.

        Args:
            event: Событие закрытия окна
        """
        sys.exit()

class ImageLabel(QLabel):
    """
    Виджет для отображения изображения с возможностью выбора области.

    Расширенный QLabel, который позволяет пользователю выбирать область
    на изображении путем перетаскивания мыши для обрезки кадра.
    """

    selectionFinished = pyqtSignal()

    def __init__(self, parent=None) -> None:
        """
        Инициализация виджета изображения.

        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.setScaledContents(True)
        self.drawing_enabled = False
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.new_size = None
        self.actual_frame = None
        self.new_frame = None

    def drawingSwitch(self, enabled: bool) -> None:
        """
        Переключает режим выбора области.

        Args:
            enabled: Если True, включает режим выбора области
        """
        self.drawing_enabled = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Обработчик нажатия кнопки мыши.

        Args:
            event: Событие нажатия мыши
        """
        if not self.drawing_enabled:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Обработчик перемещения мыши.

        Args:
            event: Событие перемещения мыши
        """
        if not self.drawing_enabled:
            return

        if self.drawing:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Обработчик отпускания кнопки мыши.

        Args:
            event: Событие отпускания мыши
        """
        if not self.drawing_enabled:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.end_point = event.position().toPoint()
            self.crop_to_selection()
            self.update()
            self.selectionFinished.emit()
            self.clear_selection()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.drawing_enabled and self.start_point and self.end_point:
            painter = QPainter(self)
            pen = QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(QRect(self.start_point, self.end_point))


    def clear_selection(self) -> None:
        """
        Очищает выбранную область.

        Сбрасывает начальную и конечную точки выбора
        и обновляет виджет.
        """
        self.start_point = None
        self.end_point = None
        self.update()

    def crop_to_selection(self) -> None:
        """
        Вычисляет координаты выбранной области для обрезки.

        Преобразует координаты выбранной области из координат виджета
        в координаты изображения с учетом масштабирования.
        """
        # x1 = min(self.start_point.x(), self.end_point.x())
        # y1 = min(self.start_point.y(), self.end_point.y())
        # x2 = max(self.start_point.x(), self.end_point.x())
        # y2 = max(self.start_point.y(), self.end_point.y())
        #
        # x1, y1 = max(0, x1), max(0, y1)
        # x2, y2 = min(1920, x2), min(1080, y2)
        #
        # if x2 > x1 and y2 > y1:
        #     self.new_size = [y1, y2, x1, x2]
        #     print(self.new_size)
        # else:
        #     print("Некорректная область выделения")
        print(type(self.actual_frame))
        if self.actual_frame is None:
            return

        label_w = self.width()
        label_h = self.height()
        img_h, img_w, _ = self.actual_frame.shape

        scale_x = img_w / label_w
        scale_y = img_h / label_h

        x1 = int(min(self.start_point.x(), self.end_point.x()) * scale_x)
        y1 = int(min(self.start_point.y(), self.end_point.y()) * scale_y)
        x2 = int(max(self.start_point.x(), self.end_point.x()) * scale_x)
        y2 = int(max(self.start_point.y(), self.end_point.y()) * scale_y)

        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img_w, x2), min(img_h, y2)

        if x2 > x1 and y2 > y1:
            self.new_size = [y1, y2, x1, x2]
            print("Область обрезки (в пикселях):", self.new_size)
        else:
            print("Некорректная область выделения")




