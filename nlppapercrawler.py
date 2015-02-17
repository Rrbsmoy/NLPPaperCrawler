# coding=utf-8

"""
名称 :"NLP论文爬虫"
版本 :1.1
作者 :heyu and ArthurYang
Email:heyucs@yahoo.com and ArthurYangCS@gmail.com
"""

import re
import urllib
import urllib2


ROOT_URL = 'http://www.aclweb.org/anthology/'


def get_paper_url(root_url):
    response = urllib2.urlopen(root_url)
    html = response.read()
    pattern = r'<p><a href=.+>.+</a>.*: <b>.+</b><br><i>.+</i>'
    regex = re.compile(pattern)
    url_list = re.findall(regex, html)
    return url_list


def get_file_name(url):
    regex_pr = re.compile(r'<p><a href=["]*(.*?)["]*>(.*?)</a>[: ]', re.DOTALL)
    filename = regex_pr.search(url)
    return filename.group(1)


def get_author(url):
    regex_pr = re.compile(r': <b>(.*?)</b><br>', re.DOTALL)
    authors = regex_pr.search(url)
    return authors.group(1)


def get_paper_name(url):
    regex_pr = re.compile(r'<br><i>(.*?)</i>', re.DOTALL)
    paper_name = regex_pr.search(url)
    return paper_name.group(1)


def filter_url(url_list, writer, keyword_dic):
    new_url_list = []
    for url in url_list:
        authors = get_author(url)
        paper_name = get_paper_name(url)
        flag = True
        for i in writer:
            if i.lower() not in authors.lower():
                flag = False
        for i in keyword_dic:
            if i.lower() not in paper_name.lower():
                flag = False
        if flag:
            new_url_list.append(url)
    return new_url_list


def get_conf_time(url):
    regex_pr = re.compile(r'<a href=".*">(.*?)</a>', re.DOTALL)
    years = regex_pr.search(url)
    conf_time = years.group(1)
    if conf_time == '74-79':
        return '1974-1979'
    else:
        if int(conf_time) > 50:
            return '19' + conf_time
        else:
            return '20' + conf_time


def get_conf_loc(url):
    regexpr = re.compile(r'<a href="(.*?)">.*</a>', re.DOTALL)
    loc = regexpr.search(url)
    return loc.group(1)


def get_one_conf(pattern, html, regex, locmap):
    regex_pr = re.compile(pattern, re.DOTALL)
    block = regex_pr.search(html)
    name_list = re.findall(regex, block.group(1))
    no = len(locmap)
    conf_list = []
    for i in range(len(name_list)):
        conf_list.append(get_conf_time(name_list[i]))
        if not get_conf_loc(name_list[i]).endswith('/'):
            locmap[no] = get_conf_loc(name_list[i]) + '/'
        else:
            locmap[no] = get_conf_loc(name_list[i])
        no += 1
    return conf_list


def get_all_conference(root_url, loc_map, conf_list):
    response = urllib2.urlopen(root_url)
    html = response.read()
    pattern = r'<a href="[A-Z0-9/]+">[-0-9]+</a>'
    regex = re.compile(pattern)
    cl_pattern = r'<tr><th title="Computational Linguistics Journal">CL:</th>(.*?)</td></tr>'
    acl_pattern = r'<tr><th title="ACL Annual Meeting">ACL:</th>(.*?)</td></tr>'
    eacl_pattern = r'<tr><th title="European Chapter of ACL">EACL:</th>(.*?)</td></tr>'
    naacl_pattern = r"<tr><th title=\"North American Chapter of ACL\">NAACL:</th>(.*?)</td></tr>"
    emnlp_pattern = r'<tr><th title=.*>EMNLP:</th>(.*?)</td></tr>'
    coling_pattern = r'<tr><th title=.*>COLING:</th>(.*?)</td></tr>'
    del conf_list[:]
    conf_list.extend([('CL', get_one_conf(cl_pattern, html, regex, loc_map)),
                      ("ACL", get_one_conf(acl_pattern, html, regex, loc_map)),
                      ('EACL', get_one_conf(eacl_pattern, html, regex, loc_map)),
                      ('NAACL', get_one_conf(naacl_pattern, html, regex, loc_map)),
                      ('EMNLP', get_one_conf(emnlp_pattern, html, regex, loc_map)),
                      ('Coling', get_one_conf(coling_pattern, html, regex, loc_map))])
    write_conference('conference.txt', conf_list, loc_map)


def down_paper(url, filename):
    urllib.urlretrieve(url, filename)
    f = urllib2.urlopen(url)
    data = f.read()
    with open(filename, "wb") as code:
        code.write(data)


def filename_filter(filename):
    result, number = re.subn(r'[/:*?"><|’]', '', filename)
    return result


def write_conference(filename, conf_list, loc_map):
    fw = open(filename, 'w')
    for x, y in loc_map.items():
        fw.write(y + ' ')
    fw.write('\n')
    for x, y in conf_list:
        fw.write(x + ':\n')
        for i in y:
            fw.write(i + ' ')
        fw.write('\n')
    fw.close()


def read_conference(filename, conf_list, loc_map):
    del conf_list[:]
    loc_map.clear()
    no = 0
    fr = open(filename)
    t = ''
    for i in fr.readline().strip().split():
        loc_map[no] = i
        no += 1
    for i in fr.readlines():
        if i[-2] == ':':
            t = i[:-2]
        else:
            conf_list.append((t, i.strip().split()))
    fr.close()