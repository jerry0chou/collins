import requests
from pyquery import PyQuery as pq
from db import insertWordInfo, queryAllWord, handleError, getUncapturedWord


def getWord(content):
    dic = {}
    d = pq(content)
    articles = d('.collins-section')
    for ar in pq(articles)('.section-prep').items():
        index = pq(ar)('.prep-order-icon').text()
        if index:
            title = pq(ar)('.size-chinese').eq(0)
            feature = title('.family-english').eq(0).text()
            chinese = title('.family-chinese').text()
            english = title('.prep-en').text()

            sentenceList = []
            for sentence in pq(ar)('.text-sentence').items():
                en = sentence('.family-english').text()
                cn = sentence('.family-chinese').text()
                sentenceList.append((en, cn))
            detailDict = {}
            detailDict['feature'] = feature
            detailDict['chinese'] = chinese
            detailDict['english'] = english
            detailDict['examples'] = sentenceList
            dic[index] = detailDict
    return dic


def setRequest(word):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.scxxb.com.cn/html/2019/gnxw_0716/705043.html',
        'Content-Type': 'text/html'}
    content = requests.get(f"http://www.iciba.com/{word}", headers=headers).text
    return content


def getWordInfoFromWeb(index, wordList):
    length = len(wordList) - index
    count = 0
    errorCount = 0
    for i in range(index, len(wordList)):
        word = wordList[i]
        count += 1
        content = setRequest(word)
        d = getWord(content)
        insertWordInfo(word, d)
        if not d:
            errorCount += 1
        print(
            f'\rerrorCount={errorCount},insertCount={count-errorCount}, count={count}, completed={round(count / length, 4) * 100}%, leave {length - count} to insert',
            end="")


# 出现错误重新爬取
# word = handleError()
# wordList = queryAllWord()
# index = wordList.index(word)
# getWordInfoFromWeb(index)

# 没有爬取到的单词
# word = handleError()
# index = wordList.index(word)

# wordList = getUncapturedWord()
# getWordInfoFromWeb(0, wordList)
