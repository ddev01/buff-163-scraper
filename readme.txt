pip install requirements.txt
Add a cookie inside cookie.py between the ''.
Run stickerscraper.py to populate DB with stickers & prices (make sure to drop sticker table and rescrape once a while to keep prices up to date).
View scraped items with something like https://sqlitebrowser.org/

in main.py make sure to  set:
maxPrizeUSD = 10 #To whatever max price in usd
yenToUsd = 0.136955 #Update RMB to USD rate incase of change
goods_id_list = []#populate with goods ID's to scrape

If you don't know how to find your cookie:
check findcookie.png
1. Login to buff.163.com
2. Open browser inspect by right clicking anywhere on the page and clicking inspect or use CTRL + SHIFT + I
3. Click network
4. Refresh the page.
5. Search for buff
6. click on 'buff.163.com'
7. under headers find 'request headers'
8. right click on cookie and click copy.
9. Paste this into cookie.py between the ''
10. If you don't know how to find your cookie I don't think you will know how to use this bot at all.