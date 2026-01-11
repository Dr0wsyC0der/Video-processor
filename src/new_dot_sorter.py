"""
Модуль сортировки и сопоставления точек для отслеживания объектов.

Класс MegaSorter группирует точки отслеживания, извлекает их координаты
и сопоставляет позиции объектов между кадрами.
"""

from random import randint
from typing import List, Tuple, Optional


class MegaSorter:
    """
    Класс для сортировки и сопоставления точек отслеживания объектов.

    Обрабатывает списки точек из различных кадров, группирует их
    и сопоставляет позиции объектов между кадрами для отслеживания.
    """

    def __init__(
        self,
        home_dots: List[List],
        frame_dots: List[Tuple[float, float]],
        threshold: int = 10
    ) -> None:
        """
        Инициализация сортировщика точек.

        Args:
            home_dots: Список списков точек из опорных кадров
            frame_dots: Список координат точек из текущего кадра
            threshold: Пороговое значение для группировки точек по X
        """
        self.home_dots = home_dots
        self.frame_dots = frame_dots
        self.new_l_x: List[List[List[int]]] = []
        self.new_l_y: List[List[List[int]]] = []
        self.old_x_y: List[Tuple[int, int]] = []
        self.new_x_y: List[Tuple[int, int]] = []
        self.threshold = threshold

    def group_first_list(self) -> None:
        """
        Группирует точки из первого списка по координате X.

        Сортирует точки из первого элемента home_dots и группирует их
        в списки по близости координаты X (в пределах threshold).
        """
        zero_list = sorted(self.home_dots, key=lambda x: (x[0], x[1]), reverse=True)

        flag_x: Optional[int] = None
        n = 0

        for point in zero_list[0][1]:
            if flag_x is None or abs(point[0] - flag_x) > self.threshold:
                flag_x = point[0]
                self.new_l_x.append([[point[0]]])
                self.new_l_y.append([[point[1]]])
                n += 1
            else:
                self.new_l_x[n - 1].append([point[0]])
                self.new_l_y[n - 1].append([point[1]])

    def extract_old_x_y(self) -> None:
        """
        Извлекает координаты старых точек из сгруппированных списков.

        Извлекает координаты точек из первого элемента каждого подсписка
        в сгруппированных списках и сохраняет их в old_x_y.
        """
        for i in range(len(self.new_l_x)):
            for i2 in range(len(self.new_l_x[i])):
                for i3 in range(len(self.new_l_x[i][i2])):
                    if i3 == 0:
                        self.old_x_y.append((
                            self.new_l_x[i][i2][i3],
                            self.new_l_y[i][i2][i3]
                        ))

    def extract_new_x_y(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Сопоставляет старые и новые координаты точек.

        Для каждой старой точки пытается найти ближайшую точку в текущем
        кадре. Если точка не найдена, генерирует случайную координату
        вблизи старой позиции.

        Returns:
            Кортеж (список_старых_координат, список_новых_координат)
        """
        new_positions: List[Tuple[int, int]] = []
        for point in self.old_x_y:
            found = False
            for point2 in self.frame_dots:
                if abs(point[0] - point2[0]) <= 10 and abs(point[1] - point2[1]) <= 10:
                    new_positions.append((int(point2[0]), int(point2[1])))
                    found = True
                    break

            if not found:
                # Генерация случайной координаты, если точка не найдена
                new_x = randint(point[0], point[0] + 3)
                new_y = randint(point[1], point[1] + 3)
                new_positions.append((new_x, new_y))

        # Сопоставление и сортировка пар точек
        paired = list(zip(self.old_x_y, new_positions))
        paired.sort(key=lambda x: (x[0][0], x[0][1]), reverse=True)

        nl1, nl2 = zip(*paired) if paired else ([], [])
        scaled_points = [(x, y) for x, y in list(nl2)]

        return list(nl1), scaled_points

    def reset_all_data(self) -> None:
        """
        Сбрасывает все данные сортировщика.

        Очищает все внутренние списки и данные для нового цикла обработки.
        """
        self.new_l_x = []
        self.new_l_y = []
        self.old_x_y = []
        self.new_x_y = []
        self.frame_dots = []
        self.home_dots = []

    def process(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Выполняет полный цикл обработки точек.

        Выполняет все этапы обработки: группировку, извлечение координат
        и сопоставление точек.

        Returns:
            Кортеж (список_старых_координат, список_новых_координат)
        """
        self.group_first_list()
        self.extract_old_x_y()
        old_coords, new_coords = self.extract_new_x_y()
        return old_coords, new_coords
