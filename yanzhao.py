# coding=UTF-8
import re
import time
import datetime
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}


def get_yztj():
    url = 'https://yz.chsi.com.cn/yztj/'
    re_list = []
    try:
        resp = requests.get(url=url, headers=headers, timeout=2)
        re_list = re.findall('class="bigfont">(.*?)</span>', resp.text)
        return re_list
    except Exception as e:
        print('{}'.format(e))
        return re_list


def monitor():
    old_list = get_yztj()
    while True:
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_list = get_yztj()
        if new_list:
            string = '[{}]{}'.format(now_time, new_list)
            print(string)
            if new_list != old_list:
                msg = '信息更新{}'.format(new_list)
                print(msg)
            old_list = new_list
        time.sleep(60)


if __name__ == '__main__':
    monitor()
