#!/usr/bin/env python3
#coding:utf-8
#----------------------------svedbox-----------------------------------#
#-----Telegram bot for watching at the course of USD on site of -------#
#-----Central bank of Russia and when it changed sends message to -----# 
#-----telegram---------------------------------------------------------#
#----------------------------------------------------------------------#
#--------Modules-------#
import os
import urllib.request
import string
import requests
import socks
import datetime
import sqlite3
import configparser
#--------Variables of paths--------------------------#
workpath=(os.getcwd() +'/.usdcourse')
configpath=(os.getcwd() +'/.usdcourse/usdcourse.conf')
logpath=(os.getcwd() +'/.usdcourse/usdcourse.log')
dbpath=(os.getcwd() +'/.usdcourse/usdcourse.db')
#----Creating work dir-----------------#
if not (os.path.exists(workpath)):
    d = os.mkdir(workpath)
#----Creating conf file---------#
if not (os.path.exists(configpath)):
    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section("Read me")
    config.set('Read me', "# If you use a proxy-server please set address and port\n #for example proxy = 127.0.0.1:9090\n #default proxy=false")
    config.add_section("Main") 
    config.set("Main", "proxy","false")
    with open(configpath, "w") as config_file:
        config.write(config_file)
#----Creating log file---------#
if not (os.path.exists(logpath)):
    file = open(logpath, 'w+')
    file.write('0')
    file.close()
#--------Reading conf file-------------#
config = configparser.ConfigParser()
config.read(configpath)
proxy = config.get('Main', 'proxy')
#--------Work variables-------------------------------------#
cbrurl = ('http://www.cbr.ru/scripts/XML_daily.asp?date_req=')
boturl='https://api.telegram.org/bot' 
date = str(datetime.datetime.today().strftime("%d.%m.%Y"))
prox = ("socks5://" + proxy)
proxies = {"https":prox}
#-------Checking exist database------------#
if not (os.path.exists(dbpath)):
    token = input('Enter your telegram token -')
    chatid = input('Enter your telegram chat id -')
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE secret
                      ('id' INTEGER PRIMARY KEY, 'token' TEXT, 'chatid' TEXT)
                   """)
    cursor.execute("""CREATE TABLE courses
                      ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'date' TEXT, 'course' REAL, 'message' TEXT )
                   """)
    cursor.execute("""CREATE TABLE lastusd
                      ('id' INTEGER PRIMARY KEY,'lastcourse' REAL)
                   """)
    cursor.execute("INSERT INTO lastusd (id, lastcourse) VALUES (1, 0)" )
    cursor.execute("INSERT INTO secret (id, token, chatid) VALUES (1, ?, ?)" , (token, chatid))
    conn.commit()
    cursor.close()
    conn.close()

#----------------SQL--Sec------------------------------#
conn = sqlite3.connect(dbpath)
cursor = conn.cursor()
[token], = cursor.execute("SELECT token FROM secret WHERE id = 1 ")
[chatid], = cursor.execute("SELECT chatid FROM secret WHERE id = 1 ")
conn.commit()
cursor.close()
conn.close()
#---------------------------------------------------#
urlt = str(boturl + token +'/sendMessage')
cbrpage = str(urllib.request.urlopen(cbrurl).read())
usdindex = cbrpage.find('USD')
usdcoursetmp = (cbrpage[usdindex+91:usdindex+96]).replace(',','.')
usdcourse = float(usdcoursetmp) #-Digital course of CBR--#
#-------Check course of USD on the site of CBR of Russia-------#
#-------------SQL-------------------------#
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
[usdold], = cur.execute("SELECT lastcourse FROM lastusd WHERE id = 1 ")
conn.commit()
cur.close()
conn.close()
#-----------------------------------------#
if (usdcourse != usdold):
    usdchange = round((usdcourse - usdold),2)
    if (usdchange > 0):
        usdchangestr=str(usdchange)
        usdchangeout = ('+'+ usdchangestr)
        data = {"chat_id":chatid, "text":("Курс ЦБ  " + str(usdcourse) + " (" + usdchangeout + ")")}
        if proxy == 'false':
            message = str(requests.post(urlt, data))
        else:
            message = str(requests.post(urlt, data ,proxies=proxies))
        file = open(logpath, 'a')
        file.write('\n' "| " + message + " | "+ date + " | Курс USD - " + usdcoursetmp + " |")
        file.close()
        #-------------SQL----------------#
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (date, course, message) VALUES (?, ?, ?)" , (date, usdcourse, message))
        cursor.execute("UPDATE lastusd SET lastcourse = ? WHERE id = 1 "  , (usdcourse,))
        conn.commit()
        cursor.close()
        conn.close()
        #--------------------------------#
    else:
        usdchangeout = str(usdchange)
        data = {"chat_id":chatid, "text":("Курс ЦБ  " + str(usdcourse) + " (" + usdchangeout + ")")}
        if proxy == 'false':
            message = str(requests.post(urlt, data))
        else:
            message = str(requests.post(urlt, data ,proxies=proxies))
        file = open(logpath, 'a')
        file.write('\n' "| " + message + " | "+ date + " | Курс USD - " + usdcoursetmp + " |")
        file.close()
        #-------------SQL----------------#
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (date, course, message) VALUES (?, ?, ?)" , (date, usdcourse, message))
        cursor.execute("UPDATE lastusd SET lastcourse = ? WHERE id = 1 "  , (usdcourse,))
        conn.commit()
        cursor.close()
        conn.close()
#----------------------------END-----------------------------#
