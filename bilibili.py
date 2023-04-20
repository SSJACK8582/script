import json
import time
import datetime
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}


def get_dynamic_list(uid):
    url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={}'.format(uid)
    try:
        resp = requests.get(url=url, headers=headers)
        resp_json = json.loads(resp.text)
        print('[{}]{}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resp_json['data'])[0:80])
        if resp_json['data'] and resp_json['data']['has_more']:
            return resp_json['data']['cards']
        else:
            return []
    except Exception as e:
        print(e)


def get_last_dynamic(dynamic_list):
    if dynamic_list:
        if dynamic_list[0]['extra']['is_space_top'] == 0:
            return dynamic_list[0]
        else:
            return dynamic_list[1]
    else:
        return {}


def compare_dynamic(dynamic1, dynamic2):
    if dynamic1 and dynamic2:
        dynamic_id1 = dynamic1['desc']['dynamic_id']
        dynamic_id2 = dynamic2['desc']['dynamic_id']
        timestamp2 = dynamic2['desc']['timestamp']
        if dynamic_id1 != dynamic_id2 and int(time.time()) - timestamp2 < 3600:
            return True
    return False


def check_dynamic(dynamic):
    desc = dynamic['desc']
    card = json.loads(dynamic['card'])
    type = desc['type']
    rid = desc['rid']
    dynamic_id = desc['dynamic_id']
    uname = desc['user_profile']['info']['uname']
    string = ''
    res_type = 0
    res_rid = 0
    if (type == 1):
        orig_type = desc['orig_type']
        content = card['item']['content']
        if (orig_type == 2):
            string = '[{}][转发图片动态][{}]'.format(uname, content)
        elif (orig_type == 4):
            string = '[{}][转发文字动态][{}]'.format(uname, content)
        elif (orig_type == 8):
            string = '[{}][转发视频动态][{}]'.format(uname, content)
            res_type = 17
            res_rid = dynamic_id
        elif (orig_type == 4200):
            string = '[{}][转发直播间][{}]'.format(uname, content)
        elif (orig_type == 64):
            string = '[{}][转发专栏动态][{}]'.format(uname, content)
            res_type = 17
            res_rid = dynamic_id
        elif (orig_type == 4300):
            string = '[{}][转发收藏夹][{}]'.format(uname, content)
        elif (orig_type == 2048):
            string = '[{}][转发挂件动态][{}]'.format(uname, content)
        elif (orig_type == 1024):
            string = '[{}][转发失效动态][{}]'.format(uname, content)
    elif (type == 2):
        description = card['item']['description']
        string = '[{}][发表图片动态][{}]'.format(uname, description)
        res_type = 11
        res_rid = rid
    elif (type == 4):
        content = card['item']['content']
        string = '[{}][发表文字动态][{}]'.format(uname, content)
        res_type = 17
        res_rid = dynamic_id
    elif (type == 8):
        bvid = desc['bvid']
        title = card['title']
        dynamic = card['dynamic']
        string = '[{}][发表视频动态][{}][{}][{}]'.format(uname, title, dynamic, bvid)
        res_type = 1
        res_rid = rid
    elif (type == 2048):
        content = card['vest']['content']
        string = '[{}][发表挂件动态][{}]'.format(uname, content)
    elif (type == 64):
        title = card['title']
        string = '[{}][发表专栏动态][{}]'.format(uname, title)
        res_type = 12
        res_rid = rid
    print('[{}]{}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), string))
    return res_type, res_rid


def get_reply_data(type, oid):
    url = 'https://api.bilibili.com/x/v2/reply/main?type={}&oid={}'.format(type, oid)
    try:
        resp = requests.get(url=url, headers=headers)
        resp_json = json.loads(resp.text)
        print('[{}]{}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), resp_json['data'])[0:60])
        return resp_json['data']
    except Exception as e:
        print(e)


def check_reply(uid, type, rid):
    for i in range(0, 60):
        try:
            time.sleep(2)
            data = get_reply_data(type, rid)
            reply_list = []
            if data['replies']:
                reply_list.extend(data['replies'])
            if data['top']['upper']:
                reply_list.append(data['top']['upper'])
            if data['top_replies']:
                reply_list.extend(data['top_replies'])
            for reply in reply_list:
                if reply['mid'] == uid:
                    message = reply['content']['message']
                    print('[{}]{}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))
                    return True
        except Exception as e:
            print(e)


def monitor(uid):
    dynamic_list = get_dynamic_list(uid)
    old_dynamic = get_last_dynamic(dynamic_list)
    while True:
        try:
            time.sleep(4)
            now = datetime.datetime.now().strftime('%H:%M:%S')
            if '10:00:00' < now < '24:00:00':
                dynamic_list = get_dynamic_list(uid)
                new_dynamic = get_last_dynamic(dynamic_list)
                if compare_dynamic(old_dynamic, new_dynamic):
                    old_dynamic = new_dynamic
                    type, rid = check_dynamic(new_dynamic)
                    if type and rid:
                        check_reply(uid, type, rid)
            if '09:59:00' < now < '10:00:00':
                dynamic_list = get_dynamic_list(uid)
                old_dynamic = get_last_dynamic(dynamic_list)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    uid = ''
    monitor(uid)
