"""
作者：朱江
脚本简介：本脚本实现对妹子图网站的图片的多线程爬取
时间:2019/10/9
"""

import threading
import re
import requests
import time
import os
from queue import Queue

# 存放爬取线程的列表
crawl_thread_list  = []
# 存放解析网页线程的列表
parse_thread_list = []
# 存放下载图片线程的列表
download_thread_list = []

def gethtml(x_url):
    """
    获取要爬取网站的首页html
    :param x_url:要爬取的网站uurl
    :return: 返回该网站的html
    """
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
							'(KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
							'Referer': "https://www.mzitu.com/xinggan/"}
    req = requests.get(url=x_url, headers=header)
    return req.text

def get_index(page_nums):
    """
    爬取的页面总数，每个页面又有24个图片集，这里获取前page_nums个网页
    :param page_nums: 页数
    :return:
    """
    url = 'https://www.mzitu.com/xinggan/'
    every_index = []
    for i in range(1,page_nums+1):
        every_index.append(url+'page/'+str(i)+'/')
    return every_index

def get_img_src(url):
    """
    获取页面中的图片链接
    """
    demo = gethtml(url)
    m = ''.join(re.findall('<img src=\"(.*?)\"', demo))
    return m

def download_img(src):
    """
    下载传进来的图片
    :param src: 图片链接
    """
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            '(KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
              'Referer': "https://www.mzitu.com/xinggan/"}
    return requests.get(src, headers=header, verify=False).content

def get_title(url):
    """
    获取每个图片集的标题，之后用作存储图片的总文件夹
    """
    demo = gethtml(url)
    title = ''.join(re.findall('main-title\">(.*?)<',demo))
    return title

# 爬取线程类
class crawlthread(threading.Thread):
    def __init__(self,name,index_queue,web_queue):
        """
        该类实现对所有index的页面进行爬取，返回所有的图片集对应的网页链接
        :param name: 线程名称
        :param index_queue: 首页链接队列
        :param web_queue: 各个图片集的链接队列
        """
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.index_queue = index_queue
        self.web_queue = web_queue

    def run(self):
        print(self.name + '启动-->', os.getpid())
        while not self.index_queue.empty():
            url = self.index_queue.get()
            demo = gethtml(url)
            m = re.findall('<li><a href=\"(.*?)\"', demo)
            for i in m:
                self.web_queue.put(i)

# 解析线程类
class parsethread(threading.Thread):
    def __init__(self,name,web_queue,img_queue):
        """
        该类实现对每个图片集中爬取一定数量的图片链接
        :param name: 线程名
        :param web_queue: 图片集链接队列
        :param img_queue: 图片集标题和对应图片链接队列
        """
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.web_queue = web_queue
        self.img_queue = img_queue
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                '(KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
                  'Referer': "https://www.mzitu.com/xinggan/"}


    def parse_url(self,index):
        title = get_title(index)
        # 可能存在请求失败的情况，这种时候回返回空页面，如果出现空页面就一直重复请求，知道获取网页
        while title == '':
            title = get_title(index)
        result = []
        result.append(title)
        print(self.name + '正在解析' + index)
        for j in range(1, 6):
            m = str(index) + '/' + str(j)
            img_src = get_img_src(m)
            while img_src=='':
                img_src = get_img_src(m)
            if img_src is not None:
                result.append(img_src)
        return result

    def run(self):
        print(self.name + '启动-->', os.getpid())
        while not self.web_queue.empty():
            # 通过if使线程分开工作，防止在一个线程使用全局变量时，另一个线程对这个变量造成修改
            if self.name=='解析线程1号':
                index1 = self.web_queue.get()
                result1 = self.parse_url(index1)
                self.img_queue.put(result1)
                
            elif self.name=='解析线程2号':
                result2 = self.parse_url(index2)
                self.img_queue.put(result2)
                
            else:
                index3 = self.web_queue.get()
                result3 = self.parse_url(index3)
                self.img_queue.put(result3)



class downloadthread(threading.Thread):
    def __init__(self,name,img_queue):
        """
        该类实现对图片的下载
        :param name: 线程名称
        :param img_queue: 存有图片链接的队列
        """
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.img_queue = img_queue


    def download_img(self,img_src):
        # 不存在以图片集为名的文件夹时则创建之
        if not os.path.exists('test\\%s' % img_src[0]):
            os.mkdir('test\\%s' % img_src[0])
        x = 1
        for i in range(1, len(img_src)):
            print(self.name + '正在下载图片' + img_src[i])
            image = download_img(img_src[i])
            picFile = open('test\\%s\\%s.jpg' % (img_src[0], x), 'wb')
            x += 1
            picFile.write(image)
        picFile.close()

    def run(self):
        requests.packages.urllib3.disable_warnings()
        print(self.name + '启动-->', os.getpid())
        while not self.img_queue.empty():
            if self.name=='下载线程1号':
                img_src1 = self.img_queue.get()
                self.download_img(img_src1)
            elif self.name=='下载线程2号':
                img_src2 = self.img_queue.get()
                self.download_img(img_src2)
            else:
                img_src3 = self.img_queue.get()
                self.download_img(img_src3)
            
# 创建队列
def create_queue():
    # 存放全部首页的队列
    index_queue = Queue()
    # 将前page页放入该队列
    page = 1
    web_index = get_index(page)
    for i in web_index:
        index_queue.put(i)
    # 存放所有图片集链接的队列
    web_queue = Queue()
    # 存放所有图片链接的队列
    img_queue = Queue()
    return index_queue,web_queue,img_queue


# 创建爬取线程
def create_crawl_thread(index_queue,web_queue):
    carwl_thread_name = ['采集线程1号','采集线程2号','采集线程3号']
    for name in carwl_thread_name:
        t = crawlthread(name,index_queue,web_queue)
        crawl_thread_list.append(t)
    return crawl_thread_list

# 创建解析线程
def create_parse_thread(web_queue,img_queue):
    parse_thread_name = ['解析线程1号', '解析线程2号', '解析线程3号']
    for name in parse_thread_name:
        t = parsethread(name,web_queue,img_queue)
        parse_thread_list.append(t)
    return parse_thread_list

# 创建下载线程
def create_download_thread(img_queue):
    download_thread_name = ['下载线程1号', '下载线程2号', '下载线程3号']
    for name in download_thread_name:
        t = downloadthread(name,img_queue)
        download_thread_list.append(t)
    return download_thread_list


def main():
    start = time.time()
    index_queue, web_queue,img_queue= create_queue()
    crawl_thread_list = create_crawl_thread(index_queue,web_queue)
    parse_thread_list = create_parse_thread(web_queue,img_queue)
    download_thread_list = create_download_thread(img_queue)
    for i in crawl_thread_list:
        i.start()
    for i in crawl_thread_list:
        i.join()
    for p in parse_thread_list:
        p.start()
    for p in parse_thread_list:
        p.join()
    for d in download_thread_list:
        d.start()
    for d in download_thread_list:
        d.join()
    end = time.time()
    print('下载完成！')
    time.sleep(2)
    print('耗时：', end-start)


if __name__ =='__main__':
    main()


