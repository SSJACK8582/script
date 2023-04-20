import json
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
    'Cookie': 'SUB=_'
}


def get_wb_hot(num):
    res_list = []
    url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        rank_list = soup.select('td.td-01')
        hot_list = soup.select('td a')
        for i in range(num * 2):
            if rank_list[i].text.isdigit():
                hot = hot_list[i].text.strip()
                res_list.append(hot)
            if rank_list[i].text == str(num):
                break
    except Exception as e:
        print(e)
    return res_list


def get_zh_hot(num):
    res_list = []
    url = 'https://api.zhihu.com/topstory/hot-list?limit10'
    try:
        resp = requests.get(url=url, headers=headers)
        resp_json = json.loads(resp.text)
        hot_list = resp_json['data']
        for i in range(num):
            hot = hot_list[i]['target']['title']
            res_list.append(hot)
    except Exception as e:
        print(e)
    return res_list


def get_bd_hot(num):
    res_list = []
    url = 'https://top.baidu.com/board?tab=realtime'
    try:
        resp = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        hot_list = soup.select('div.c-single-text-ellipsis')
        for i in range(num):
            hot = hot_list[i].text.strip()
            res_list.append(hot)
    except Exception as e:
        print(e)
    return res_list


def get_smzdm_hot(num):
    res_list = []
    url = 'https://faxian.smzdm.com/h3s0t0f0c0p1'
    try:
        resp = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        hot_list = soup.select('#feed-main-list > li > div > h5')
        price_list = soup.select('#feed-main-list > li > div > div.z-highlight.z-ellipsis')
        for i in range(num):
            hot = hot_list[i].text.replace(' ', '').replace('\n', '').replace('\r', '')
            price = price_list[i].text
            res_list.append(hot + '=' + price)
    except Exception as e:
        print(e)
    return res_list


if __name__ == '__main__':
    print(get_wb_hot(10))
    print(get_zh_hot(10))
    print(get_bd_hot(10))
    print(get_smzdm_hot(10))
