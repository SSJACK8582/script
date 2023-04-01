import json
import requests

host = '127.0.0.1'
port = ''
key = ''
headers = {
    'User-Agent': 'Mozilla',
    'Authorization': 'Bearer {}'.format(key)
}


def get_configs():
    url = 'http://{}:{}/{}'.format(host, port, 'configs')
    try:
        resp = requests.get(url=url, headers=headers)
        resp_json = json.loads(resp.text)
        return resp_json
    except Exception as e:
        print(e)


def set_mode(mode):
    url = 'http://{}:{}/{}'.format(host, port, 'configs')
    payload = {'mode': mode}
    try:
        resp = requests.patch(url=url, headers=headers, data=json.dumps(payload))
        print(resp.text)
    except Exception as e:
        print(e)


def get_proxies():
    url = 'http://{}:{}/{}'.format(host, port, 'proxies')
    try:
        resp = requests.get(url=url, headers=headers)
        resp_json = json.loads(resp.text)
        return resp_json.get('proxies')
    except Exception as e:
        print(e)


def set_node(group, name):
    url = 'http://{}:{}/{}/{}'.format(host, port, 'proxies', group)
    payload = {'name': name}
    try:
        resp = requests.put(url=url, headers=headers, data=json.dumps(payload))
        print(resp.text)
    except Exception as e:
        print(e)


def get_delay(name):
    url = 'http://{}:{}/{}/{}/delay?timeout=5000&url=http://www.gstatic.com/generate_204'.format(host, port, 'proxies', name)
    try:
        resp = requests.get(url=url, headers=headers)
        resp_json = json.loads(resp.text)
        return resp_json.get('delay')
    except Exception as e:
        print(e)


def get_ip_info():
    configs = get_configs()
    proxies = {
        'http': '127.0.0.1:{}'.format(configs.get('mixed-port')),
        'https': '127.0.0.1:{}'.format(configs.get('mixed-port'))
    }
    url = 'https://2023.ipchaxun.com'
    try:
        resp = requests.get(url=url, headers=headers, proxies=proxies)
        resp_json = json.loads(resp.text)
        return resp_json
    except Exception as e:
        print(e)


def change_node(index):
    set_mode('GLOBAL')
    proxies = get_proxies()
    global_node = proxies.get('GLOBAL', {}).get('all')
    while True:
        print(global_node[index])
        set_node('GLOBAL', global_node[index])
        delay = get_delay(global_node[index])
        if index + 1 < len(global_node):
            index += 1
        else:
            index = 0
        if str(delay).isdigit():
            ip_info = get_ip_info()
            print(ip_info)
            if ip_info:
                return index


if __name__ == '__main__':
    change_node(0)
