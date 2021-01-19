import datetime
import json
import os
import sys
import threading

from flask import Flask, jsonify, request, request
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox

import create_data_ui

HOST = '127.0.0.1'
PORT = 80
close_flag = False
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
now = datetime.datetime.now()


def run():
    app.run(host='0.0.0.0', port='80')


class MyQueue(object):
    """
    存储方式为 range距离的list
    [
        [],
        [],
        []
    ]
    """

    def __init__(self) -> None:
        self.items = []
        self.filter_items = []

    def put(self, item):
        self.items.insert(0, item)

    def put_filter(self, item):
        self.filter_items.insert(0, item)

    def pu_all(self, _items, _filter_item):
        self.destroy()
        self.items = _items
        self.filter_items = _filter_item

    def pop(self):
        return self.items.pop()

    def pop_filter(self):
        return self.filter_items.pop()

    def empty(self):
        return self.items == []

    def empty_filter(self):
        return self.filter_items == []

    def size(self):
        return len(self.items)

    def size_filter(self):
        return len(self.filter_items)

    def destroy(self):
        self.items = []
        self.filter_items = []


queue_create = MyQueue()


class MainDialog(QDialog):
    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)
        self.ui = create_data_ui.Ui_dialog()
        self.ui.setupUi(self)
        self.ui.textEdit.setText('如有疑问， 请点击下方？阅读参考文档')

    @staticmethod
    def create_data():
        raw_data_list = []
        filter_data_list = []
        with open('RAW_LIDAR_DATA.json', 'r') as f:
            raw_data_dict = json.load(f)
            raw_data_list = raw_data_dict.get('lidar_data')

        with open('FILTERED_LIDAR_DATA.json', 'r') as f:
            raw_data_dict = json.load(f)
            filter_data_list = raw_data_dict.get('lidar_data')
        # print(raw_data_list)
        queue_create.pu_all(raw_data_list, filter_data_list)

    @staticmethod
    def help_button():
        os.system('HELP.txt')

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
            event.accept()
        else:
            event.ignore()


@app.route('/', methods=["GET"])
def hello():
    return jsonify("中科银狐激光雷达系统")


@app.route('/help/', methods=["GET"])
def help_page():
    return jsonify({'result': 0, 'result_message': '待编写'})


@app.route('/get_lidar_data/', methods=["GET"])
def get_lidar_data():
    if not queue_create.empty():
        _list = queue_create.pop()
        return jsonify({'result': 0, 'result_message': '0成功; lidar_data_x为横坐标列表 lidar_data_y为纵坐标列表; 横纵坐标相同下标互相对应',
                        'lidar_data_x': _list[0], 'lidar_data_y': _list[1], 'key': 'info_robot'})
    else:
        return jsonify({'result': 1, 'result_message': '1：失败，无数据，请先开启雷达'})


@app.route('/get_lidar_filter_data/', methods=["GET"])
def get_lidar_filter_data():
    if not queue_create.empty_filter():
        _list = queue_create.pop_filter()
        return jsonify({'result': 0, 'result_message': '0成功; lidar_data_x为横坐标列表 lidar_data_y为纵坐标列表; 横纵坐标相同下标互相对应',
                        'lidar_data_x': _list[0], 'lidar_data_y': _list[1], 'key': 'info_robot'})
    else:
        return jsonify({'result': 1, 'result_message': '1：失败，无数据，请先开启雷达'})


if __name__ == "__main__":
    t1 = threading.Thread(target=run, name='run')
    t1.start()
    myapp = QApplication(sys.argv)
    myDlg = MainDialog()
    myDlg.show()
    sys.exit(myapp.exec_())
