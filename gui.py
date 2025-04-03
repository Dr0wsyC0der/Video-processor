import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk



class VideoApp:
    def __init__(self, root, processor):
        self.root = root
        self.processor = processor

        self.root.title("Видео-плеер")
        self.root.geometry("800x500")

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        self.select_btn = tk.Button(self.frame, text="Выбрать видео", command=self.load_video)
        self.select_btn.pack(side=tk.LEFT, padx=10)

        self.video_path_label = tk.Label(self.frame, text="Файл не выбран")
        self.video_path_label.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.root, width=640, height=360)
        self.canvas.pack()

        self.play_btn = tk.Button(self.root, text="Воспроизвести", command=self.play_video)
        self.play_btn.pack(pady=10)

    def load_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Видео файлы", "*.mp4;*.avi;*.mov;*.mkv")])
        if file_path:
            self.video_path_label.config(text=file_path)
            self.processor.load_video(file_path)

    def play_video(self):
        self.processor.running = True
        self.update_frame()

    def update_frame(self):
        if self.processor.running:
            frame = self.processor.process_frame()
            if frame is not None:
                frame = cv2.resize(frame, (640, 360))
                img = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
                self.canvas.image = img
                self.root.after(33, self.update_frame)