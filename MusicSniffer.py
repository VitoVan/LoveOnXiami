# -*- coding: utf-8 -*-
import re
import urllib2
import time
import subprocess
from bs4 import BeautifulSoup

'''
请本着一颗仁爱之心使用。
不要非法下载音乐，请尊重艺术作品版权。
一个不尊重版权的民族，不值得拥有人权。
'''

#模拟浏览器进行页面抓取，虾米的某些数据必须有浏览器参数才可以访问，直接用urllib2.urlopen不好使
def getPageSoup(pageUrl):
    hds = { 'User-Agent' : 'Mozilla/5.0 (XiamiLover NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36' }
    req = urllib2.Request(url = pageUrl,headers = hds)
    opener = urllib2.build_opener()
    resp = opener.open(req)
    doc = resp.read()
    soup = BeautifulSoup(doc)
    return soup
#从页面上获取用户最后听的一首歌的ID
def getLatestSongId(user_id):
    song_list_url = 'http://www.xiami.com/space/charts-recent/u/'+user_id
    songlist_soup = getPageSoup(song_list_url)
    songs = songlist_soup.find_all('a')
    for song in songs:
        if '/song/' in song['href']:
            return song['href'][6:]

#获取歌曲XML，解密并以BeautifulSoup对象返回
def getSongSoup(song_id):
    song_url = 'http://www.xiami.com/song/playlist/id/'+song_id+'/object_name/default/object_id/0'
    song_soup = getPageSoup(song_url)
    song_address_code = song_soup.find('location').string
    #此部分为虾米链接解密算法，抄袭自：https://github.com/Flowerowl/xiami
    num = int(song_address_code[0])
    avg_len, remainder = int(len(song_address_code[1:]) / num), int(len(song_address_code[1:]) % num)
    result = [song_address_code[i * (avg_len + 1) + 1: (i + 1) * (avg_len + 1) + 1] for i in range(remainder)]
    result.extend([song_address_code[(avg_len + 1) * remainder:][i * avg_len + 1: (i + 1) * avg_len + 1] for i in range(num-remainder)])
    url = urllib2.unquote(''.join([''.join([result[j][i] for j in range(num)]) for i in range(avg_len)]) + \
                              ''.join([result[r][-1] for r in range(remainder)])).replace('^','0')
    song_soup.find('location').string = url
    return song_soup

#循環監聽
def startMonitor(user_id):
    if user_id == '':
        user_id = '8419837'
    print 'Let be in love......'
    global pre_song_id
    global cur_song_id
    global start_player_cmd
    while True:
        try:
            cur_song_id = getLatestSongId(user_id)
        except KeyboardInterrupt:
            exit();
        except:
            print 'Something went wrong...I gonna try again.'
        if pre_song_id == cur_song_id:
            print "Don't worry, I'm working -- TIMESTAMP:" + str(time.time())
            time.sleep(heartbeat_frequency)
        else:
            pre_song_id = cur_song_id
            subprocess.call(stop_player_cmd)
            songSoup = getSongSoup(cur_song_id)
            cur_song_addr = songSoup.find('location').string
            start_player_cmd.append(cur_song_addr)
            subprocess.Popen(start_player_cmd)

#心跳頻率（秒）
heartbeat_frequency = 10

#歌曲ID
pre_song_id = 0
cur_song_id = 0

#播放器命令
start_player_cmd = ["/usr/bin/mplayer",'-volume','50']
stop_player_cmd = ["/usr/bin/killall","mplayer"]


startMonitor(raw_input('Input her/his ID (8419837) : \n'))
