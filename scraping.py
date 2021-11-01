import requests
from time import sleep
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import numpy as np
#クローリング中にランキングの変動があったとき、同じ映画を複数回取得することがある
#1度現れた映画のidをappeared_idsのフラグで管理し、複数回のスクレイピングを避ける
def repeated_check(file_num,appeared_ids):
    soup = BeautifulSoup(open('./html_file/movie_file{}.html'.format(file_num),encoding='utf-8'),'html.parser')
    id = soup.find_all('div',class_='btn-group btn-group--block btn-group--vertical btn-group--multi mb1em')[0].get('data-cinema-id')
    if(appeared_ids[int(id)]==0):
        appeared_ids[int(id)]=1
        return (False,appeared_ids)

    else :
        return (True,appeared_ids)

#info_trは作品情報を表すhtml
#attributesはその映画の作品情報テーブルに記載されている属性(タイトル、製作年度、...)
#テーブル上に属性を持たない場合の属性値は「記載なし」で処理する
def get_attributes_values(info_tr,attributes):
    target_attributes = ['タイトル','製作年度','上映時間','製作国']
    target_attributes_values = []
    for i in target_attributes:
        if i in attributes:
            index = attributes.index(i)
            tmp = info_tr[index].find('td').text
        else:
            tmp = str(i)+'記載なし'

        target_attributes_values.append(tmp)

    return target_attributes_values

#1つの映画がもつジャンルは最大4つなので、genresに4つの要素を入れる。
#4つ未満の場合は空欄を'記載なし'で埋めている。
def get_genres(info_tr,attributes):
    genres = []
    if 'ジャンル' in attributes:
        index = attributes.index('ジャンル')
        genre_li = info_tr[index].find_all('li',class_='pr1em')
        for i in range(len(genre_li)):
            tmp = genre_li[i].find('a').text
            genres.append(tmp)

        for j in range(4-len(genre_li)):
            tmp = 'ジャンル記載なし'
            genres.append(tmp)

    else :
        for i in range(4):
            tmp = 'ジャンル記載なし'
            genres.append(tmp)

    return genres


def get_data(file_num):
    soup = BeautifulSoup(open('./html_file/movie_file{}.html'.format(file_num),encoding='utf-8'),'html.parser')
    #映画idの取得
    id = soup.find_all('div',class_='btn-group btn-group--block btn-group--vertical btn-group--multi mb1em')[0].get('data-cinema-id')
    movie_url = "https://movies.yahoo.co.jp/movie/"+id

    #タイトル、原題、製作年、製作国、...がまとまったテーブル
    info = soup.find('div',attrs = {'id':'mvinf'})
    info_tr = info.find_all('tr')
    attributes = []
    for i in range(len(info_tr)):
        attributes.append(info_tr[i].find('th').text)
    #タイトル、..、ジャンルまでを取得
    title , year , showtime , country = get_attributes_values(info_tr,attributes)
    genres = get_genres(info_tr,attributes)

    #作品の評価に関する情報を取得
    eval = soup.find('div',class_='movie_data')
    #平均評価、評価数を取得
    eval_rating = eval.find('span',class_='rating-score')
    average = eval_rating.find('span').text
    eval_num = eval_rating.find('small',class_='text-xsmall')
    eval_num = eval_num.text.split(':')[1]
    eval_num = eval_num.replace(",","").replace("件","")
    #星1,2,3,4,5の割合を取得
    eval_dist = eval.find_all('div',attrs={'class':'rating-distribution__cell-point'})
    star5 = eval_dist[0].text.replace("%","")
    star4 = eval_dist[1].text.replace("%","")
    star3 = eval_dist[2].text.replace("%","")
    star2 = eval_dist[3].text.replace("%","")
    star1 = eval_dist[4].text.replace("%","")
    #レーダーチャートの点数を取得
    chart = eval.find('canvas',class_='rader-chart__figure').get('data-chart-val-total')
    story = chart.split(',')[0]
    casting = chart.split(',')[1]
    directing = chart.split(',')[2]
    video = chart.split(',')[3]
    music = chart.split(',')[4]

    #各情報を代入
    movie_cur = {'タイトル':title,'製作年度':year,'上映時間':showtime,'製作国':country,
    'ジャンル1':genres[0],'ジャンル2':genres[1],'ジャンル3':genres[2],'ジャンル4':genres[3],
    '平均評価':float(average),'評価数':int(eval_num),
    '5点評価の割合':float(star5),'4点評価の割合':float(star4),'3点評価の割合':float(star3),'2点評価の割合':float(star2),'1点評価の割合':float(star1),
    '物語':float(story),'配役':float(casting),'演出':float(directing),'映像':float(video),'音楽':float(music),'詳細url':movie_url}

    return movie_cur

def scraping():
    #映画本数
    Num = 5008
    #movie_listに映画の情報を加えていく
    movie_list = []
    appeared_ids = np.zeros(500000)
    repeated = 0 #映画の重複回数をカウント

    print('スクレイピング開始',datetime.datetime.now())

    for file_num in range(1,Num+1):
        appeared,appeared_ids = repeated_check(file_num,appeared_ids)
        if(appeared):
            repeated = repeated+1
        else:
            movie_list.append(get_data(file_num))
        #500本ごとにチェック
        if file_num%500==0:
            print(str(file_num)+'本完了',datetime.datetime.now())

    df = pd.DataFrame(movie_list)

    with open('data.csv',mode = 'w',encoding = 'shift_jis',errors = 'ignore')as f:
        df.to_csv(f)

    #検収条件の確認
    if (len(df)+repeated==Num):
        print('研修条件を満たしています。',datetime.datetime.now())
    else:
        print('研修条件を満たしていません。(len(df)+repeated={})'.format(len(df)+repeated))

if __name__ == '__main__':
    scraping()
