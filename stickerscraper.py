import requests
import json
import sqlite3
from datetime import datetime
from datetime import timedelta
import time
import random
from cookieModule import cookieFormatter
from cookie import cookie #Set an active cookie inside a cookie.py file like cookie=''

con = sqlite3.connect('main.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS stickers(id int PRIMARY KEY, market_hash_name text, sell_min_price real, sell_reference_price real, sell_num int, steam_price real, steam_price_cny real, buy_num int, buy_max_price real, time_checked text, original_icon_url text, steam_market_url text)''')
cookieDict = cookieFormatter(cookie)

def stickerPageCount():
    r = requests.get(
        'https://buff.163.com/api/market/goods?game=csgo&sort_by=price.asc&category_group=sticker&page_size=80&page_num=1',
        cookies=cookieDict)
    temp = r.json()
    return temp['data']['total_page'] + 1 #Returns page count + 1 because in range goes up to and doesnt include

stickerList = []

for x in range(1, stickerPageCount()):
    r = requests.get('https://buff.163.com/api/market/goods?game=csgo&sort_by=price.asc&category_group=sticker&page_size=80&page_num=' + str(x), cookies=cookieDict)
    temp = r.json()
    for item in temp['data']['items']:
        buy_max_price = item['buy_max_price']#
        buy_num = item['buy_num']#
        original_icon_url = item['goods_info']['original_icon_url']
        steam_price = item['goods_info']['steam_price']#
        steam_price_cny = item['goods_info']['steam_price_cny']#
        market_hash_name = item['market_hash_name']#
        id = item['id']#
        sell_min_price = item['sell_min_price'] #
        sell_num = item['sell_num']#
        sell_reference_price = item['sell_reference_price']#
        steam_market_url = item['steam_market_url']
        time_checked = datetime.now().replace(second=0, microsecond=0)
        stickerList.append((id, market_hash_name, sell_min_price, sell_reference_price, sell_num, steam_price, steam_price_cny, buy_num, buy_max_price, time_checked, original_icon_url, steam_market_url))
    print('Finished:', x, 'pages.')
print('Executing many command...')
cur.executemany("INSERT OR IGNORE INTO stickers VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",stickerList)
con.commit()
con.close()
print('Succesfully scraped.')