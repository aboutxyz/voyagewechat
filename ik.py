# -*- coding:utf-8 -*-
import sys
import datetime
import time
from flask import Flask, g, request, make_response
import hashlib
import xml.etree.ElementTree as ET
import threading
import MySQLdb


tips = u'请输入船名'
error_msg = u'暂无计划'
#data=()
  

app = Flask(__name__)

app.debug = True
@app.route('/')
def hello():
    return 'hello,my dear'
  
@app.route('/weixin', methods = ['GET', 'POST'] )
def wechat_auth():
  global Content1
  if request.method == 'GET':
    token = 'voyage'
    query = request.args
    signature = query.get('signature', '')
    timestamp = query.get('timestamp', '')
    nonce = query.get('nonce', '')
    echostr = query.get('echostr', '')
    s = [timestamp, nonce, token]
    s.sort()
    s = ''.join(s)
    if ( hashlib.sha1(s).hexdigest() == signature ):  
      return make_response(echostr)
  # Get the infomations from the recv_xml.
  xml_recv = ET.fromstring(request.data)
  ToUserName = xml_recv.find("ToUserName").text
  FromUserName = xml_recv.find("FromUserName").text
  Content = xml_recv.find("Content").text
  reply = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"

  if Content == u'帮助':
    Content1 = tips
  else:
    args = Content.split('@')
    for i in range(len(args)): args[i] = args[i].encode('utf8') # pass test
    db = MySQLdb.connect(host='45.32.248.255',user='root',passwd='900502',db='voyagecheck',port=3306,charset='utf8')
    cursor=db.cursor()
    sql9 = "select *from voyagecheck where VESSELCN=%s or VESSELEN=%s"
    aa=cursor.execute(sql9,(Content,Content))
    result =cursor.fetchmany(aa)
    Content1 = ''
    bb=len(result)-1
    if bb<0:
        Content1=error_msg
    else:
        data=result[bb]
        Content1=u"码头:"+data[1]+'\n'+u"中文船名:"+data[2]+'\n'+u"英文船名:"+data[3]+'\n'+u"进口航次:"+data[4]+'\n'+u"出口航次:"+data[5]+'\n'+data[6]+'\n'+data[7]
    #data=()
    db.close()
  response = make_response( reply % (FromUserName, ToUserName, str(int(time.time())), Content1 ) )
  response.content_type = 'application/xml'
  return response


