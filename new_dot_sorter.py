from random import randint
class MegaSorter:
    def __init__(self, home_dots, frame_dots, threshold = 10):
        self.home_dots = home_dots
        self.frame_dots = frame_dots
        self.new_l_x = []
        self.new_l_y = []
        self.old_x_y = []
        self.new_x_y = []
        self.threshold = threshold

    def group_first_list(self):
        zero_list = sorted(self.home_dots, key=lambda x: (x[0], x[1]), reverse=True)
        flag_x = None
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

    def extract_old_x_y(self):
        for i in range(len(self.new_l_x)):
            for i2 in range(len(self.new_l_x[i])):
                for i3 in range(len(self.new_l_x[i][i2])):
                    if i3 == 0:
                        self.old_x_y.append((self.new_l_x[i][i2][i3], self.new_l_y[i][i2][i3]))

    def extract_new_x_y(self):
        new_positions = []
        for point in self.old_x_y:
            found = False
            for point2 in self.frame_dots:
                if abs(point[0] - point2[0]) <= 10 and abs(point[1] - point2[1]) <= 10:
                    new_positions.append((int(point2[0]), int(point2[1])))
                    found = True
                    break
            if not found:
                new_x = randint(point[0], point[0] + 3)
                new_y = randint(point[1], point[1] + 3)
                new_positions.append((new_x, new_y))

        paired = list(zip(self.old_x_y, new_positions))
        paired.sort(key=lambda x: (x[0][0], x[0][1]), reverse=True)

        nl1, nl2 = zip(*paired) if paired else ([], [])
        scaled_points = [(x, y) for x, y in list(nl2)]
        return list(nl1), scaled_points

    def process(self):
        self.group_first_list()
        self.extract_old_x_y()
        l1, l2 = self.extract_new_x_y()
        return l1, l2




