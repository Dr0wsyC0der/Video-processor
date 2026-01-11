"""
Главный модуль приложения для обработки видео.

Модуль инициализирует графический интерфейс, обработчик видео и визуализацию
в 3D для отслеживания объектов на видео.
"""

import sys
import threading
from typing import NoReturn

from PyQt6 import QtWidgets

from video_processor import VideoProcessor
from plt import Live3DPlot
from gui import VideoProcessorWindow


def start_vispy_application(plot: Live3DPlot) -> None:
    """
    Запускает приложение vispy для визуализации в отдельном потоке.

    Args:
        plot: Экземпляр класса Live3DPlot для визуализации данных
    """
    plot.run()


def main() -> NoReturn:
    """
    Главная функция приложения.

    Инициализирует все компоненты системы:
    - 3D визуализацию в отдельном потоке
    - Обработчик видео
    - Графический интерфейс пользователя
    """
    # Создание и запуск 3D визуализации в отдельном потоке
    plot = Live3DPlot()
    vispy_thread = threading.Thread(
        target=start_vispy_application,
        args=(plot,),
        name="VispyThread",
        daemon=True
    )
    vispy_thread.start()

    # Создание обработчика видео
    processor = VideoProcessor(plot)

    # Создание и запуск графического интерфейса
    app = QtWidgets.QApplication(sys.argv)
    main_window = VideoProcessorWindow(processor, vispy_thread)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
