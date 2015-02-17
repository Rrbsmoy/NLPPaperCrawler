# coding=utf-8

"""
名称 :"NLP论文爬虫"
版本 :2.0
作者 :heyu and ArthurYang
Email:heyucs@yahoo.com and ArthurYangCS@gmail.com
"""

import os
import time
import threading
from PyQt4.QtCore import *
from nlppapercrawler import *


class CrawlerWorker(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)

        self.stars = 0
        self.divided = False
        self.search = []
        self.writer = []
        self.loc_list = []
        self.num = 0
        self.pool = []
        self.seg = None

    def render(self, search, writer, loc_list, download_number, divided):
        self.writer = str(writer).split()
        self.search = str(search).split()
        self.divided = divided
        self.loc_list = loc_list
        self.seg = threading.Semaphore(download_number)
        self.start()

    def run(self):
        if self.search:
            dic = reduce(lambda a, b: a + '_' + b, self.search) + '_'
        else:
            dic = 'ALL_'
        curr_time = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
        dic += curr_time
        os.mkdir(dic)
        dic += '/'
        self.num = len(self.loc_list)
        self.pool = []
        for index, loc in enumerate(self.loc_list):
            self.pool.append(threading.Thread(target=self.download, args=(loc[0], loc[1], dic)))
            self.pool[-1].start()
        while self.num != 0:
            time.sleep(0.1)
        self.emit(SIGNAL('all_finished()'))

    def download(self, name, loc, dic):
        self.seg.acquire()
        try:
            down_url = ROOT_URL + loc
            url_list = get_paper_url(down_url)
            new_url_list = filter_url(url_list, self.writer, self.search)
            if new_url_list:
                if self.divided:
                    os.mkdir(dic + name)
                    self.download_paper_list(name, down_url, new_url_list, dic + name + '/')
                else:
                    self.download_paper_list(name, down_url, new_url_list, dic)
        except urllib2.URLError:
            self.emit(SIGNAL('display(QString)'), u'错误：网络异常，会议 ' + name + u' 下载失败')
            self.emit(SIGNAL('wrong(QString)'), name)
        except:
            self.emit(SIGNAL('display(QString)'), u'错误：未知错误，会议 ' + name + u' 下载失败')
            self.emit(SIGNAL('wrong(QString)'), name)
        else:
            if new_url_list:
                self.emit(SIGNAL('finished(QString)'), name)
            self.emit(SIGNAL('display(QString)'), u'成功下载会议 ' + name)
        self.num -= 1
        self.seg.release()

    def download_paper_list(self, name, root_url, url_list, dic):
        self.emit(SIGNAL('add_progress(QString,int)'), name, len(url_list))
        for index, url in enumerate(url_list):
            filename = get_file_name(url)
            authors = get_author(url)
            paper_name = get_paper_name(url)
            first_author = authors.split(';')[0]
            paper_name = filename_filter(paper_name)
            self.emit(SIGNAL('update_progress(QString,QString,int)'), name, paper_name, index)
            down_paper(root_url + filename, dic + name + '_' + first_author + '_' + paper_name + '.pdf')


class UpdateConf(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.stars = 0
        self.loc_map = {}
        self.conf_list = []

    def render(self):
        self.start()

    def run(self):
        try:
            get_all_conference(ROOT_URL, self.loc_map, self.conf_list)
        except urllib2.URLError:
            self.emit(SIGNAL('display(QString)'), u'错误： 网络异常，会议更新失败')
        except:
            self.emit(SIGNAL('display(QString)'), u'错误： 未知错误，会议更新失败')
        else:
            self.emit(SIGNAL('updated()'))
        self.emit(SIGNAL('updating_down()'))