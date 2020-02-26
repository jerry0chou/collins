import requests
from pyquery import PyQuery as pq

from db import setWordSpeak, queryWrongSpeakWord, setWordSpeak2


def setRequest(word):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.scxxb.com.cn/html/2019/gnxw_0716/705043.html',
        'Content-Type': 'text/html'}
    content = requests.get(f"http://www.youdao.com/w/eng/{word}/#keyfrom=dict2.index", headers=headers).text
    return content


def getSpeak(wordInfoList):
    errorCount = 0
    length = len(wordInfoList)
    count = 0
    for index, ele in enumerate(wordInfoList):
        content = setRequest(ele[1])
        speak = pq(content)('.baav')('.pronounce').text()

        if speak == '':
            errorCount += 1
        count += 1
        if count >= length - 2:
            break

        setWordSpeak2(ele[0], speak)
        print(
            f'\rerrorCount={errorCount},setCount={count - errorCount}, count={count}, completed={round(count / length, 4) * 100}%, leave {length - count} to set',
            end="")


wordInfoList = queryWrongSpeakWord()
getSpeak(wordInfoList)
