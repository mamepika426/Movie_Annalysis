import requests
from time import sleep
from bs4 import BeautifulSoup
import os
import datetime

#page番目の一覧ページから映画のurlを取得
def get_urls(page):
    #movie_urlsにページ内の映画のurlを格納(16本格納される)
    movie_urls = []
    page_url = 'https://movies.yahoo.co.jp/movie/?type=&roadshow_flg=0&roadshow_from=&img_type=2&query=&genre=&award=&sort=-contribution&page={}'.format(page+1)
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text,'html.parser')
    page_movies = soup.find_all('li',class_='col')
    for m in range(len(page_movies)):
        movie_urls.append("https://movies.yahoo.co.jp"+page_movies[m].find('a').get('href'))

    return movie_urls

#一覧ページ上の映画をhtmlとして保存
def save_html(movie_urls,cnt):
    for movie_url in movie_urls:
        sleep(2)
        cnt = cnt+1
        response = requests.get(movie_url).text
        with open('./html_file/movie_file{}.html'.format(cnt),'w',encoding='utf_8') as f:
            f.write(response)

        #500本ごとにチェック
        if cnt%500== 0:
            print(str(cnt)+'本完了',datetime.datetime.now())

    return cnt

def crawling():
    #ディレクトリ作成
    dir = './html_file'
    if not os.path.exists(dir):
        os.mkdir(dir)

    print('クローリング開始',datetime.datetime.now())
    #5000件の映画を取得するために5000/16 = 313 ページまで検索
    max_page = 313
    cnt = 0
    for page in range(max_page):
        sleep(2)
        movie_urls = get_urls(page)
        cnt = save_html(movie_urls,cnt)

    if (cnt==5008) :
        print('検収条件を満たしています。')
    else :
        print('検収条件を満たしていません。(cnt={})'.format(cnt))

if __name__ == '__main__':
    crawling()
