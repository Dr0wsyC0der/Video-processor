import numpy as np
from vispy import app, scene
from vispy.color import ColorArray
from scipy.spatial import Delaunay
import matplotlib.cm as cm

class Live3DPlot:
    def __init__(self):
        self.old_points = np.array([])
        self.new_points = np.array([])

        # Создаём сцену
        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
        self.canvas.native.move(900, 100)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'turntable'

        # Создаём триангулированную поверхность
        self.mesh = scene.visuals.Mesh()
        self.view.add(self.mesh)

    def update_data(self, old_points, new_points):
        self.old_points = np.array(old_points)
        self.new_points = np.array(new_points)
        self.dx = self.new_points[:, 0] - self.old_points[:, 0]
        self.dy = self.new_points[:, 1] - self.old_points[:, 1]
        self.Z = np.sqrt(self.dx ** 2 + self.dy ** 2)*10
        self.update_surface()
        self.update_camera()  # Автоматическое центрирование камеры

    def update_surface(self, param = 0):
        if param==1:
            self.old_points = np.array([])
            self.new_points = np.array([])
        if self.old_points.size == 0 or self.new_points.size == 0:
            return

        x_old, y_old = self.old_points.T

        # Триангуляция точек
        tri = Delaunay(np.c_[x_old, y_old])

        vertices = np.c_[x_old, y_old, self.Z]
        faces = tri.simplices
        cmap = cm.get_cmap("plasma")

        # Исправление количества цветов
        face_colors = cmap(self.Z[faces].mean(axis=1) / self.Z.max())
        colors = ColorArray(face_colors[:, :3])

        self.mesh.set_data(vertices, faces=faces, face_colors=colors)

    def update_camera(self):
        if self.old_points.size == 0 or self.new_points.size == 0:
            return

        # Находим центр точек
        x_min, y_min = self.old_points.min(axis=0)
        x_max, y_max = self.old_points.max(axis=0)
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2

        # Оптимальная дистанция
        range_x = x_max - x_min
        range_y = y_max - y_min
        max_range = max(range_x, range_y)
        optimal_distance = max_range * 2  # Настройка дистанции

        # Устанавливаем камеру
        self.view.camera.center = (center_x, center_y, self.Z.max() / 2)
        self.view.camera.distance = optimal_distance

    def run(self):
        app.run()

    def default(self):
        self.old_points = np.array([])
        self.new_points = np.array([])
        self.mesh.parent = None  # Удаляем визуализацию с ViewBox

        # Пересоздаём пустую mesh
        self.mesh = scene.visuals.Mesh()
        self.view.add(self.mesh)