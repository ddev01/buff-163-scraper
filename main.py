import requests
import json
import sqlite3
from datetime import datetime, timedelta
import math
import time
from cookieModule import cookieFormatter
from cookie import cookie #Set an active cookie inside a cookie.py file like cookie=''

con = sqlite3.connect('main.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS items(id int PRIMARY KEY, buyURL text, goods_id int, market_hash_name text, pain
twear real, priceRMB real, priceUSD real, paintseed int, has_sticker text, stickercount real, total_sticker_price real, 
sticker_0_name text, sticker_0_id int, sticker_0_price real, sticker_1_name text, sticker_1_id int, sticker_1
_price real, sticker_2_name text, sticker_2_id int, sticker_2_price real, 
sticker_3_name text, sticker_3_id int, sticker_3_price real, time_checked text, inspect_en_url text)''')

# sticker prices https://buff.163.com/api/market/goods?game=csgo&page_num=99999999&sort_by=price.asc&category_group=sticker
# backup reqeust link https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=33974&extra_tag_ids=non_empty&page_size=80

cookieDict = cookieFormatter(cookie) #Function that converts string cookie to correct dictionary format.
yenToUsd = 0.136955 #1 RMB to USD. Used to convert maxPrizeUSD into a RMB value
maxPrizeUSD = 10 #Max item price (&max_price=)
maxPrizeRMB = str(round(maxPrizeUSD / yenToUsd))
count = 0
pageCount = 1
# 857556,
# 857652,
# 857534,
# 857554,
# 775674,
# 775146,
# 775853,
# 775142,
# 774893,
# 775915,
# 33889,
# 33893,
# 33891,
# 33873,
# 33874,
# 871772
#&sort_by=price.desc

#List with id's of items to scrape. Find IDs in link for example AK47 Slate FN link is https://buff.163.com/goods/857652?from=market#tab=selling so ID is 857652
goods_id_list = [
33872,#blue lam FN
33874,#blue lam mw
33873,#blue lam ft
# 33875,#blue lam ww
# 857652,#slate fn
# 857534,#slate mw
# 857550,#slate ft
# 857556,#slate ww
# 857554,#slate bs
# 857698,#slate bs ST
# 857637,#slate ww ST
# 857627,#slate ft ST
# 775895,#purple FN
# 775915,#purple MW
# 774893,#pruple FT
# 775853,#purple ww
# 775142, #purple bs
]
progressCount = 1
timeStarted = datetime.now()
avgTime = timedelta(seconds=0)
avgItems = 0
effList = []
for idLoop in goods_id_list: #For goods ID in x
    itemlist = [] #Holds all items
    scrapeName = ''
    print('[{}/{}]Starting loop'.format(progressCount, len(goods_id_list)))
    pageCount = 1
    loopStart = datetime.now()
    while True:
        pageNum = '&page_num=' + str(pageCount)
        timeBeforeReq = datetime.now()
        #reqURL example https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=33872&page_size=100&extra_tag_ids=non_empty&max_price=140&page_num=1
        #non_empty means only items that have one or more stickers.
        reqUrl = 'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={}&page_size=100&extra_tag_ids=non_empty&max_price='.format(idLoop) + maxPrizeRMB + pageNum #Example URL
        r = requests.get(reqUrl,cookies=cookieDict)
        timeAfterReq = datetime.now()
        temp = r.json()
        try: #We try except because we don't know how many pages to scrape so we catch except list index error to know we scraped all pages.
            pageCount += 1
            goods_id = list(temp['data']['goods_infos'])[0]
            market_hash_name = temp['data']['goods_infos'][str(goods_id)]['market_hash_name']
            scrapeName = temp['data']['goods_infos'][str(goods_id)]['market_hash_name']
            stickers = False
            for item in temp['data']['items']:
                priceRMB = item['price']
                priceUSD = round(float(item['price']) * yenToUsd, 2)
                id = item['id']
                paintwear = item['asset_info']['paintwear']
                paintseed = item['asset_info']['info']['paintseed']
                paintMin = math.floor(float(paintwear) * 10000) / 10000
                paintMax = math.ceil(float(paintwear) * 10000) / 10000
                buyURL = 'https://buff.163.com/goods/{}#tab=selling&max_price={}&paintseed={}&min_paintwear={}&max_paintwear={}'.format(goods_id,maxPrizeUSD,paintseed,paintMin,paintMax)
                can_use_inspect_trn_url = item['can_use_inspect_trn_url']
                inspecturl = ''
                time_checked = datetime.now().replace(second=0, microsecond=0)
                stickerCount = 0
                sticker_0_name = ''
                sticker_0_id = 0
                sticker_0_price = 0
                sticker_1_name = ''
                sticker_1_id = 0
                sticker_1_price = 0
                sticker_2_name = ''
                sticker_2_id = 0
                sticker_2_price = 0
                sticker_3_name = ''
                sticker_3_id = 0
                sticker_3_price = 0
                has_sticker = 'False'
                if can_use_inspect_trn_url == True:
                    try:
                        inspecturl = item['asset_info']['info']['inspect_en_url']
                    except:
                        print('KeyError: inspect_en_url')
                        print(item)
                # else:
                #     print('No inspect URL')
                if item['asset_info']['info']['stickers']:
                    has_sticker = 'True'
                    for sticker in item['asset_info']['info']['stickers']:
                        stickerCount += 1
                        try: #We run stickerscraper.py once to make a db with all stickers and prices to prevent excessive requests getting sticker price for
                             #items every time. We select those stickers from sticker table but sometimes buff API returns sticker name in chinese
                             #and item can't be found in DB because that sticker name is stored in english. We catch the error in except and set that sticker price to 0
                            get_price_query = cur.execute('SELECT sell_reference_price FROM stickers WHERE market_hash_name=?', ('Sticker | ' + sticker['name'],))
                            # print('Sticker | ' + sticker['name'])
                            # print(sticker)
                            # print(item)
                            # print(buyURL)
                            temp_sticker_price = cur.fetchall()[0][0]
                            sticker_price = round(temp_sticker_price * yenToUsd, 2)
                        except:
                            sticker_price = 0
                            # print('IndexError: list index out of range')
                            # print('sticker_price = cur.fetchall()[0][0]')
                            # # print(cur.fetchall()[0][0])
                            # print('Sticker | ' + sticker['name'])
                            # print(sticker)
                            # print(item)
                            # print(buyURL)
                            continue
                        if sticker['slot'] == 0:
                            sticker_0_name = sticker['name']
                            sticker_0_id = sticker['sticker_id']
                            sticker_0_price = sticker_price
                        if sticker['slot'] == 1:
                            sticker_1_name = sticker['name']
                            sticker_1_id = sticker['sticker_id']
                            sticker_1_price = sticker_price
                        if sticker['slot'] == 2:
                            sticker_2_name = sticker['name']
                            sticker_2_id = sticker['sticker_id']
                            sticker_2_price = sticker_price
                        if sticker['slot'] == 3:
                            sticker_3_name = sticker['name']
                            sticker_3_id = sticker['sticker_id']
                            sticker_3_price = sticker_price
                total_sticker_price = round(sticker_0_price + sticker_1_price + sticker_2_price + sticker_3_price, 2)
                temptuple = (id, buyURL, goods_id, market_hash_name, paintwear, priceRMB, priceUSD, int(paintseed), has_sticker, stickerCount, total_sticker_price,
                             sticker_0_name, sticker_0_id, sticker_0_price, sticker_1_name, sticker_1_id, sticker_1_price, sticker_2_name, sticker_2_id, sticker_2_price, sticker_3_name, sticker_3_id, sticker_3_price,
                             time_checked, inspecturl)
                itemlist.append(temptuple)
        except:
            #Finished scraping all pages because list index error thrown. If you only get this in console, you probably have an expired cookie
            print("[{}/{}]scraped all pages / error".format(progressCount, len(goods_id_list)))
            break
        #Progress print like [1/3] AK-47 | Blue Laminate (Factory New) Len of itemlist: 100
        #Where 1/3 is busy scraping 1st item out of 3, name of item being scraped and how many items are currently in itemlist var which will be appended when all items scraped
        print('[{}/{}] {} Len of itemlist: {}'.format(progressCount, len(goods_id_list),market_hash_name, len(itemlist)))
    #After scraping all listings of an item it will append that in the database en move onto the next item.
    print('[{}/{}]Inserting {} {} into database.'.format(progressCount, len(goods_id_list), len(itemlist), scrapeName))
    cur.executemany("INSERT OR IGNORE INTO items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",itemlist)
    con.commit()
    progressCount += 1
    loopTimeTotal = datetime.now() - loopStart
    avgTime += loopTimeTotal
    avgItems += len(itemlist)
    #This is a tuple holding some efficiency information like how many items were scraped, how long it took, how many items per second that amounts to etc.
    loopEffTuple = {
        'itemName': market_hash_name,
        'itemCount': len(itemlist),
        'timeTotal': loopTimeTotal,
        'timePerItem': round(len(itemlist) / loopTimeTotal.total_seconds(),2),
        'requestTime': timeAfterReq - timeBeforeReq,
        'loopTimeMinusReqTime': loopTimeTotal - (timeAfterReq - timeBeforeReq)
    }
    effList.append(loopEffTuple)
    # print("name", market_hash_name, "time", loopTimeTotal, "tuple", loopEffTuple)

con.close()
print("Runtime: ", datetime.now() - timeStarted)
print("total",round(avgItems / avgTime.total_seconds(),2))
for item in effList:
    print(item)

