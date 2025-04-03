import tkinter as tk
from video_processor import VideoProcessor
from gui import VideoApp
import threading
from plt import Live3DPlot

if __name__ == "__main__":
    def start_vispy():
        plot.run()
    plot = Live3DPlot()
    root = tk.Tk()
    vispy_thread = threading.Thread(target=start_vispy, daemon=True)
    vispy_thread.start()
    processor = VideoProcessor(plot)
    app = VideoApp(root, processor)
    root.mainloop()