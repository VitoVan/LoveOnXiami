#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
filename: MusicSniffer.py
author: Vito Van
mail: awesomevito@live.com
"""
import copy
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
    #print 'FETCHING: \n' + pageUrl
    hds = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36' }
    req = urllib2.Request(url = pageUrl,headers = hds)
    opener = urllib2.build_opener()
    resp = opener.open(req)
    doc = resp.read()
    return BeautifulSoup(doc)
#从页面上获取用户最后听的一首歌的ID
def getLatestSongId(user_id):
    song_list_url = 'http://www.xiami.com/space/charts-recent/u/'+user_id
    songlist_soup = getPageSoup(song_list_url)
    #print song_list_url+'\n===This is the SONG LIST HTML: \n' + songlist_soup.prettify() + '\n===='
    songs = songlist_soup.find_all('a')
    for song in songs:
        if '/song/' in song['href']:
            return song['href'][6:]

#获取歌曲XML，解密并以BeautifulSoup对象返回
def getSongSoup(song_id):
    song_url = 'http://www.xiami.com/song/playlist/id/'+str(song_id)+'/object_name/default/object_id/0'
    song_soup = getPageSoup(song_url)
    #print song_url + '\n===This is the song XML: \n' + song_soup.prettify() + '\n===='
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
    print 'Love is going......'
    global pre_song_id
    global cur_song_id
    global start_player_cmd
    while True:
        try:
            cur_song_id = getLatestSongId(user_id)
        except KeyboardInterrupt:
            print "bye~my love"
            exit();
        except:
            print 'Something went wrong...I gonna try again.  BECAUSE: ',ex
        if pre_song_id == cur_song_id:
            #print "Don't worry, I'm working -- CUR_SID:"+str(cur_song_id)+" TIMESTAMP:" + str(time.time())
            time.sleep(heartbeat_frequency)
        else:
            fh = open("NULL","w")
            pre_song_id = cur_song_id
            subprocess.call(stop_player_cmd,stdout=fh,stderr=fh)
            songSoup = getSongSoup(cur_song_id)
            print "==== SONG INFO: ====\n TITLE: " + songSoup.find('title').string.replace('<![CDATA[','').replace(']]>','') + ' ALBUM: ' + songSoup.find('album_name').string.string.replace('[CDATA[','').replace(']]','') + " ARTIST: "+ songSoup.find('artist').string.string.replace('[CDATA[','').replace(']]','') + "\n"
            cur_song_addr = songSoup.find('location').string
            cur_player_cmd = copy.copy(start_player_cmd)
            cur_player_cmd.append(cur_song_addr)
            subprocess.Popen(cur_player_cmd,stdout=fh,stderr=fh)
            fh.close()

#心跳頻率（秒）
heartbeat_frequency = 10

#歌曲ID
pre_song_id = 0
cur_song_id = 0

#播放器命令
start_player_cmd = ["/usr/bin/mplayer",'-quiet','-volume','50']
stop_player_cmd = ["/usr/bin/killall","mplayer"]

startMonitor(raw_input('Input her/his ID (8419837) : \n'))
