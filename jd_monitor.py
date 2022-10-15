# coding=UTF-8
import re
import json
import time
import datetime
import requests
import threading

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
}


def get_stock(sku_ids, area_id):
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    url = 'https://c0.3.cn/stocks'
    params = {
        'skuIds': sku_ids,
        'area': area_id,
        'type': 'getstocks',
    }
    stock_list = []
    try:
        resp = requests.get(url=url, params=params, headers=headers, timeout=2)
        resp_json = json.loads(resp.text)
        for sku_id, info in resp_json.items():
            sku_state = info.get('skuState')
            stock_state = info.get('StockState')
            stock_state_name = info.get('StockStateName')
            goods_info = {
                'sku_id': sku_id,
                'sku_state': sku_state,
                'stock_state': stock_state,
                'stock_state_name': stock_state_name,
            }
            stock_list.append(goods_info)
            string = '[{}][{}-{}-{}][{}][{}]'.format(
                now_time, sku_id, sku_state, stock_state, stock_state_name, area_id)
            print(string)
        return stock_list
    except requests.exceptions.Timeout:
        print('[{}]查询库存信息超时'.format(now_time))
        return []
    except Exception as e:
        print('[{}]查询库存信息异常：{}'.format(now_time, e))
        return []


def check_stock(stock_list):
    sku_id_list = []
    if stock_list:
        for item in stock_list:
            if item['sku_state'] == 1 and item['stock_state'] in (33, 36, 40):
                sku_id_list.append(item['sku_id'])
    return sku_id_list


def get_price(sku_id):
    url = 'https://p.3.cn/prices/mgets?skuIds=J_{}'.format(sku_id)
    try:
        resp = requests.get(url=url)
        resp_json = json.loads(resp.text[1:-2])
        price = resp_json.get('p')
        return price
    except Exception as e:
        print(e)


def get_name(sku_id):
    url = 'https://item.jd.com/{}.html'.format(sku_id)
    try:
        resp = requests.get(url=url, headers=headers)
        name = re.findall('<title>(.*?)</title>', resp.text)[0][:-16]
        return name
    except Exception as e:
        print(e)


def monitor(sku_id_list, area_id):
    sku_ids = ','.join(sku_id_list)
    old_list = []
    while True:
        stock_list = get_stock(sku_ids, area_id)
        new_list = check_stock(stock_list)
        for sku_id in new_list:
            if sku_id not in old_list:
                stock_state_name = ''
                for item in stock_list:
                    if item['sku_id'] == sku_id:
                        stock_state_name = item['stock_state_name']
                        break
                name = get_name(sku_id)
                price = get_price(sku_id)
                msg = '京东库存更新[{}][{}][{}][{}][{}]'.format(stock_state_name, price, name, sku_id, area_id)
                print(msg)
        old_list = new_list
        time.sleep(2)


if __name__ == '__main__':
    # sku_ids = ''
    # sku_id_list = list(filter(bool, map(lambda x: x.strip(), sku_ids.split(' '))))
    sku_id_list = ['']
    area_id_list = ['']
    for area_id in area_id_list:
        threading.Thread(target=monitor, args=(sku_id_list, area_id)).start()
