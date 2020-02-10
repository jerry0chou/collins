import sqlite3
import re

conn = sqlite3.connect('collins.db')


def autoOpenClose(func):
    def wrapper(*args, **kwargs):
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
