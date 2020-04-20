#!/usr/bin/python3
#----------------------------svedbox-----------------------------------#
#-----Telegram bot for watching at the course of USD on site of -------#
#-----Central bank of Russia and when it changed sends message to -----# 
#-----telegram---------------------------------------------------------#
#----------------------------------------------------------------------#
#--------Modules-------#
import os
import pathlib
import urllib.request
import string
import requests
import socks
import datetime
import sqlite3
import configparser
import ast
#--------Variables of paths--------------------------#
logpath=(os.getcwd() +'/.usdcourse/usdcourse.log')
confpath=(os.getcwd() +'/.usdcourse/usdcourse.conf')
workdirpath=(os.getcwd() +'/.usdcourse')
dbpath=(os.getcwd() +'/.usdcourse/usdcourse.db')
fileusdcourselog=pathlib.Path(logpath)
fileconf=pathlib.Path(confpath)
dirusdcourse = pathlib.Path(workdirpath)
dbfile = pathlib.Path(dbpath)
#----Creating work dir-----------------#
if (os.path.exists(dirusdcourse)):
    pass
else:
    d = os.mkdir(workdirpath)
#----Creating log file---------#
if (os.path.exists(fileusdcourselog)):
    pass
else:
    file = open(logpath, 'w+')
    file.write('0')
    file.close()
#----Creating conf file---------#
if (os.path.exists(fileconf)):
    pass
else:
    file = open(confpath, 'w+')
    file.write('#----Please write your telegram token and chat id---- ')
    file.write('\n''#--For exampe token=8795737745gjhg3g47564g3g5j8746763534htgjgtHGH')
    file.write('\n''#--For exampe chatid=6655675743')
    file.write('\n''#--For exampe proxy=127.0.0.1:9050''\n''\n''\n')
    file.write('\n''[Main]')
    file.write('\n''token=')
    file.write('\n''chatid=')
    file.write('\n''proxies=')
    file.close()
    print('!!! Please watch usdcourse.conf, and correct it.')
    quit()
#--------Reading conf file-------------#
config = configparser.ConfigParser()
config.read(fileconf)
token = (config["Main"]["token"])
chatid = (config["Main"]["chatid"])
proxy= (config["Main"]["proxy"])
#--------Work variables-------------------------------------#
cbrurl = ('http://www.cbr.ru/scripts/XML_daily.asp?date_req=')
boturl='https://api.telegram.org/bot' 
proxi=("{'https':'socks5://"+ proxy + "'}")
proxies=ast.literal_eval(proxi)
urlt = str(boturl + token +'/sendMessage')
date = str(datetime.datetime.today().strftime("%d.%m.%Y"))
#-------Checking exist database------------#
if (os.path.exists(dbfile)):
    pass
else:
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE courses
                      ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'date' TEXT, 'course' REAL, 'message' TEXT )
                   """)
    cursor.execute("""CREATE TABLE lastusd
                      ('id' INTEGER PRIMARY KEY,'lastcourse' REAL)
                   """)
    cursor.execute("INSERT INTO lastusd (id, lastcourse) VALUES (1, 0)" )
    conn.commit()
    cursor.close()
    conn.close()
#---------------------------------------------------#
cbrpage = str(urllib.request.urlopen(cbrurl).read())
usdindex = cbrpage.find('USD')
usdcoursetmp = (cbrpage[usdindex+91:usdindex+96]).replace(',','.')
usdcourse = float(usdcoursetmp) #-Digital course of CBR--#
#-------Check course of USD on the site of CBR of Russia-------#
#-------------SQL-------------------------#
conn = sqlite3.connect(dbfile)
cur = conn.cursor()
[usdold], = cur.execute("SELECT lastcourse FROM lastusd WHERE id = 1 ")
conn.commit()
cur.close()
conn.close()
#-----------------------------------------#
if (usdcourse == usdold):
    pass
else:
    usdchange = round((usdcourse - usdold),2)
    if (usdchange > 0):
        usdchangestr=str(usdchange)
        usdchangeout = ('+'+ usdchangestr)
        data = {"chat_id":chatid, "text":("Курс ЦБ  " + str(usdcourse) + " (" + usdchangeout + ")")}
        message = str(requests.post(urlt, data ,proxies=proxies))
        print(message)
        file = open(logpath, 'a')
        file.write('\n' "| " + message + " | "+ date + " | Курс USD - " + usdcoursetmp + " |")
        file.close()
        #-------------SQL----------------#
        conn = sqlite3.connect(dbfile)
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
        message = str(requests.post(urlt, data ,proxies=proxies))
        file = open(logpath, 'a')
        file.write('\n' "| " + message + " | "+ date + " | Курс USD - " + usdcoursetmp + " |")
        file.close()
        #-------------SQL----------------#
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (date, course, message) VALUES (?, ?, ?)" , (date, usdcourse, message))
        cursor.execute("UPDATE lastusd SET lastcourse = ? WHERE id = 1 "  , (usdcourse,))
        conn.commit()
        cursor.close()
        conn.close()
#----------------------------END-----------------------------#
