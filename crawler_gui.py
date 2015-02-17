# coding=utf-8

"""
名称 :"NLP论文爬虫"
版本 :2.0
作者 :heyu and ArthurYang
Email:heyucs@yahoo.com and ArthurYangCS@gmail.com
"""

import sys
import crawlerworker
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from nlppapercrawler import *


class CrawlerDlg(QDialog):
    def __init__(self, parent=None):

        self.no = 1
        self.updating = False
        self.downloading = False
        self.begin = False
        self.loc_map = {}
        self.top_choose = []
        self.choose = []
        self.conf_list = []
        self.num_top = []
        self.conf_name = []
        self.conf_index = {}
        self.download_label = []
        self.download_progress = []

        super(CrawlerDlg, self).__init__(parent)

        self.worker = crawlerworker.CrawlerWorker()
        self.updater = crawlerworker.UpdateConf()

        self.search_line_edit = QLineEdit()
        self.writer_line_edit = QLineEdit()
        search_label = QLabel(u'关键字：')
        writer_label = QLabel(u'第一作者：')
        ok_button = QPushButton(u'开始')
        cancel_button = QPushButton(u'取消')
        update_conf = QPushButton(u'更新会议')
        self.all_select = QCheckBox(u'全部会议')
        self.all_search = QCheckBox(u'全部论文')
        self.divide_paper = QCheckBox(u'按会议分类')
        download_number_label = QLabel(u'同时下载')
        self.download_number_spinbox = QSpinBox()
        self.download_number_spinbox.setRange(1, 8)
        self.download_number_spinbox.setValue(5)
        self.display_label = QLabel()
        self.display_label.setFrameShape(QFrame.Panel)
        self.display_label.setFrameShadow(QFrame.Sunken)

        self.select_frame = QFrame()
        select_scroll = QScrollArea()
        select_scroll.setWidget(self.select_frame)
        select_scroll.setWidgetResizable(True)
        select_scroll.setMinimumSize(300, 200)
        select_scroll.setFrameShape(QFrame.Panel)
        select_scroll.setFrameShadow(QFrame.Sunken)
        self.select_layout = QGridLayout(self.select_frame)
        self.display_select()

        self.progress_frame = QFrame()
        self.progress_frame.setFrameShape(QFrame.Panel)
        self.progress_frame.setFrameShadow(QFrame.Sunken)
        self.progress_scroll = QScrollArea()
        self.progress_scroll.setWidget(self.progress_frame)
        self.progress_scroll.setWidgetResizable(True)
        self.progress_scroll.setMinimumSize(600, 160)
        self.progress_scroll.setFrameShape(QFrame.NoFrame)
        self.progress_layout = QVBoxLayout(self.progress_frame)

        search_layout = QGridLayout()
        search_layout.addWidget(search_label, 0, 0)
        search_layout.addWidget(self.search_line_edit, 0, 1)
        search_layout.addWidget(writer_label, 1, 0)
        search_layout.addWidget(self.writer_line_edit, 1, 1)

        download_number_layout = QHBoxLayout()
        download_number_layout.addWidget(download_number_label)
        download_number_layout.addWidget(self.download_number_spinbox)

        button_layout = QVBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(update_conf)
        button_layout.addWidget(self.all_select)
        button_layout.addWidget(self.all_search)
        button_layout.addWidget(self.divide_paper)
        button_layout.addLayout(download_number_layout)

        layout = QGridLayout()
        layout.addLayout(search_layout, 0, 0)
        layout.addWidget(select_scroll, 1, 0)
        layout.addLayout(button_layout, 0, 1, 2, 1)
        layout.addWidget(self.progress_scroll, 3, 0, 1, 2)
        layout.addWidget(self.display_label, 4, 0, 1, 2)
        self.setLayout(layout)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.resize(1, 1)
        self.setWindowTitle(u'Paper Crawler')

        self.connect(ok_button, SIGNAL("clicked()"), self.begin_download)
        self.connect(cancel_button, SIGNAL("clicked()"), SLOT('reject()'))
        self.connect(update_conf, SIGNAL("clicked()"), self.update_conference)
        self.connect(self.all_search, SIGNAL("clicked()"), self.search_clicked)
        self.connect(self.all_select, SIGNAL("clicked()"), self.select_clicked)
        self.connect(self.updater, SIGNAL("updating_down()"), self.updating_down)
        self.connect(self.updater, SIGNAL("updated()"), self.updated)
        self.connect(self.updater, SIGNAL("display(QString)"), self.display)
        self.connect(self.worker, SIGNAL("display(QString)"), self.display)
        self.connect(self.worker, SIGNAL('add_progress(QString,int)'), self.make_progress)
        self.connect(self.worker, SIGNAL('update_progress(QString,QString,int)'), self.update_progress)
        self.connect(self.worker, SIGNAL('finished(QString)'), self.finished_progress)
        self.connect(self.worker, SIGNAL('wrong(QString)'), self.wrong_finished)
        self.connect(self.worker, SIGNAL('all_finished()'), self.all_finished)

    def wrong_finished(self, name):
        index = self.conf_index[name]
        self.download_label[index].setText(u'下载出错')
        self.download_label[index].setStyleSheet('color:red')

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if isinstance(item, QWidgetItem):
                item.widget().close()
            else:
                print "layout " + str(item)
                self.clearLayout(item.layout())
            layout.removeItem(item)

    def all_finished(self):
        self.downloading = False
        self.display(u'下载全部完成')

    def finished_progress(self, name):
        index = self.conf_index[name]
        self.download_label[index].setText(u'下载完成')
        finish = self.download_progress[index].maximum().real
        self.download_progress[index].setValue(finish)

    def update_progress(self, name, paper_name, number):
        index = self.conf_index[name]
        if len(paper_name) > 59:
            paper_name = paper_name[:59] + u'...'
        self.download_label[index].setText(u'正在下载 ' + paper_name)
        self.download_progress[index].setValue(number)

    def make_progress(self, name, maximum):
        self.conf_index[name] = len(self.download_label)
        progress = QFrame()
        progress.setFrameShape(QFrame.Panel)
        progress.setFrameShadow(QFrame.Sunken)
        layout = QGridLayout(progress)
        layout.setAlignment(Qt.AlignTop)
        progress_name = QLabel(name)
        self.download_label.append(QLabel(u'正在下载'))
        self.download_progress.append(QProgressBar())
        self.download_progress[-1].setRange(0, maximum)
        self.download_progress[-1].setValue(0)
        self.download_progress[-1].setFormat(u'%v/%m')

        layout.addWidget(progress_name, 0, 0)
        layout.addWidget(self.download_progress[-1], 0, 1)
        layout.addWidget(self.download_label[-1], 1, 0, 1, 2)

        self.progress_layout.addWidget(progress)

    def search_clicked(self):
        if self.all_search.isChecked():
            self.search_line_edit.setEnabled(False)
            self.search_line_edit.setText('')
        else:
            self.search_line_edit.setEnabled(True)

    def sub_select_clicked(self):
        selected = self.sender()
        iss = selected.isChecked()
        i = self.top_choose.index(selected)
        for j in range(self.num_top[i][0], self.num_top[i][1]):
            self.choose[j].setChecked(iss)
        flag = True
        for i in self.top_choose:
            if not i.isChecked():
                flag = False
        self.all_select.setChecked(flag)

    def conf_select_clicked(self):
        selected = self.sender()
        index = self.choose.index(selected)
        flag = True
        x, y = filter(lambda a: a[0] <= index < a[1], self.num_top)[0]
        top_index = self.num_top.index((x, y))
        for i in range(x, y):
            if not self.choose[i].isChecked():
                flag = False
        self.top_choose[top_index].setChecked(flag)
        for i in self.top_choose:
            if not i.isChecked():
                flag = False
        self.all_select.setChecked(flag)

    def select_clicked(self):
        iss = self.all_select.isChecked()
        for i in self.top_choose + self.choose:
            i.setChecked(iss)

    def update_conference(self):
        if self.downloading:
            self.display(u'正在下载，请稍后再试')
            return
        self.updating = True
        self.display(u'正在更新会议，请稍后……')
        self.loc_map = {}
        self.updater.render()

    def updated(self):
        self.loc_map = self.updater.loc_map
        self.conf_list = self.updater.conf_list
        self.display_select()
        self.display(u'会议更新完成')

    def updating_down(self):
        self.updating = False

    def display(self, string):
        self.display_label.setText(string)

    def display_select(self):
        read_conference('conference.txt', self.conf_list, self.loc_map)
        self.clear_layout(self.select_layout)
        self.top_choose = []
        self.choose = []
        self.num_top = []
        self.conf_name = []
        y = -1
        raw = 0
        for x, i in self.conf_list:
            col = 0
            name = x
            self.top_choose.append(QCheckBox(x))
            self.select_layout.addWidget(self.top_choose[-1], raw, col)
            raw += 1
            x = y + 1
            for j in i:
                self.conf_name.append(name + u'-' + j)
                self.choose.append(QCheckBox(j))
                self.select_layout.addWidget(self.choose[-1], raw, col)
                col += 1
                y += 1
            raw += 1
            self.num_top.append((x, y + 1))

        for i in self.top_choose:
            self.connect(i, SIGNAL("clicked()"), self.sub_select_clicked)
        for i in self.choose:
            self.connect(i, SIGNAL("clicked()"), self.conf_select_clicked)
        self.all_select.setChecked(False)

    def begin_download(self):
        if self.updating:
            self.display(u'正在更新会议，请稍后再试')
            return
        if self.downloading:
            self.display(u'正在下载，请稍后再试')
            return
        self.downloading = True
        self.display(u'正在下载论文，请稍后……')
        loc_list = []
        self.clear_layout(self.progress_layout)
        self.download_label = []
        self.download_progress = []
        download_number = self.download_number_spinbox.value()
        for index, x in enumerate(self.choose):
            if x.isChecked():
                loc_list.append((self.conf_name[index], self.loc_map[index]))
        self.display(u'共 ' + str(len(loc_list)) + u' 个会议')
        self.worker.render(self.search_line_edit.text(),
                           self.writer_line_edit.text(),
                           loc_list,
                           download_number,
                           self.divide_paper.isChecked())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CrawlerDlg()
    gui.show()
    app.exec_()