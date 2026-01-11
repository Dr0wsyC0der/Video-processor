"""
Модуль обработки видео для отслеживания объектов.

Класс VideoProcessor обрабатывает видеофайлы и кадры с камеры,
применяет фильтры изображения и отслеживает объекты с использованием
компьютерного зрения.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List

from new_dot_sorter import MegaSorter

# Включение поддержки OpenCL для ускорения обработки
cv2.ocl.setUseOpenCL(True)


class VideoProcessor:
    """
    Класс для обработки видео и отслеживания объектов.

    Обрабатывает видеофайлы и кадры с камеры, применяет фильтры изображения
    (яркость, контраст, резкость, шумоподавление) и отслеживает объекты
    с помощью алгоритмов компьютерного зрения.
    """

    def __init__(self, plot) -> None:
        """
        Инициализация обработчика видео.

        Args:
            plot: Объект для визуализации данных в 3D
        """
        self.cap: Optional[cv2.VideoCapture] = None
        self.flag: int = 0
        self.x1: int = 0
        self.y1: int = 0
        self.x2: int = 0
        self.y2: int = 0
        self.cords2: List[List[int]] = []
        self.home_pos: List[List] = []
        self.crop_coords: Optional[List[int]] = None
        self.old: int = 0
        self.new: int = 0
        self.plot = plot
        self.brightness: float = 0
        self.contrast: float = 1
        self.sharpness: float = 0
        self.noises: float = 0

    def load_video(self, file_path: str) -> None:
        """
        Загружает видеофайл для обработки.

        Args:
            file_path: Путь к видеофайлу
        """
        self.cap = cv2.VideoCapture(file_path)

    def get_params(
        self,
        brightness: float,
        contrast: float,
        sharpness: float,
        noise: float
    ) -> None:
        """
        Устанавливает параметры фильтров обработки изображения.

        Args:
            brightness: Значение яркости
            contrast: Значение контрастности
            sharpness: Значение резкости
            noise: Значение уровня шумоподавления
        """
        self.brightness = brightness
        self.contrast = int(contrast)
        self.sharpness = sharpness
        self.noises = noise

    def get_crop_coords(self, crop_coords: Optional[List[int]]) -> None:
        """
        Устанавливает координаты области обрезки кадра.

        Args:
            crop_coords: Список координат [y1, y2, x1, x2] или None
        """
        self.crop_coords = crop_coords

    def apply_filters(self, frame: np.ndarray) -> np.ndarray:
        """
        Применяет фильтры к кадру изображения.

        Применяет медианный фильтр для шумоподавления, регулировку яркости
        и контрастности, а также фильтр резкости.

        Args:
            frame: Входной кадр изображения

        Returns:
            Обработанный кадр изображения
        """
        # Медианный фильтр для шумоподавления
        if self.noises > 0:
            kernel_size = int(self.noises)
            if kernel_size % 2 == 0:
                kernel_size += 1
            frame = cv2.medianBlur(frame, kernel_size)

        # Регулировка яркости и контрастности
        frame = cv2.convertScaleAbs(
            frame,
            alpha=self.contrast if self.contrast > 0 else 1,
            beta=self.brightness
        )

        # Фильтр резкости
        if self.sharpness > 0:
            base_kernel = np.array([
                [0, -1, 0],
                [-1, 5 + self.sharpness * 2, -1],
                [0, -1, 0]
            ])
            frame = cv2.filter2D(frame, -1, base_kernel)

        return frame

    def process_frame(
        self,
        frame: Optional[np.ndarray] = None,
        ret: Optional[bool] = None
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Обрабатывает один кадр видео для отслеживания объектов.

        Если frame и ret не указаны, кадр считывается из загруженного видео.
        Обрабатывает кадр, применяет фильтры, определяет объекты и отслеживает
        их перемещение.

        Args:
            frame: Кадр изображения (опционально, если None - считывается из видео)
            ret: Флаг успешности чтения кадра (опционально)

        Returns:
            Кортеж (обработанный_кадр, маска) или None в случае ошибки
        """
        # Считывание кадра из видео, если не передан
        if frame is None and ret is None:
            if self.cap is None or not self.cap.isOpened():
                return None
            ret, frame = self.cap.read()
            if not ret or frame is None:
                return None

            # Применение обрезки, если задана
            if self.crop_coords is not None:
                y1, y2, x1, x2 = self.crop_coords
                frame = frame[y1:y2, x1:x2]

            # Изменение размера кадра
            frame = cv2.resize(frame, (960, 960), interpolation=cv2.INTER_LINEAR)
            print(frame.shape[:2])

        frame_cords: List[Tuple[float, float]] = []

        # Применение фильтров
        frame = self.apply_filters(frame)

        # Преобразование в серый цвет и создание бинарной маски
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Морфологическая операция для улучшения маски
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)

        # Фаза обучения: определение области отслеживания (первые 13 кадров)
        if self.flag <= 12:
            tracked_centers: List[Tuple[int, int]] = []
            circles = cv2.HoughCircles(
                mask,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=100,
                param1=100,
                param2=40,
                minRadius=150,
                maxRadius=400
            )

            if circles is not None:
                circles = np.uint16(np.around(circles))
                x, y, r = circles[0][0]
                square_side = int(r * np.sqrt(2) / 2)
                x1, y1 = x - square_side, y - square_side
                x2, y2 = x + square_side, y + square_side

                # Поиск контуров в области круга
                contours, _ = cv2.findContours(
                    mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                for cnt in contours:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])

                        if x1 < cx < x2 and y1 < cy < y2:
                            tracked_centers.append((cx, cy))

                # Визуализация области отслеживания
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                for cx, cy in tracked_centers:
                    cv2.circle(frame, (cx, cy), 3, (0, 255, 255), -1)

                # Сохранение данных для обучения
                self.cords2.append([len(tracked_centers), x1, y1, x2, y2])
                self.home_pos.append([len(tracked_centers), tracked_centers])
                self.flag += 1

        # Выбор оптимальной области отслеживания после обучения
        if self.flag == 13:
            self.cords2.sort(key=lambda x: x[0], reverse=True)
            self.x1 = self.cords2[0][1]
            self.y1 = self.cords2[0][2]
            self.x2 = self.cords2[0][3]
            self.y2 = self.cords2[0][4]

        # Фаза отслеживания объектов
        if self.flag == 13:
            contours, _ = cv2.findContours(
                mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )

            # Визуализация области отслеживания
            if self.flag:
                cv2.rectangle(
                    frame, (self.x1, self.y1), (self.x2, self.y2), (255, 0, 0), 5
                )

            # Определение координат объектов
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 8:
                    x, y, w, h = cv2.boundingRect(cnt)
                    frame_cords.append((x + (w / 2), y + (h / 2)))
                    cv2.rectangle(
                        frame, (x, y), (x + w, y + h), (0, 255, 255), 3
                    )

            # Сопоставление и сортировка точек
            sorter = MegaSorter(self.home_pos, frame_cords)
            if not ret:
                sorter.reset_all_data()
            self.old, self.new = sorter.process()
            self.plot.update_data(self.old, self.new)

        # Преобразование в RGB для отображения
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame, mask

    def pre_process_frame(
        self, frame: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Предварительная обработка кадра для предпросмотра.

        Применяет фильтры и создает бинарную маску для отображения
        в режиме предпросмотра.

        Args:
            frame: Входной кадр изображения

        Returns:
            Кортеж (обработанный_кадр, маска)
        """
        frame = self.apply_filters(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if gray is not None and gray.size > 0:
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            _, mask = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(
                mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )

            # Визуализация контуров
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 8:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(
                        frame, (x, y), (x + w, y + h), (0, 255, 255), 3
                    )

        return frame, mask

    def return_default_params(self, full_reset: bool = True) -> None:
        """
        Сбрасывает параметры обработчика к значениям по умолчанию.

        Args:
            full_reset: Если True, также сбрасывает параметры фильтров
        """
        self.cap = None
        self.flag = 0
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.cords2 = []
        self.home_pos = []
        self.old = 0
        self.new = 0

        if full_reset:
            self.brightness = 0
            self.contrast = 1
            self.sharpness = 0
            self.noises = 0
