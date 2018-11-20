import urllib.request
import urllib.parse
import json
import time

while 1:
    content = input("输入翻译内容(!q退出)：")
    if content == '!q':
        break
    #tsto =input ("想要输出的语言：")
    url = "http://fanyi.baidu.com/v2transapi"
    data={}
    data['from']='auto'
    data['to']='en'
    data['query']=content
    data['transtype']='realtime'
    data['simple_means_flag']='3'
    
    data = urllib.parse.urlencode(data).encode('utf-8')

    response = urllib.request.urlopen(url,data)

    html = response.read().decode("utf-8")
    json.loads(html)

    target = json.loads(html)
    tst=target["trans_result"]['data'][0]['dst']
    print(tst)
    #print ("翻译结果：%s" %(target["trans_result"]['data'][0]['dst']))
    # time.sleep(3) 防止识别为非人类操作



