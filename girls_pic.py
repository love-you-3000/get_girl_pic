"""
作者：朱江
班级：数据1707
学号：2017007839
创作时间：2019/9/25
"""
import requests
import re
import os
from tqdm import *


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


def get_index():
	url = 'https://www.mzitu.com/xinggan/'
	every_index = []
	for i in range(1,3):
		every_index.append(url+'page/'+str(i)+'/')
	return every_index


def getWeb():
	"""
	在获取的网站首页有很多图片集，每个图片集都是一个链接，
	该函数把所有图片集链接从首页html中抽离出来，并放入列表返回
	:return: 返回每个图片集的链接
	"""
	every_index = get_index()
	every_web = []
	for url in every_index:
		demo = gethtml(url)
		m = re.findall('<li><a href=\"(.*?)\"', demo)
		every_web.extend(m)
	return every_web


def get_picWeb():
	"""
	循环遍历每一个图片集的HTML，从中找到该图片集的标题，
	把他作为字典的键，然后把该图片集下的所有图片主页的链接放入列表作为该键的值
	:return:返回字典
	"""
	eve_web=getWeb()
	pic_dict = {}  # 创建一个字典用来存储题目和对应的照片主题链接
	for i in eve_web:
		new_i = gethtml(i)
		title = ''.join(re.findall('main-title\">(.*?)<',new_i)) # 提取每一个图片集的题目
		for j in range(16):
			m1=str(i)+'/'+str(j)  # 每个图片集的链接加上“/j”(j是第几页，正整数整数)就是对应图片的网页
			pic_dict.setdefault(title, []).append(m1)  # 将图片的网页链接加入到对应的title的值中
	return pic_dict


def download():
	"""
	该函数实现对图片的下载与保存
	"""
	requests.packages.urllib3.disable_warnings()  # 禁用证书验证会弹出warning，这样设置可以避免弹出
	pic_dict=get_picWeb()
	header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
							' (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
		, 'Referer': "https://www.mzitu.com/xinggan/"}
	print('正在下载。。。')
	# 这里的tqdm是为了显示进度条
	for i in tqdm(pic_dict): # 循环字典中的键，也就是每个图片集的标题
		pic_list = [] # 创建一个用于存储图片链接的列表
		os.mkdir('result\\%s' % i)  # 先创建好result文件夹，然后在该文件夹下以每个图片集的标题作为文件名创建文件夹
		for j in pic_dict[i]:  # 循环每一个标题对应的值，也就是图片网页的链接
			demo=gethtml(j)  # 获取网页的html源码
			m = re.findall('<img src=\"(.*?)\"', demo)  # 从源码中获取图片的链接
			pic_list.extend(m)
			x = 0  # 用户命名图片名
			for imgurl in pic_list:  # 循环每一个图片链接
				picFile = open('result\\%s\\%s.jpg' % (i,x), "wb")  # 打开对应标题的文件夹
				# 请求的是https 协议，这里的verify参数请求禁用证书验证
				picFile.write(requests.get(imgurl, headers=header, verify=False).content)  # 用request的content对图片进行下载
				picFile.close()  # 记得关闭文件
				x = x+1  # 图片名称加1
	print()
	print('全部下载完成！')


if __name__ == '__main__':
	print('程序启动中。。。')
	download()
