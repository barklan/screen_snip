#!/usr/bin/env python3

import io
import sys
import os
import pyperclip
import pytesseract
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from skimage.filters import threshold_otsu, threshold_yen
import skimage
# import cv2
from datetime import datetime
import numpy as np

import subprocess

from img2tex import ScribbleMyScience


class Snipper(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.setWindowTitle("TextShot")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog
        )
        self.setWindowState(self.windowState() | Qt.WindowFullScreen)

        self.screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos()).grabWindow(0)
        palette = QtGui.QPalette()
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(self.screen))
        self.setPalette(palette)

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.start, self.end = QtCore.QPoint(), QtCore.QPoint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QtWidgets.QApplication.quit()

        return super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.drawRect(0, 0, self.width(), self.height())

        if self.start == self.end:
            return super().paintEvent(event)

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 3))
        painter.setBrush(painter.background())
        painter.drawRect(QtCore.QRect(self.start, self.end))
        return super().paintEvent(event)

    def mousePressEvent(self, event):
        self.start = self.end = event.pos()
        self.update()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.start == self.end:
            return super().mouseReleaseEvent(event)

        # self.hide()
        QtWidgets.QApplication.processEvents()
        shot = self.screen.copy(QtCore.QRect(self.start, self.end))
        self.processImage(shot)
        self.hide()  # Hide overlay only after image have been processed
        QtWidgets.QApplication.quit()

    def save_img_to_log(self, pil_img):
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        pil_img.save(f"../img/snip_{dt_string}.png")

    def processImage(self, img):
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        img_work = Image.open(io.BytesIO(buffer.data()))

        # Upscale
        new_size = (dim * 5 for dim in img_work.size)
        img_work = img_work.resize(new_size, resample=Image.LANCZOS)

        # Threshold
        img_work = np.array(img_work)
        img_work = skimage.color.rgb2gray(img_work)
        thresh = threshold_otsu(img_work)
        # thresh = threshold_yen(img_work)
        img_work = img_work > thresh

        # Final image
        img_final = Image.fromarray(img_work)

        # img2tex
        # img_final.save("temp.png")

        # buffer.close()

        # img2tex
        # result = ScribbleMyScience.img2tex("temp.png")
        # os.remove("temp.png")

        # if result:
            # result = result.strip()
            # result = "$$\n" + result + "\n$$\n"
        # else:
        try:
            result = pytesseract.image_to_string(
                img_final, timeout=20, lang=(sys.argv[1] if len(sys.argv) > 1 else None)
            )
            if result:
                result = result.strip()
        except RuntimeError as error:
            print(f"ERROR: An error occurred when trying to process the image: {error}")
            result = None
                
        if result:
            if result != "":
                pyperclip.copy(result)
            else:
                pyperclip.copy("OCR_FAILED")
                print(f"OCR_FAILED")
        else:
            pyperclip.copy("OCR_FAILED")
            print(f"OCR_FAILED")

        # self.save_img_to_log(img_final)
        


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    # try:
    #     pytesseract.get_tesseract_version()
    # except EnvironmentError:
    #     print(
    #         "ERROR: Tesseract is either not installed or cannot be reached.\n"
    #         "Have you installed it and added the install directory to your system path?"
    #     )
    #     sys.exit()

    window = QtWidgets.QMainWindow()
    snipper = Snipper(window)
    snipper.show()
    sys.exit(app.exec_())
