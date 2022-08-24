import json
import aiohttp
import nonebot
from bs4 import BeautifulSoup
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot_plugin_apscheduler import scheduler


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
    'Cookie': 'SUB=_'
}
hotlist = on_command('hotlist', rule=to_me(), aliases={'热榜'}, priority=1)
wb_list = []
zh_list = []
bd_list = []


@hotlist.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg('mode', args)


@hotlist.got('mode', prompt='输入查询平台')
async def handle_mode(mode: Message = Arg(), mode_name: str = ArgPlainText('mode')):
    if mode_name not in ['微博', '知乎', '百度']:
        await hotlist.reject(mode.template('暂不支持，重新输入！'))
    hot_list = await get_hot_list(mode_name)
    await hotlist.finish(hot_list)


async def get_hot_list(mode: str) -> str:
    res = ''
    num = 0
    res_list = []
    if mode == '微博':
        res_list = await get_wb_hot(10)
    if mode == '知乎':
        res_list = await get_zh_hot(10)
    if mode == '百度':
        res_list = await get_bd_hot(10)
    for hot in res_list:
        num += 1
        res += str(num) + '.' + str(hot) + '\n'
    return res


async def send_msg(message):
    try:
        driver = nonebot.get_driver()
        groups = driver.config.groups
        bots = nonebot.get_bots()
        bot = next(iter(bots.values()))
        for group_id in groups:
            await bot.send_group_msg(group_id=group_id, message=message)
    except Exception as e:
        print(e)


@scheduler.scheduled_job('cron', hour='*/1', id='hotlist')
async def monitor():
    global wb_list, zh_list, bd_list
    if not (wb_list and zh_list and bd_list):
        wb_list = get_wb_hot(5)
        zh_list = get_zh_hot(5)
        bd_list = get_bd_hot(5)
    hot_list = []
    res = ''
    wb_new = await get_wb_hot(5)
    for wb in wb_new:
        if wb not in wb_list:
            hot_list.append('[微博]' + wb)
            wb_list.append(wb)
    zh_new = await get_zh_hot(5)
    for zh in zh_new:
        if zh not in zh_list:
            hot_list.append('[知乎]' + zh)
            zh_list.append(zh)
    bd_new = await get_bd_hot(5)
    for bd in bd_new:
        if bd not in bd_list:
            hot_list.append('[百度]' + bd)
            bd_list.append(bd)
    for hot in hot_list:
        res += str(hot) + '\n'
    if res:
        await send_msg(res)


async def get_wb_hot(num):
    res_list = []
    url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    try:
        resp = await get(url)
        soup = BeautifulSoup(resp, 'html.parser')
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


async def get_zh_hot(num):
    res_list = []
    url = 'https://api.zhihu.com/topstory/hot-list?limit10'
    try:
        resp = await get(url)
        resp_json = json.loads(resp)
        hot_list = resp_json['data']
        for i in range(num):
            hot = hot_list[i]['target']['title']
            res_list.append(hot)
    except Exception as e:
        print(e)
    return res_list


async def get_bd_hot(num):
    res_list = []
    url = 'https://top.baidu.com/board?tab=realtime'
    try:
        resp = await get(url)
        soup = BeautifulSoup(resp, 'html.parser')
        hot_list = soup.select('div.c-single-text-ellipsis')
        for i in range(num):
            hot = hot_list[i].text.strip()
            res_list.append(hot)
    except Exception as e:
        print(e)
    return res_list


async def get(url):
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                return await resp.text()
    except Exception:
        return ''
