import cv2
import numpy as np
import optuna

class AutoParams:
    def __init__(self, frame):
        self.frame = frame
        print(self.frame.shape[:2])

    def evaluate_params(self, brightness, contrast, noise):
        self.frame = cv2.resize(self.frame, (960, 540), interpolation=cv2.INTER_LINEAR)
        img = self.frame.copy()

        # Яркость и контраст
        img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness * 255)
        # Резкость
        # if sharpness > 0:
        #     kernel = np.array([[0, -1, 0],
        #                        [-1, 5 + sharpness * 2, -1],
        #                        [0, -1, 0]])
        #     img = cv2.filter2D(img, -1, kernel)
        # Шумоподавление
        if noise > 0:
            k = int(noise)
            if k % 2 == 0:
                k += 1
            img = cv2.medianBlur(img, k)
        # В серый
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Порог по Отсу
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cv2.imshow("bb", binary)
        # Контуры
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        good = [cnt for cnt in contours if 10 < cv2.contourArea(cnt) < 200]

        return len(good)

    def objective(self, trial):
        brightness = trial.suggest_float("brightness", -0.3921, 0.3921)
        contrast = trial.suggest_float("contrast", 0.5, 2.0)
        noise = trial.suggest_int("noise", 0, 5)

        score = self.evaluate_params(brightness, contrast, noise)
        return -score  # максимизируем количество хороших контуров

    def get_params(self, n_trials=50):
        study = optuna.create_study()
        study.optimize(self.objective, n_trials=n_trials)
        return study.best_params
