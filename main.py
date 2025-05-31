# from video_processor import VideoProcessor
# import threading
# from plt import Live3DPlot
# from gui import Ui_Video_Processor
# import sys
# import cv2
# from PyQt6 import QtCore, QtGui, QtWidgets
# from PyQt6.QtWidgets import QFileDialog, QMessageBox
# from PyQt6.QtGui import QImage, QPixmap
# if __name__ == "__main__":
#     def start_vispy():
#         plot.run()
#     plot = Live3DPlot()
#     vispy_thread = threading.Thread(target=start_vispy, daemon=True)
#     vispy_thread.start()
#     processor = VideoProcessor(plot)
#     app = QtWidgets.QApplication(sys.argv)
#     Video_Processor = QtWidgets.QMainWindow()
#     ui = Ui_Video_Processor(processor)
#     ui.setupUi(Video_Processor)
#     Video_Processor.show()
#     sys.exit(app.exec())

from video_processor import VideoProcessor
import threading
from plt import Live3DPlot
from gui2 import VideoProcessorWindow
import sys
import cv2
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication
if __name__ == "__main__":
    def start_vispy():
        plot.run()
    plot = Live3DPlot()
    vispy_thread = threading.Thread(target=start_vispy, daemon=True)
    vispy_thread.start()
    processor = VideoProcessor(plot)
    app = QtWidgets.QApplication(sys.argv)
    Video_Processor = QtWidgets.QMainWindow()
    ui = VideoProcessorWindow(processor)
    ui.show()
    sys.exit(app.exec())