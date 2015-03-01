NLPPaperCrawler
===============
本程序主要针对**自然语言处理方向**的学者方便获取 Aclweb.org 上面与研究方向相关的论文。

在 heyuce 师兄的 1.0 版本的基础上加上了 GUI 界面以及多线程下载。

1.0 版本：[NLPPaperCrawler 1.0](https://github.com/heyucs/NLPPaperCrawler)

注意事项
---
**开发环境：** 

 * Python 2.7.9
 * Ubuntu 14.10
 * PyQt4

**所需 Python 模块：**

 * PyQt4

使用说明
---
 0. 运行 crawler\_gui.py
 1. 若会议列表为空或者不全，点击“更新会议”按钮更新会议列表
 2. 输入搜索关键词，不区分大小写，空格键分隔。若为空或者勾选“全部论文”单选框，则会下载全部论文
 3. 若要选择第一作者，在“第一作者”输入框内输入作者名称，不区分大小写，可以仅输入第一作者的姓或名
 4. 勾选所要下载的论文
 5. 若要按会议对所下载的论文进行分类，则勾选“按会议分类”单选框，每个会议都会生成单独的文件夹
 6. 同时下载的会议个数并不是越多越好，数量过多可能因网络阻塞而造成下载失败
 7. 点击“开始”按扭，即会开始下载论文，论文将会保存到当前目录下

联系方式
---
 * heyucs AT yahoo DOT com
 * ArthurYangCS AT gmail DOT com
 * 黑龙江大学A区实验楼312室

版权
---
黑龙江大学自然处理实验室©2014

官方微信:

![wx](http://ww3.sinaimg.cn/large/730c253cjw1els6zgnkm2j2076076jrw.jpg)

![NLPLabLogo](http://ww4.sinaimg.cn/large/730c253cjw1els6zsibuhj21kw06i0w8.jpg)
