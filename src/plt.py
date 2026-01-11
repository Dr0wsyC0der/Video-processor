"""
Модуль для визуализации данных в 3D.

Класс Live3DPlot создает интерактивную 3D визуализацию перемещений
объектов, отображая данные в виде триангулированной поверхности.
"""

import numpy as np
import numpy.typing as npt
from typing import List, Tuple, Optional

from vispy import app, scene
from vispy.color import ColorArray
from scipy.spatial import Delaunay
import matplotlib.cm as cm


class Live3DPlot:
    """
    Класс для интерактивной 3D визуализации данных.

    Создает и обновляет 3D визуализацию перемещений объектов в реальном
    времени, отображая данные в виде цветной триангулированной поверхности.
    """

    def __init__(self) -> None:
        """
        Инициализация 3D визуализации.

        Создает окно с 3D сценой и настраивает камеру для отображения
        триангулированной поверхности.
        """
        self.old_points: npt.NDArray[np.float64] = np.array([])
        self.new_points: npt.NDArray[np.float64] = np.array([])

        # Создание сцены
        self.canvas = scene.SceneCanvas(
            keys='interactive',
            size=(800, 600),
            show=True
        )
        self.canvas.native.move(900, 100)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'turntable'

        # Создание триангулированной поверхности
        self.mesh = scene.visuals.Mesh()
        self.view.add(self.mesh)

    def update_data(
        self,
        old_points: List[Tuple[float, float]],
        new_points: List[Tuple[float, float]]
    ) -> None:
        """
        Обновляет данные для визуализации.

        Принимает старые и новые координаты точек, вычисляет смещения
        и обновляет 3D поверхность.

        Args:
            old_points: Список старых координат точек (x, y)
            new_points: Список новых координат точек (x, y)
        """
        self.old_points = np.array(old_points)
        self.new_points = np.array(new_points)

        # Вычисление смещений
        self.dx = self.new_points[:, 0] - self.old_points[:, 0]
        self.dy = self.new_points[:, 1] - self.old_points[:, 1]

        # Вычисление высоты (Z) как расстояние перемещения
        self.Z = np.sqrt(self.dx ** 2 + self.dy ** 2) * 10

        self.update_surface()
        self.update_camera()  # Автоматическое центрирование камеры

    def update_surface(self, param: int = 0) -> None:
        """
        Обновляет триангулированную поверхность.

        Создает триангуляцию Делоне для точек и обновляет визуализацию
        с цветовой картой, основанной на значениях высоты.

        Args:
            param: Параметр управления (1 - сброс данных)
        """
        if param == 1:
            self.old_points = np.array([])
            self.new_points = np.array([])

        if self.old_points.size == 0 or self.new_points.size == 0:
            return

        x_old, y_old = self.old_points.T

        # Триангуляция Делоне
        tri = Delaunay(np.c_[x_old, y_old])

        # Создание вершин с координатами (x, y, z)
        vertices = np.c_[x_old, y_old, self.Z]
        faces = tri.simplices

        # Выбор цветовой карты
        cmap = cm.get_cmap("viridis")

        # Вычисление цветов граней на основе средней высоты
        face_colors = cmap(self.Z[faces].mean(axis=1) / self.Z.max())
        colors = ColorArray(face_colors[:, :3])

        # Обновление визуализации
        self.mesh.set_data(vertices, faces=faces, face_colors=colors)

    def update_camera(self) -> None:
        """
        Обновляет позицию камеры для оптимального обзора.

        Вычисляет центр точек и оптимальную дистанцию для камеры,
        чтобы все точки были видны в поле зрения.
        """
        if self.old_points.size == 0 or self.new_points.size == 0:
            return

        # Нахождение границ точек
        x_min, y_min = self.old_points.min(axis=0)
        x_max, y_max = self.old_points.max(axis=0)
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2

        # Вычисление оптимальной дистанции
        range_x = x_max - x_min
        range_y = y_max - y_min
        max_range = max(range_x, range_y)
        optimal_distance = max_range * 2  # Настройка дистанции

        # Установка позиции камеры
        self.view.camera.center = (center_x, center_y, self.Z.max() / 2)
        self.view.camera.distance = optimal_distance

    def run(self) -> None:
        """
        Запускает приложение vispy.

        Запускает главный цикл обработки событий vispy для отображения
        визуализации.
        """
        app.run()

    def default(self) -> None:
        """
        Сбрасывает визуализацию к начальному состоянию.

        Очищает сцену и переинициализирует компоненты визуализации.
        """
        self.view.scene.clear()
        self.__init__()
