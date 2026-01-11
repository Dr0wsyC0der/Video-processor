"""
Модуль для выбора камеры.

Предоставляет диалоговое окно для выбора доступной камеры
с предпросмотром изображения с выбранной камеры.
"""

import cv2
from typing import List, Optional

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt


def get_available_cameras(max_cameras: int = 5) -> List[int]:
    """
    Получает список доступных камер.

    Проверяет наличие доступных камер, начиная с индекса 0
    до указанного максимального количества.

    Args:
        max_cameras: Максимальное количество камер для проверки

    Returns:
        Список индексов доступных камер
    """
    available: List[int] = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return available


class CameraSelectionDialog(QDialog):
    """
    Диалоговое окно для выбора камеры.

    Позволяет пользователю выбрать камеру из списка доступных
    с предпросмотром изображения в реальном времени.
    """

    def __init__(self, parent=None) -> None:
        """
        Инициализация диалогового окна выбора камеры.

        Args:
            parent: Родительское окно
        """
        super().__init__(parent)
        self.setWindowTitle("Выбор камеры")
        self.setFixedSize(320, 300)

        self.selected_index: Optional[int] = None
        self.camera_index: int = 0
        self.cap: Optional[cv2.VideoCapture] = None

        # Создание элементов интерфейса
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

        # Настройка layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.combo)
        layout.addWidget(self.label)
        layout.addWidget(self.btn_ok)

        # Таймер для обновления изображения с камеры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.change_camera(0)

    def change_camera(self, index: int) -> None:
        """
        Переключает камеру на выбранную в комбобоксе.

        Args:
            index: Индекс выбранного элемента в комбобоксе
        """
        if self.cap:
            self.cap.release()
        self.camera_index = self.combo.itemData(index)
        self.cap = cv2.VideoCapture(self.camera_index)

    def update_frame(self) -> None:
        """
        Обновляет изображение с камеры в предпросмотре.

        Считывает кадр с текущей камеры и отображает его
        в виджете предпросмотра.
        """
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (300, 225))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                image = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(image))

    def on_accept(self) -> None:
        """
        Обработчик нажатия кнопки ОК.

        Сохраняет индекс выбранной камеры и закрывает диалог.
        """
        self.selected_index = self.camera_index
        self.close()

    def get_selected_camera_index(self) -> Optional[int]:
        """
        Получает индекс выбранной камеры.

        Отображает диалоговое окно и возвращает индекс
        выбранной пользователем камеры.

        Returns:
            Индекс выбранной камеры или None
        """
        self.exec()
        if self.cap:
            self.cap.release()
        return self.selected_index
