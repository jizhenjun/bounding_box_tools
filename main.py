import numpy as np
import pandas as pd
import time
import cv2
import sys
import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QRadioButton, QLineEdit, 
                             QHBoxLayout, QVBoxLayout, QMessageBox, QButtonGroup, QApplication, QLabel, QListView, QComboBox)
from PyQt5.QtCore import QCoreApplication, QRect, Qt, QStringListModel
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QGuiApplication, QColor

LABEL_LIST = pd.read_csv('label_list.csv',sep='\t',encoding='GBK',header = None)
LABEL_LIST = np.array(LABEL_LIST[0])
LABEL_LIST = LABEL_LIST.tolist()

class Rectangle():
    def __init__(self, x0=0, y0=0, x1=0, y1=0, whether_display=False, label=0):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.whether_display = whether_display
        self.label = label


class myLabel(QLabel):
    rectangle_label = []
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    img = None
    img_current = None
    qlabel_length = 640
    qlabel_width = 480

    def mousePressEvent(self, event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()

    def mouseReleaseEvent(self, event):
        self.flag = False

    def mouseMoveEvent(self, event):
        if self.flag:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        rect = QRect(self.x0, self.y0, abs(
            self.x1-self.x0), abs(self.y1-self.y0))
        painter = QPainter(self)
        painter.setPen(QPen(Qt.blue, 4, Qt.SolidLine))
        painter.drawRect(rect)

    def save_current_border(self, label):
        self.rectangle_tmp = Rectangle(
            self.x0, self.y0, self.x1, self.y1, True, label)
        self.rectangle_label.append(self.rectangle_tmp)
        self.img_current = self.img.copy()
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.update()

    def delete_border(self, pos):
        if pos in range(len(self.rectangle_label)):
            self.rectangle_label.pop(pos)

    def update_qlabel_img(self):  # 更新当前的图片
        self.img_current = self.img.copy()
        h, w, channel= self.img_current.shape
        for i in range(len(self.rectangle_label)):
            if self.rectangle_label[i].whether_display == True:  # 如果mark为true
                cv2.rectangle(
                    self.img_current, (self.rectangle_label[i].x0 * w // self.qlabel_length,
                                       self.rectangle_label[i].y0 * h // self.qlabel_width),
                                      (self.rectangle_label[i].x1 * w // self.qlabel_length,
                                       self.rectangle_label[i].y1 * h // self.qlabel_width), (0, 0, 255), 4)

class CollectData(QWidget):
    def __init__(self):
        super().__init__()
        self.init_variable()
        self.init_img()

        self.init_ui()
        self.show()

    def init_img(self):
        self.qlabel = myLabel(self)
        img = cv2.imread('data/test.png')  # 打开图片
        self.qlabel.img = img.copy()
        self.qlabel.img_current = img.copy()
        self.update_img()

    def init_variable(self):
        self.label = 0
        self.transformation_type = 0
        self.total_img_number = 0
        self.current_img_index = 0
        self.folder_path = r"data"
        self.jump_img_index = -1
        self.img_list = []
        self.img_name_list = []

    def init_ui(self):
        self.setGeometry(200, 200, 1000, 800)
        self.setWindowTitle('数据标注')
        self.qlabel.setGeometry(QRect(30, 30, 640, 480))
        self.init_buttons()

        for file_name in os.listdir(self.folder_path + '/'):
            img = cv2.imread(self.folder_path + '/' + file_name)
            if img is None:
                continue
            self.img_list.append(img)
            self.img_name_list.append(os.path.splitext(self.folder_path + '/' + file_name)[0])
        #QMessageBox.information(self, 'complete', '图片加载完毕')
        self.total_img_number = len(self.img_list)
        self.current_img_index = 1
        self.refresh_img()

        self.update_list()

    def init_buttons(self):
        self.previous_img_button = QPushButton("上一张图片", self)
        self.next_img_button = QPushButton("下一张图片", self)
        self.save_message_button = QPushButton("保存当前图片信息", self)
        self.show_message_button = QPushButton("显示当前图片信息", self)
        self.open_folder_button = QPushButton("打开文件夹", self)
        self.add_border_button = QPushButton("保存当前框", self)
        self.delete_border_button = QPushButton("删除选中框", self)
        self.img_folder_text = QLineEdit('data', self)
        self.goto_chosen_img_button = QPushButton("跳转图片", self)
        self.jump_img_text = QLineEdit('', self)
        self.show_index_message = QLabel(self)

        self.img_folder_text.selectAll()
        self.img_folder_text.setFocus()

        self.previous_img_button.setGeometry(30, 530, 150, 40)
        self.next_img_button.setGeometry(200, 530, 150, 40)
        self.save_message_button.setGeometry(370, 530, 150, 40)
        self.show_message_button.setGeometry(540, 530, 150, 40)
        self.img_folder_text.setGeometry(30, 590, 660 ,40)
        self.open_folder_button.setGeometry(710, 590, 150, 40)
        self.jump_img_text.setGeometry(30, 650, 150, 40)
        self.goto_chosen_img_button.setGeometry(200, 650, 150, 40)
        self.show_index_message.setGeometry(30, 710, 200, 40)
        self.add_border_button.setGeometry(710, 380, 150, 40)
        self.delete_border_button.setGeometry(710, 440, 150, 40)

        self.previous_img_button.clicked.connect(self.previous_img)
        self.next_img_button.clicked.connect(self.next_img)
        self.save_message_button.clicked.connect(self.save_message)
        self.show_message_button.clicked.connect(self.show_message)
        self.open_folder_button.clicked.connect(self.open_folder)
        self.add_border_button.clicked.connect(self.save_current_border)
        self.delete_border_button.clicked.connect(self.delete_border)
        self.goto_chosen_img_button.clicked.connect(self.goto_chosen_img)

        self.label_combo = QComboBox(self)
        for i in range(len(LABEL_LIST)):
            self.label_combo.addItem(LABEL_LIST[i])
        self.label_combo.move(900, 30)
        self.label_combo.activated[str].connect(self.label_on_activated)

        self.listview = QListView(self)
        self.listview.setGeometry(710, 30, 150, 320)
        self.listview.doubleClicked.connect(self.list_clicked)
        self.listview.setEditTriggers(QListView.NoEditTriggers)

    def previous_img(self):
        if self.current_img_index == 1:
            QMessageBox.information(self, 'warning', '已经是第一张啦')
            return
        self.current_img_index -= 1
        self.refresh_img()

    def next_img(self):
        if self.current_img_index == self.total_img_number:
            QMessageBox.information(self, 'warning', '已经是最后一张啦')
            return
        self.current_img_index += 1
        self.refresh_img()

    def show_message(self):
        if len(self.qlabel.rectangle_label) > 0:
            reply = QMessageBox.question(self, '确认', '当前有未保存信息，是否继续？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        self.qlabel.rectangle_label.clear()
        if os.path.isfile(self.img_name_list[self.current_img_index - 1] + '.csv') == False:
            QMessageBox.information(self, 'warning', '当前图片无信息')
            return
        message = pd.read_csv(self.img_name_list[self.current_img_index - 1] + '.csv', sep=',' ,header = None)
        message = np.array(message.T)
        message = message.astype(int)
        for i in range(len(message)):
            self.qlabel.rectangle_label.append(
                Rectangle(message[i][1],
                          message[i][2],
                          message[i][3],
                          message[i][4],
                          True,
                          message[i][0])
            )
        self.update_list()
        self.refresh_img()
        
        QMessageBox.information(self, 'complete', '信息加载完毕')

    def open_folder(self):
        self.folder_path = self.img_folder_text.text()
        if os.path.isdir(self.folder_path) == False:
            QMessageBox.information(self, 'warning', '文件夹路径非法')
            return
        self.img_list.clear()
        self.img_name_list.clear()
        for file_name in os.listdir(self.folder_path + '/'):
            img = cv2.imread(self.folder_path + '/' + file_name)
            if img is None:
                continue
            self.img_list.append(img)
            self.img_name_list.append(os.path.splitext(self.folder_path + '/' + file_name)[0])
        QMessageBox.information(self, 'complete', '图片加载完毕')
        self.total_img_number = len(self.img_list)
        self.current_img_index = 1
        self.refresh_img()

    def goto_chosen_img(self):
        if int(self.jump_img_text.text()) <= 0 or int(self.jump_img_text.text()) > self.total_img_number:
            QMessageBox.information(self, 'warning', '已经是最后一张啦')
            return
        self.current_img_index = int(self.jump_img_text.text())
        self.refresh_img()

    def refresh_img(self):
        img = self.img_list[self.current_img_index - 1]
        self.qlabel.img = img.copy()
        self.qlabel.update_qlabel_img()
        self.update_img()
        self.show_index_message.setText('一共' + str(self.total_img_number) + '张图片,当前第' + str(self.current_img_index) + '张图片')

    def label_on_activated(self):
        self.label = self.label_combo.currentIndex()

    def update_list(self):
        slm = QStringListModel()
        string_list = []
        for i in range(len(self.qlabel.rectangle_label)):
            string_list.append(LABEL_LIST[self.qlabel.rectangle_label[i].label])
        slm.setStringList(string_list)
        self.listview.setModel(slm)

    def list_clicked(self, qModelIndex):
        if self.qlabel.rectangle_label[qModelIndex.row()].whether_display == True:
            self.qlabel.rectangle_label[qModelIndex.row()].whether_display = False
        else:
            self.qlabel.rectangle_label[qModelIndex.row()].whether_display = True
        self.qlabel.update_qlabel_img()
        self.update_img()

    def save_current_border(self):
        self.qlabel.save_current_border(self.label)
        self.qlabel.update_qlabel_img()
        self.update_img()
        self.update_list()

    def update_img(self):
        img_resize = cv2.resize(self.qlabel.img_current, (self.qlabel.qlabel_length, self.qlabel.qlabel_width))
        height, width, bytesPerComponent = img_resize.shape
        bytesPerLine = 3 * width
        cv2.cvtColor(img_resize, cv2.COLOR_BGR2RGB, img_resize)
        QImg = QImage(img_resize.data, width, height,
                      bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        self.qlabel.setPixmap(pixmap)
        self.qlabel.setCursor(Qt.CrossCursor)

    def label_clicked(self):
        sender = self.sender()
        if sender == self.label_button:
            self.label = self.label_button.checkedId()

    def save_message(self):
        self.save_current_angle()
        img = cv2.imread('data/test.png')  # 打开图片
        self.qlabel.rectangle_label.clear()
        self.update_img()
        self.update_list()
        self.qlabel.img = img.copy()
        self.qlabel.img_current = img.copy()
        self.update_img()

    def save_current_angle(self):
        if os.path.isfile(self.img_name_list[self.current_img_index - 1] + '.csv'):
            reply = QMessageBox.question(self, '确认', '是否覆盖当前图片已保存信息？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        save_data = []
        for i in range(5):
            save_data.append([])
        if len(self.qlabel.rectangle_label) > 0:
            for i in range(len(self.qlabel.rectangle_label)):
                save_data[0].append(self.qlabel.rectangle_label[i].label)
                save_data[1].append(self.qlabel.rectangle_label[i].x0)
                save_data[2].append(self.qlabel.rectangle_label[i].x1)
                save_data[3].append(self.qlabel.rectangle_label[i].y0)
                save_data[4].append(self.qlabel.rectangle_label[i].y1)

            if np.shape(np.array(save_data)) != (5, 0):
                print(self.current_img_index)
                np.savetxt(self.img_name_list[self.current_img_index - 1] + '.csv',
                           np.array(save_data), delimiter=',')

    def delete_border(self):
        if self.listview.currentIndex().row() > -1:
            self.qlabel.delete_border(self.listview.currentIndex().row())
            self.qlabel.update_qlabel_img()
            self.update_img()
            self.update_list()
        else:
            QMessageBox.information(self, 'warning', '请先选中一行')

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = CollectData()
    sys.exit(app.exec_())
