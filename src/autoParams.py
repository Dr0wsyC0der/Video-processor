"""
Модуль автоматической настройки параметров обработки изображения.

Использует библиотеку Optuna для оптимизации параметров фильтров
(яркость, контраст, шумоподавление) с целью получения наилучшего
результата сегментации объектов.
"""

import cv2
import numpy as np
import optuna
from typing import Dict, Any

import numpy.typing as npt


class AutoParams:
    """
    Класс для автоматической настройки параметров обработки изображения.

    Использует оптимизацию через Optuna для поиска оптимальных значений
    параметров фильтров изображения на основе качества сегментации.
    """

    def __init__(self, frame: npt.NDArray[np.uint8]) -> None:
        """
        Инициализация оптимизатора параметров.

        Args:
            frame: Исходный кадр изображения для оптимизации
        """
        self.frame = frame
        print(self.frame.shape[:2])

    def evaluate_params(
        self,
        brightness: float,
        contrast: float,
        noise: int
    ) -> int:
        """
        Оценивает качество сегментации для заданных параметров.

        Применяет фильтры с указанными параметрами к изображению,
        выполняет бинаризацию и подсчитывает количество "хороших"
        контуров (с площадью в определенном диапазоне).

        Args:
            brightness: Значение яркости (от -0.3921 до 0.3921)
            contrast: Значение контрастности (от 0.5 до 2.0)
            noise: Значение уровня шумоподавления (от 0 до 5)

        Returns:
            Количество хороших контуров (чем больше, тем лучше)
        """
        # Изменение размера для ускорения обработки
        self.frame = cv2.resize(self.frame, (960, 540), interpolation=cv2.INTER_LINEAR)
        img = self.frame.copy()

        # Применение яркости и контрастности
        img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness * 255)

        # Применение шумоподавления
        if noise > 0:
            kernel_size = int(noise)
            if kernel_size % 2 == 0:
                kernel_size += 1
            img = cv2.medianBlur(img, kernel_size)

        # Преобразование в серый цвет
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Бинаризация методом Оцу
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cv2.imshow("bb", binary)

        # Поиск контуров
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Подсчет "хороших" контуров (с площадью в диапазоне 10-200)
        good_contours = [cnt for cnt in contours if 10 < cv2.contourArea(cnt) < 200]

        return len(good_contours)

    def objective(self, trial: optuna.Trial) -> float:
        """
        Целевая функция для оптимизации Optuna.

        Предлагает значения параметров и оценивает качество результата.
        Цель - максимизировать количество хороших контуров.

        Args:
            trial: Объект trial от Optuna

        Returns:
            Отрицательное значение оценки (для минимизации)
        """
        brightness = trial.suggest_float("brightness", -0.3921, 0.3921)
        contrast = trial.suggest_float("contrast", 0.5, 2.0)
        noise = trial.suggest_int("noise", 0, 5)

        score = self.evaluate_params(brightness, contrast, noise)
        # Возвращаем отрицательное значение для минимизации
        return -score

    def get_params(self, n_trials: int = 50) -> Dict[str, Any]:
        """
        Находит оптимальные параметры обработки изображения.

        Использует Optuna для оптимизации параметров фильтров
        через заданное количество итераций.

        Args:
            n_trials: Количество итераций оптимизации

        Returns:
            Словарь с оптимальными параметрами:
            - brightness: оптимальная яркость
            - contrast: оптимальная контрастность
            - noise: оптимальный уровень шумоподавления
        """
        study = optuna.create_study()
        study.optimize(self.objective, n_trials=n_trials)
        return study.best_params
