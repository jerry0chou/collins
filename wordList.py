import re
from db import insertWord, clearAllData, setWordLevel, setDefaultWordLevel


def getWordFromTxt():
    allWordSet = set()
    wordLevelDict = {}
    for level in range(1, 6):
        filename = f'data/{level}.txt'
        with open(filename, 'r', encoding='utf8') as f:
            wordLevelSet = set()
            for row in f:
                if len(row) > 1:
                    wordList = row.split('\t')
                    for word in wordList:
                        word = word.replace('\n', '')
                        wordLevelSet.add(word)
                        allWordSet.add(word)
            wordLevelDict[level] = wordLevelSet

    return allWordSet, wordLevelDict


def getAllWord(filename):
    wordSet = []
    with open(filename, 'r', encoding='utf8') as f:
        for row in f:
            val = re.search('[<>/;#\u4e00-\u9fa5\d]', row)
            if not val:
                row = row.strip("\n")
                if len(row) > 2:
                    wordSet.append(row)

    return wordSet


def writeDataIntoDB():
    wordList = getAllWord('mdx/collins.txt')
    length = len(wordList)
    count = 0
    for word in wordList:
        count += 1
        insertWord(word)
        print(f'\r count: {count} , completed: {round(count / length, 4) * 100}%, leave {length - count} to insert',
              end="")


def initWordLevel():
    allWordSet, wordLevelDict = getWordFromTxt()
    for level, words in wordLevelDict.items():
        for word in words:
            setWordLevel(word, level)
    setDefaultWordLevel()


#initWordLevel()

# clearAllData()
# writeDataIntoDB()
