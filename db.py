import sqlite3
import re

conn = sqlite3.connect('collins.db')


def autoOpenClose(func):
    def wrapper(*args, **kwargs):
        global conn
        try:
            conn.cursor()
        except:
            conn = sqlite3.connect('collins.db')
        res = func(*args, **kwargs)
        conn.commit()
        conn.close()
        return res

    return wrapper


@autoOpenClose
def clearAllData():
    c = conn.cursor()
    c.execute('delete from detail')
    c.execute('delete from example')
    c.execute('delete from word')
    c.execute('update sqlite_sequence set seq=0')


def rep(string: str):
    string = string.replace("'", '"')
    return string

def rep2(string: str):
    string = string.replace('"', "'")
    return string

@autoOpenClose
def insertWordInfo(word, wordDict):
    c = conn.cursor()
    # 查出单词id
    queryWordId = f"SELECT id from word where name='{rep(word)}'"
    res = c.execute(queryWordId)
    wordId = [r[0] for r in res][0]
    for k, v in wordDict.items():
        # 插入detail
        insertDetail = f"""
        INSERT INTO detail(word_id,feature,chinese,english)
        values ({wordId},'{rep(v['feature'])}','{rep(v['chinese'])}','{rep(v['english'])}')
        """
        c.execute(insertDetail)

        queryDetailId = f'SELECT max(id) from detail where word_id={wordId}'
        res = c.execute(queryDetailId)
        detailId = [r[0] for r in res][0]

        for exp in v['examples']:
            insertExample = f'''
            INSERT INTO example(en,cn,detail_id) values('{rep(exp[0])}','{rep(exp[1])}',{detailId})
            '''
            c.execute(insertExample)


@autoOpenClose
def insertWord(name):
    c = conn.cursor()
    sql = f'''insert into word(name) VALUES ('{rep(name)}')'''
    c.execute(sql)


@autoOpenClose
def setWordLevel(word, level):
    c = conn.cursor()
    c.execute(f"""update word set level={level} where name='{rep(word)}'""")

@autoOpenClose
def setWordSpeak(word, speak):
    c = conn.cursor()
    c.execute(f'''update word set speak="{rep2(speak)}" where name="{word}" ''')

@autoOpenClose
def setWordSpeak2(wordId, speak):
    c = conn.cursor()
    c.execute(f'''update word set speak="{rep2(speak)}" where id={wordId} ''')

@autoOpenClose
def setDefaultWordLevel():
    c = conn.cursor()
    c.execute(f'update word set level=0 where level is null ')


@autoOpenClose
def queryAllWord():
    c = conn.cursor()
    res = c.execute('select name from word ')
    wordList = []
    for r in res:
        wordList.append(r[0])
    return wordList

@autoOpenClose
def querySpeakIsNullWord():
    c = conn.cursor()
    res = c.execute('select name from word where speak="" or speak is null')
    wordList = []
    for r in res:
        wordList.append(r[0])
    return wordList

@autoOpenClose
def handleError():
    c = conn.cursor()
    res = c.execute('SELECT name from word where id in (SELECT word_id from detail ORDER BY id DESC LIMIT 1) ')
    word = [r[0] for r in res][0]
    c.execute("""
    delete from example where detail_id in (SELECT id from detail WHERE word_id in (SELECT word_id from detail ORDER BY id DESC LIMIT 1)  ) 
    """)
    c.execute('delete from detail where word_id in (SELECT word_id from detail ORDER BY id DESC LIMIT 1) ')
    return word


@autoOpenClose
def getUncapturedWord():
    c = conn.cursor()
    res = c.execute('SELECT  name from word where id not in (SELECT word_id from detail)')
    wordList = []
    for r in res:
        wordList.append(r[0])
    return wordList


@autoOpenClose
def queryWordByName(name):
    c = conn.cursor()
    res = c.execute(f"SELECT id,name,speak,level from word where name='{name}'")
    word = [r for r in res][0]
    return word


@autoOpenClose
def queryWordDetailByWordId(wid):
    c = conn.cursor()
    res = c.execute(f"SELECT id, feature,chinese,english from detail WHERE word_id={wid}")
    detail = [r for r in res]
    return detail


@autoOpenClose
def queryWordExampleByDetailId(detail_id):
    c = conn.cursor()
    res = c.execute(f"SELECT en,cn from example where detail_id={detail_id}")
    examples = [r for r in res]
    return examples

@autoOpenClose
def queryWordByLevel(level):
    c = conn.cursor()
    res = c.execute(f'select name from word where level={level} ')
    wordList = []
    for r in res:
        wordList.append(r[0])
    return wordList

@autoOpenClose
def queryWrongSpeakWord():
    c = conn.cursor()
    res = c.execute(f"""SELECT id,name from word where speak = '' """)
    wordInfoList = []
    for r in res:
        wordInfoList.append((r[0],r[1]))
    return wordInfoList
