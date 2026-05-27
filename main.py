from dotenv import load_dotenv
import os

# .env ファイルをロード
load_dotenv()

# 環境変数の取得
secret_key = os.getenv("SECRET_KEY")
database_url = os.getenv("DATABASE_URL")

print(f"Secret Key: {secret_key}")
print(f"Database URL: {database_url}")






from flask import render_template





#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template 
from flask import request
app = Flask(__name__)
import requests
import logging
# from amazon.paapi import AmazonAPI
# from amazon.paapi import SearchItemsResource
from flask import session
from flask import make_response
from logging.handlers import RotatingFileHandler
from multiprocessing.pool import ThreadPool
import time
import threading
from time import sleep
from bs4 import BeautifulSoup
from datetime import timedelta
import json
from concurrent.futures import ThreadPoolExecutor

# from page98 import app


# log_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(threadName)s] %(message)s')
# handler = RotatingFileHandler('app_error.log', maxBytes=10000, backupCount=1)
# handler.setLevel(logging.ERROR)
# handler.setFormatter(log_formatter)
# app.logger.addHandler(handler)

# @app.route('/')
# def index():
#     return render_template('index2.html')
@app.route('/')
def index():
    envtest=os.getenv("SECRET_KEY")
    return render_template(
        'index.html', envtest=envtest
    )


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    keyword = query
    url = "https://app.rakuten.co.jp/services/api/BooksTotal/Search/20170404"
    param = {
        "applicationId" : "1038728018402819690",
        "affiliateId": "21715c73.23fd5977.21715c74.a6751da5",
        "keyword" : keyword,
        "format" : "json",
        "booksGenreId":"001",
        "hits" : "10",

    }
    result = requests.get(url, param)
    json_result = result.json()     
    return render_template('search.html', results=json_result)

# @app.route('/search2', methods=['GET'])
# def search2(): 
#     # try:
#     query2 = request.args.get('query2', '')
    
#     results2 = perform_search2(query2)
#     bookoff = bookoff_search(query2)
#     netoff =netoff_search(query2)
#     rakuten_r = rak_pricelow(query2)
    
#     try:
#         systemid = session['systemid']
        
#         lib_results,reserveurl = bookstatus(systemid,query2)
        
#         return render_template('search2.html', results2=results2, bookoff=bookoff,netoff=netoff,lib_results=lib_results, rakuten_r=rakuten_r,systemid=systemid,reserveurl=reserveurl)

#     except:
#         systemid=""
        
#         lib_results = ""
#         return render_template('search2.html', results2=results2, bookoff=bookoff,netoff=netoff,lib_results=lib_results, rakuten_r=rakuten_r,systemid=systemid)


@app.route('/search2', methods=['GET'])
def search2():
    query2 = request.args.get('query2', '')

    with ThreadPoolExecutor() as executor:
        # 並列処理で関数を実行し、結果を取得する
        results2_future = executor.submit(perform_search2, query2)
        bookoff_future = executor.submit(bookoff_search, query2)
        netoff_future = executor.submit(netoff_search, query2)
        rakuten_r_future = executor.submit(rak_pricelow, query2)
        
        try:
            systemid = session['systemid']
            lib_results_future = executor.submit(bookstatus, systemid, query2)
            lib_results, reserveurl = lib_results_future.result()
        except:
            systemid = ""
            lib_results = ""
            reserveurl = ""
        
        # すべての処理が完了するまで待機
        results2 = results2_future.result()
        bookoff = bookoff_future.result()
        netoff = netoff_future.result()
        rakuten_r = rakuten_r_future.result()

    return render_template('search2.html', results2=results2, bookoff=bookoff, netoff=netoff, lib_results=lib_results, rakuten_r=rakuten_r, systemid=systemid, reserveurl=reserveurl)

def perform_search2(query2):
    keyword2 = query2
    # 楽天商品検索API 
    url = "https://app.rakuten.co.jp/services/api/BooksTotal/Search/20170404"
    param = {
        "applicationId" : "1038728018402819690",
        "affiliateId": "21715c73.23fd5977.21715c74.a6751da5",
        "keyword" : keyword2 ,
        "format" : "json", 
        "booksGenreId"  : "001",
        "hits" : "10",
    }
    # APIを実行して結果を取得する
    result = requests.get(url, param)
    # jsonにデコードして出力する
    json_result = result.json()
    return json_result


def bookoff_search(query2):
    def getsite_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # CSSセレクターを使って該当する要素を取得
                link_element = soup.select_one("#items_field > div > div:nth-child(1) > div > div.productItem__detail > a")
                # 要素が存在するか確認してURLを取得
                if link_element:
                    url = link_element.get('href')
                    return url
                else:
                    return "Error: URL not found"
            else:
                return "Error: Unable to retrieve URL"
        except Exception as e:
            return "Error: " + str(e)
    code = query2
    

    bookoffurl = 'https://shopping.bookoff.co.jp/search/keyword/'+ code
    url = getsite_url(bookoffurl)
    
    urlnum= url[-10:]
    usedURL="https://shopping.bookoff.co.jp/used/"+urlnum

    response2 = requests.get(usedURL)
    soup2 = BeautifulSoup(response2.text, 'html.parser')
    stock_info = soup2.find('span', class_='')
    try:
   
        if stock_info:
            stock_text = stock_info.text
        else:
            # 在庫情報が<p>タグ内にある場合
            stock_info = soup2.find('p', class_='productInformation__stock')
            stock_text = stock_info.find('span', class_='productItem__stock--alert').text
        # price = soup2.find('span', class_='productInformation__price--large').text   
        price = soup2.find('span', class_='.productItem__price').text   
        # bookoffprint=str(stock_text)+str(price)
        bookoffprint= str(price)
        
        return bookoffprint
    except:
        bookoffprint=""
        return bookoffprint
def netoff_search(query2):
    url = 'https://www.netoff.co.jp/cmdtyallsearch?word=' + query2
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        link_element = soup.select_one('#dataId1 > ul > li > dl > dd:nth-child(1) > ul > ul > li.titleBox > ul > li:nth-child(1) > p > a')
        href_value = link_element['href']
        product_page = requests.get(href_value)
        product_soup = BeautifulSoup(product_page.content, 'html.parser')

        stock_element = product_soup.select_one('#main > div.itemExp.mediaDetail.clearfix > div.description > div > div:nth-child(2) > div.priceGuarantyCp > div.stockArea > div.cartBtnArea > div:nth-child(1) > span')
        netoffstock = "在庫あり" if stock_element and stock_element.text.strip() == "在庫あり" else "在庫なし"

        price_element = product_soup.select_one('#orange1 > p.price_text2')
        netoff_price = price_element.text.strip() if price_element else "エラー"
        netoff_price = netoff_price.replace("(税込)", "")
        netoffprint = str(netoffstock)+str(netoff_price)
    except Exception as e:
        netoffprint ="取得できません"
    return netoffprint


def rak_pricelow(query2):
    
    # 楽天商品検索API (BooksGenre/Search/)のURL
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"

    keyword = query2
    # 9784815624255
    # code = "9784815624255"
    # code = "9784798166469"
    # URLのパラメータ
    param = {
        # 前手順で取得したアプリIDを設定する
        "applicationId" : "1038728018402819690",
        "affiliateId": "21715c73.23fd5977.21715c74.a6751da5",
        "genreId" :  "200162",
        "format" : "json",
        "keyword" : keyword,
        "hits":7,
        "sort":"+itemPrice"
    
    }

    # APIを実行して結果を取得する
    result = requests.get(url, param)# APIを実行して結果を取得する

    # jsonにデコードして出力する
    json_result = result.json()
    return json_result





@app.route('/policy')
def policy():
    return render_template(
        'policy.html')
    


def bookstatus(systemid,query2):
    try:
        url = "https://api.calil.jp/check"
        
        params = {
            "appkey": "edf3f46bcd4860e71d352082d98b8aab",
            "isbn": query2,
            "systemid": systemid,
            "callback": "no"
        }
        
        # APIを実行して結果を取得する
        result = requests.get(url, params=params)
        
        rjson = result.text.lstrip("callback(").rstrip(");")
        rjson = '{"data":' + rjson + "}"
        data = json.loads(rjson)
        returncheck = data["data"]["continue"]
        
        while True:
            result = requests.get(url, params=params)
            rjson = result.text.lstrip("callback(").rstrip(");")
            rjson = '{"data":' + rjson + "}"
            data = json.loads(rjson)
            returncheck = data["data"]["continue"]
            if returncheck == 0:
                break
            else:
                while True:
                    session = data["data"]["session"]
                    
                    params = {
                        "appkey": "edf3f46bcd4860e71d352082d98b8aab",
                        "session": session,
                    }
                    # APIを実行して結果を取得する
                    result = requests.get(url, params=params)
                    
                    rjson = result.text.lstrip("callback(").rstrip(");")
                    rjson = '{"data":' + rjson + "}"
                    data = json.loads(rjson)
                    returncheck = data["data"]["continue"]
                    if returncheck == 0:
                        break
                    else:
                        time.sleep(2)
                        
        lib_results = data["data"]["books"][query2][systemid]["libkey"]

        reserveurl= data["data"]["books"][query2][systemid]["reserveurl"]
        
        return lib_results,reserveurl
    except:
        lib_results="エラー"
        return lib_results    
    

app.secret_key = 'my_key'
app.permanent_session_lifetime = timedelta(days=365)
@app.route('/libget', methods=['GET', 'POST'])
def libget():
    # 初期値

   
    systemid = request.form['systemid']
    session['systemid'] = systemid
    libid =session['systemid']
        

    return render_template('save.html',libid =libid)         


@app.route('/prefecture')
def prefecture():
    return render_template(
        'prefecture.html', prefectures=prefectures)


@app.route('/prefecture/<prefecture_name>')
def city(prefecture_name):
    cities_in_prefecture = cities.get(prefecture_name)
    return render_template('city.html', prefecture=prefecture_name, cities=cities_in_prefecture)

@app.route('/libs', methods=['GET'])
def libs():
    key1 = request.args.get('key1')
    key2 = request.args.get('key2')
    results = lib_search(key1,key2)  
    return render_template('libs.html', libs=results)
def lib_search(key1,key2):
    pref = key1
    city = key2  
    endpoint = "https://api.calil.jp/library"
    params={
        "appkey":"edf3f46bcd4860e71d352082d98b8aab", 
        "pref":pref,
        "city":city,
        "format":"json",
      
    }

    result = requests.get(endpoint,params=params)
    rjson = result.text.lstrip("callback(").rstrip(");")
    rjson = '{"data": ' + rjson + '}'

    # JSON文字列をPythonの辞書オブジェクトに変換
    data = json.loads(rjson)

    return data    

prefectures = ["北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島", "茨城", "栃木", "群馬", "埼玉", "千葉", "東京", "神奈川", "新潟", "富山", "石川", "福井", "山梨", "長野", "岐阜", "静岡", "愛知", "三重", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山", "鳥取", "島根", "岡山", "広島", "山口", "徳島", "香川", "愛媛", "高知", "福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"]

cities = {
    "北海道": ["赤平市", "旭川市", "芦別市", "足寄町", "厚岸町", "厚真町", "網走市", "安平町", "池田町", "石狩市", "今金町", "岩内町", "岩見沢市", "歌志内市", "浦河町", "浦幌町", "枝幸町", "恵庭市", "江別市", "遠軽町", "雄武町", "大空町", "置戸町", "興部町", "長万部町", "小樽市", "音更町", "帯広市", "小平町", "上川町", "上士幌町", "上富良野町", "北広島市", "北見市", "京極町", "共和町", "清里町", "釧路市", "倶知安町", "栗山町", "黒松内町", "訓子府町", "剣淵町", "小清水町", "札幌市", "様似町", "更別村", "猿払村", "佐呂間町", "標茶町", "士別市", "標津町", "士幌町", "清水町", "下川町", "斜里町", "白老町", "新得町", "新十津川町", "新ひだか町", "砂川市", "せたな町", "大樹町", "鷹栖町", "滝川市", "滝上町", "伊達市", "千歳市", "月形町", "津別町", "鶴居村", "弟子屈町", "当別町", "当麻町", "苫小牧市", "豊頃町", "豊富町", "奈井江町", "中札内村", "中標津町", "中頓別町", "中富良野町", "長沼町", "名寄市", "南幌町", "新冠町", "ニセコ町", "沼田町", "根室市", "登別市", "函館市", "羽幌町", "浜頓別町", "東神楽町", "東川町", "日高町", "広尾町", "美瑛町", "美唄市", "美幌町", "平取町", "比布町", "深川市", "福島町", "富良野市", "古平町", "別海町", "北斗市", "幌加内町", "幌延町", "本別町", "幕別町", "松前町", "三笠市", "むかわ町", "室蘭市", "芽室町", "紋別市", "八雲町", "夕張市", "湧別町", "余市町", "羅臼町", "蘭越町", "利尻町", "留萌市", "稚内市", "和寒町"]
    ,"青森": ["青森市", "おいらせ町", "大鰐町", "黒石市", "五所川原市", "五戸町", "三戸町", "七戸町", "田子町", "つがる市", "十和田市", "中泊町", "南部町", "野辺地町", "階上町", "八戸市", "平川市", "弘前市", "藤崎町", "三沢市", "むつ市", "六戸町", "六ヶ所村"]
    ,"岩手":["一関市", "一戸町", "岩泉町", "岩手町", "奥州市", "大槌町", "大船渡市", "金ケ崎町", "釜石市", "軽米町", "北上市", "久慈市", "雫石町", "紫波町", "滝沢市", "田野畑村", "遠野市", "二戸市", "野田村", "八幡平市", "花巻市", "平泉町", "洋野町", "普代村", "宮古市", "盛岡市", "矢巾町", "山田町", "陸前高田市"]
    ,"秋田":["秋田市", "井川町", "羽後町", "大潟村", "大館市", "男鹿市", "潟上市", "鹿角市", "上小阿仁村", "北秋田市", "小坂町", "五城目町", "仙北市", "大仙市", "かほ市", "能代市", "八郎潟町", "東成瀬村", "美郷町"]
    ,"宮城": ["石巻市", "岩沼市", "大河原町", "大崎市", "角田市", "加美町", "栗原市", "気仙沼市", "蔵王町", "塩竈市", "色麻町", "柴田町", "白石市", "仙台市", "大和町", "多賀城市", "富谷市", "登米市", "名取市", "東松島市", "美里町", "南三陸町", "利府町", "亘理町"]
    ,"山形": ["朝日町", "大石田町", "大江町", "尾花沢市", "河北町", "上山市", "川西町", "酒田市", "寒河江市", "庄内町", "白鷹町", "新庄市", "高畠町", "鶴岡市", "天童市", "中山町", "長井市", "南陽市", "西川町", "東根市", "真室川町", "村山市", "山形市", "遊佐町", "米沢市"]
    ,"福島" :["会津美里町", "会津若松市", "石川町", "泉崎村", "猪苗代町", "いわき市", "大熊町", "小野町","鏡石町", "喜多方市", "国見町", "桑折町", "郡山市", "白河市", "新地町", "須賀川市", "相馬市","棚倉町", "田村市", "伊達市", "富岡町", "浪江町", "西会津町", "西郷村", "二本松市","塙町", "広野町", "福島市", "双葉町", "南会津町", "南相馬市", "三春町", "本宮市","矢吹町", "矢祭町"]
    ,"茨城": ["阿見町", "石岡市", "潮来市", "稲敷市", "茨城町", "牛久市", "大洗町", "小美玉市", "笠間市", "鹿嶋市", "かすみがうら市", "神栖市", "河内町", "北茨城市", "古河市", "桜川市", "下妻市", "城里町", "常総市", "高萩市", "大子町", "筑西市", "つくば市", "つくばみらい市", "土浦市", "東海村", "利根町", "取手市", "那珂市", "行方市", "坂東市", "常陸太田市", "常陸大宮市", "日立市", "ひたちなか市", "鉾田市", "水戸市", "美浦村", "守谷市", "八千代町", "結城市", "龍ケ崎市"]
    ,"栃木":["足利市", "市貝町", "宇都宮市", "大田原市", "小山市", "鹿沼市", "上三川町", "さくら市", "佐野市", "塩谷町", "下野市", "高根沢町", "栃木市", "那珂川町", "那須烏山市", "那須塩原市", "那須町", "日光市", "野木町", "芳賀町", "益子町", "壬生町", "真岡市", "茂木町", "矢板市"]
    ,"群馬": ["安中市", "伊勢崎市", "板倉町", "上野村", "邑楽町", "大泉町", "太田市", "甘楽町", "桐生市", "渋川市", "高崎市", "館林市", "玉村町", "千代田町", "富岡市", "中之条町", "長野原町", "沼田市", "藤岡市", "前橋市", "みどり市", "明和町", "吉岡町"]
    ,"埼玉": ["上尾市", "朝霞市", "伊奈町", "入間市", "小鹿野町", "小川町", "桶川市", "越生町", "春日部市", "加須市", "神川町", "上里町", "川口市", "川越市", "川島町", "北本市", "行田市", "久喜市", "熊谷市", "鴻巣市", "越谷市", "さいたま市", "坂戸市", "幸手市", "狭山市", "志木市", "白岡市", "杉戸町", "草加市", "秩父市", "鶴ヶ島市", "ときがわ町", "所沢市", "戸田市", "滑川町", "新座市", "蓮田市", "鳩山町", "羽生市", "飯能市", "東秩父村", "東松山市", "日高市", "深谷市", "富士見市", "ふじみ野市", "本庄市", "三郷市", "美里町", "宮代町", "三芳町", "毛呂山町", "八潮市", "横瀬町", "吉川市", "吉見町", "寄居町", "嵐山町", "和光市", "蕨市"]
    ,"千葉": ["旭市", "我孫子市", "市川市", "市原市", "印西市", "浦安市", "大網白里市", "大多喜町", "柏市", "勝浦市", "香取市", "鎌ケ谷市", "鴨川市", "木更津市", "君津市", "神崎町", "栄町", "佐倉市", "山武市", "酒々井町", "芝山町", "白井市", "匝瑳市", "袖ケ浦市", "多古町", "館山市", "千葉市", "銚子市", "長生村", "東金市", "東庄町", "富里市", "長柄町", "流山市", "習志野市", "成田市", "野田市", "富津市", "船橋市", "松戸市", "南房総市", "睦沢町", "茂原市", "八街市", "八千代市", "横芝光町", "四街道市"]
    ,"東京": ["昭島市", "あきる野市", "足立区", "荒川区", "板橋区", "稲城市", "江戸川区", "青梅市", "大田区", "奥多摩町", "葛飾区", "北区", "清瀬市", "国立市", "江東区", "小金井市", "国分寺市", "小平市", "狛江市", "品川区", "渋谷区", "新宿区", "杉並区", "墨田区", "世田谷区", "台東区", "立川市", "多摩市", "中央区", "調布市", "千代田区", "豊島区", "中野区", "新島村", "西東京市", "練馬区", "八王子市", "羽村市", "東久留米市", "東村山市", "東大和市", "日野市", "日の出町", "府中市", "福生市", "文京区", "町田市", "瑞穂町", "三鷹市", "港区", "武蔵野市", "武蔵村山市", "目黒区"]
    ,"神奈川": ["愛川町", "厚木市", "綾瀬市", "伊勢原市", "海老名市", "大磯町", "大井町", "小田原市", "開成町", "鎌倉市", "川崎市", "清川村", "相模原市", "寒川町", "座間市", "逗子市", "茅ヶ崎市", "中井町", "二宮町", "箱根町", "秦野市", "葉山町", "平塚市", "藤沢市", "松田町", "真鶴町", "三浦市", "南足柄市", "山北町", "大和市", "湯河原町", "横須賀市", "横浜市"]
    ,"新潟":["阿賀野市", "阿賀町", "粟島浦村", "糸魚川市", "魚沼市", "小千谷市", "柏崎市", "加茂市", "刈羽村", "五泉市", "佐渡市", "三条市", "新発田市", "上越市", "聖籠町", "関川村", "胎内市", "津南町", "燕市", "十日町市", "長岡市", "新潟市", "見附市", "南魚沼市", "妙高市", "村上市", "弥彦村"]
    ,"長野": ["青木村", "上松町", "朝日村", "阿智村", "安曇野市", "阿南町", "飯島町", "飯田市", "飯綱町", "飯山市", "池田町", "伊那市", "上田市", "大桑村", "大町市", "岡谷市", "小谷村", "小布施町", "軽井沢町", "川上村", "木曽町", "木祖村", "小海町", "駒ヶ根市", "小諸市", "坂城町", "佐久市", "佐久穂町", "塩尻市", "下條村", "下諏訪町", "須坂市", "諏訪市", "喬木村", "高森町", "辰野町", "立科町", "千曲市", "茅野市", "東御市", "豊丘村", "中川村", "中野市", "長野市", "長和町", "白馬村", "原村", "富士見町", "松川町", "松川村", "松本市", "南相木村", "南牧村", "南箕輪村", "箕輪町", "宮田村", "御代田町", "山形村", "山ノ内町"]
    ,"山梨": ["市川三郷町", "上野原市", "大月市", "忍野村", "甲斐市", "甲州市", "甲府市", "小菅村", "昭和町", "中央市", "都留市", "南部町", "韮崎市", "笛吹市", "富士河口湖町", "富士川町", "富士吉田市", "北杜市", "南アルプス市", "身延町", "山中湖村", "山梨市"]
    ,"富山": ["朝日町", "射水市", "魚津市", "小矢部市", "上市町", "黒部市", "高岡市", "立山町", "砺波市", "富山市", "滑川市", "南砺市", "入善町", "氷見市", "舟橋村"]
    ,"石川": ["穴水町", "内灘町", "加賀市", "金沢市", "かほく市", "川北町", "小松市", "志賀町", "珠洲市", "津幡町", "中能登町", "七尾市", "能登町", "野々市市", "能美市", "羽咋市", "白山市", "宝達志水町", "輪島市"]
    ,"福井": ["あわら市", "池田町", "永平寺町", "越前市", "越前町", "おおい町", "大野市", "小浜市", "勝山市", "坂井市", "鯖江市", "高浜町", "敦賀市", "福井市", "南越前町", "美浜町", "若狭町"]
    ,"岐阜":["安八町", "池田町", "揖斐川町", "恵那市", "大垣市", "大野町", "海津市", "各務原市", "笠松町", "可児市", "川辺町", "北方町", "岐南町", "岐阜市", "郡上市", "下呂市", "神戸町", "坂祝町", "白川町", "白川村", "関ケ原町", "関市", "高山市", "多治見市", "垂井町", "土岐市", "富加町", "中津川市", "羽島市", "飛騨市", "瑞浪市", "瑞穂市", "御嵩町", "美濃加茂市", "美濃市", "本巣市", "山県市", "養老町", "輪之内町"]
    ,"静岡": ["熱海市", "伊豆市", "伊豆の国市", "伊東市", "磐田市", "御前崎市", "小山町", "掛川市", "河津町", "函南町", "菊川市", "湖西市", "御殿場市", "静岡市", "島田市", "清水町", "下田市", "裾野市", "長泉町", "西伊豆町", "沼津市", "浜松市", "東伊豆町", "袋井市", "藤枝市", "富士市", "富士宮市", "牧之原市", "松崎町", "三島市", "南伊豆町", "森町", "焼津市", "吉田町"]
    ,"三重": ["朝日町", "伊賀市", "伊勢市", "いなべ市", "大台町", "尾鷲市", "亀山市", "川越町", "木曽岬町", "紀宝町", "紀北町", "熊野市", "桑名市", "菰野町", "志摩市", "鈴鹿市", "多気町", "玉城町", "津市", "東員町", "鳥羽市", "名張市", "松阪市", "南伊勢町", "明和町", "四日市市", "度会町"]
    ,"愛知": ["愛西市", "阿久比町", "あま市", "安城市", "一宮市", "稲沢市", "犬山市", "岩倉市", "大口町", "大治町", "大府市", "岡崎市", "尾張旭市", "春日井市", "蟹江町", "刈谷市", "蒲郡市", "北名古屋市", "清須市", "幸田町", "江南市", "小牧市", "設楽町", "新城市", "瀬戸市", "高浜市", "武豊町", "田原市", "知多市", "知立市", "津島市", "東海市", "東郷町", "常滑市", "飛島村", "豊明市", "豊川市", "豊田市", "豊橋市", "豊山町", "長久手市", "名古屋市", "西尾市", "日進市", "半田市", "東浦町", "扶桑町", "碧南市", "美浜町", "みよし市", "弥富市"]
    ,"大阪":["池田市", "泉大津市", "泉佐野市", "和泉市", "茨木市", "大阪狭山市", "大阪市", "貝塚市", "柏原市", "交野市", "門真市", "河南町", "河内長野市", "岸和田市", "熊取町", "堺市", "四條畷市", "島本町", "吹田市", "摂津市", "泉南市", "太子町", "高石市", "高槻市", "田尻町", "忠岡町", "大東市", "千早赤阪村", "豊中市", "豊能町", "富田林市", "寝屋川市", "能勢町", "羽曳野市", "阪南市", "東大阪市", "枚方市", "藤井寺市", "松原市", "箕面市", "守口市", "八尾市"]
    ,"京都":["綾部市", "井手町", "伊根町", "宇治市", "宇治田原町", "大山崎町", "亀岡市", "木津川市", "京田辺市", "京丹後市", "京丹波町", "京都市", "久御山町", "城陽市", "精華町", "長岡京市", "南丹市", "福知山市", "舞鶴市", "南山城村", "宮津市", "向日市", "八幡市", "与謝野町", "和束町"]
    ,"滋賀":["愛荘町", "近江八幡市", "大津市", "草津市", "甲賀市", "甲良町", "湖南市", "高島市", "多賀町", "豊郷町", "長浜市", "東近江市", "彦根市", "日野町", "米原市", "守山市", "野洲市", "栗東市", "竜王町"]
    ,"兵庫":["相生市", "明石市", "赤穂市", "朝来市", "芦屋市", "尼崎市", "淡路市", "伊丹市", "市川町", "猪名川町", "稲美町", "小野市", "加古川市", "加西市", "加東市", "神河町", "上郡町", "川西市", "神戸市", "佐用町", "三田市", "宍粟市", "新温泉町", "洲本市", "太子町", "高砂市", "多可町", "宝塚市", "たつの市", "丹波篠山市", "丹波市", "豊岡市", "西宮市", "西脇市", "播磨町", "姫路市", "福崎町", "三木市", "南あわじ市", "養父市"]
    ,"奈良":["安堵町", "斑鳩町", "生駒市", "宇陀市", "王寺町", "大淀町", "橿原市", "香芝市", "葛城市", "河合町", "川上村", "川西町", "上牧町", "広陵町", "五條市", "御所市", "桜井市", "三郷町", "下市町", "高取町", "田原本町", "天理市", "奈良市", "平群町", "三宅町", "大和郡山市", "大和高田市"]    
    ,"和歌山":["有田川町", "有田市", "印南町", "岩出市", "海南市", "かつらぎ町", "上富田町", "紀の川市", "紀美野町", "高野町", "古座川町", "御坊市", "新宮市", "田辺市", "那智勝浦町", "橋本市", "広川町", "みなべ町", "美浜町", "湯浅町", "由良町", "和歌山市"]
    ,"鳥取":["岩美町", "倉吉市", "江府町", "琴浦町", "境港市", "大山町", "智頭町", "鳥取市", "南部町", "日南町", "日吉津村", "日野町", "伯耆町", "北栄町", "三朝町", "八頭町", "湯梨浜町", "米子市", "若桜町"]
    ,"島根":["海士町", "出雲市", "雲南市", "大田市", "邑南町", "隠岐の島町", "奥出雲町", "川本町", "江津市", "津和野町", "西ノ島町", "浜田市", "益田市", "松江市", "美郷町", "安来市", "吉賀町"]
    ,"岡山":["赤磐市", "浅口市", "井原市", "岡山市", "鏡野町", "笠岡市", "吉備中央町", "久米南町", "倉敷市", "里庄町", "勝央町", "瀬戸内市", "総社市", "高梁市", "玉野市", "津山市", "奈義町", "新見市", "西粟倉村", "早島町", "備前市", "真庭市", "美咲町", "美作市", "矢掛町", "和気町"]
    ,"広島":["安芸太田町", "安芸高田市", "江田島市", "大崎上島町", "大竹市", "尾道市", "海田町", "北広島町", "熊野町", "呉市", "坂町", "庄原市", "神石高原町", "世羅町", "竹原市", "廿日市市", "東広島市", "広島市", "福山市", "府中市", "府中町", "三原市", "三次市"]
    ,"山口":["岩国市", "宇部市", "上関町", "下松市", "山陽小野田市", "下関市", "周南市", "周防大島町", "田布施町", "長門市", "萩市", "光市", "平生町", "防府市", "美祢市", "柳井市", "山口市", "和木町"]
    ,"徳島":["藍住町", "阿南市", "阿波市", "石井町", "板野町", "海陽町", "勝浦町", "上板町", "北島町", "小松島市", "佐那河内村", "徳島市", "那賀町", "鳴門市", "東みよし町", "松茂町", "美波町", "美馬市", "三好市", "牟岐町", "吉野川市"]
    ,"香川":["綾川町", "宇多津町", "観音寺市", "坂出市", "さぬき市", "小豆島町", "善通寺市", "高松市", "多度津町", "土庄町", "東かがわ市", "丸亀市", "まんのう町", "三木町", "三豊市"]
    ,"愛媛":["伊方町", "今治市", "伊予市", "内子町", "宇和島市", "大洲市", "上島町", "久万高原町", "西条市", "四国中央市", "西予市", "東温市", "砥部町", "新居浜市", "松前町", "松山市", "八幡浜市"]
    ,"高知":["安芸市", "いの町", "大月町", "越知町", "香美市", "黒潮町", "芸西村", "高知市", "香南市", "佐川町", "四万十市", "四万十町", "宿毛市", "須崎市", "田野町", "津野町", "土佐市", "土佐清水市", "土佐町", "南国市", "仁淀川町", "日高村", "室戸市", "本山町", "梼原町"]
    ,"福岡":["朝倉市", "芦屋町", "飯塚市", "糸島市", "糸田町", "うきは市", "宇美町", "大川市", "大木町", "大任町", "大野城市", "大牟田市", "岡垣町", "小郡市", "遠賀町", "春日市", "粕屋町", "嘉麻市", "川崎町", "香春町", "苅田町", "北九州市", "鞍手町", "久留米市", "桂川町", "上毛町", "古賀市", "篠栗町", "志免町", "新宮町", "須恵町", "添田町", "田川市", "大刀洗町", "太宰府市", "筑後市", "筑紫野市", "築上町", "筑前町", "那珂川市", "中間市", "直方市", "久山町", "広川町", "福岡市", "福智町", "福津市", "豊前市", "水巻町", "みやこ町", "みやま市", "宮若市", "宗像市", "柳川市", "八女市", "行橋市"]
    ,"佐賀":["有田町", "伊万里市", "嬉野市", "小城市", "鹿島市", "上峰町", "唐津市", "神埼市", "基山町", "玄海町", "江北町", "佐賀市", "白石町", "多久市", "武雄市", "太良町", "鳥栖市", "みやき町"]
    ,"長崎":["壱岐市", "諫早市", "雲仙市", "大村市", "小値賀町", "五島市", "西海市", "佐々町", "佐世保市", "島原市", "新上五島町", "時津町", "長崎市", "長与町", "波佐見町", "平戸市", "松浦市", "南島原市"]
    ,"大分":["宇佐市", "臼杵市", "大分市", "杵築市", "玖珠町", "国東市", "九重町", "佐伯市", "竹田市", "津久見市", "中津市", "日出町", "日田市", "豊後大野市", "豊後高田市", "別府市", "由布市"]
    ,"熊本":["芦北町", "阿蘇市", "天草市", "荒尾市", "宇城市", "宇土市", "大津町", "上天草市", "菊池市", "菊陽町", "玉東町", "熊本市", "合志市", "玉名市", "長洲町", "南関町", "氷川町", "人吉市", "益城町", "水俣市", "南阿蘇村", "八代市", "山鹿市", "山都町"]
    ,"宮崎":["綾町", "えびの市", "門川町", "川南町", "木城町", "串間市", "国富町", "小林市", "西都市", "椎葉村", "新富町", "高千穂町", "高鍋町", "都農町", "西米良村", "日南市", "延岡市", "日之影町", "日向市", "三股町", "都城市", "宮崎市"]
    ,"鹿児島":["姶良市", "阿久根市", "天城町", "奄美市", "出水市", "伊仙町", "いちき串木野市", "指宿市", "大崎町", "鹿児島市", "鹿屋市", "喜界町", "肝付町", "霧島市", "錦江町", "薩摩川内市", "さつま町", "志布志市", "瀬戸内町", "曽於市", "龍郷町", "垂水市", "知名町", "徳之島町", "中種子町", "長島町", "西之表市", "日置市", "東串良町", "枕崎市", "南大隅町", "南九州市", "南さつま市", "屋久島町", "湧水町", "与論町", "和泊町"]
    ,"沖縄":["石垣市", "糸満市", "浦添市", "うるま市", "沖縄市", "恩納村", "嘉手納町", "北中城村", "金武町", "宜野座村", "宜野湾市", "久米島町", "北谷町", "豊見城市", "中城村", "名護市", "那覇市", "南城市", "西原町", "南風原町", "宮古島市", "本部町", "八重瀬町", "与那原町", "読谷村"]
    }
    
     				