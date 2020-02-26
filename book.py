import uuid, os, zipfile, string, re

from jinja2 import Environment, FileSystemLoader, select_autoescape
from db import queryAllWord, queryWordByName, queryWordDetailByWordId, queryWordExampleByDetailId, queryWordByLevel

env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml', 'opf', 'opf'])
)


def setTemplateValues(dataDict):
    for filename, dictValues in dataDict.items():
        template = None
        try:
            template = env.get_template(filename)
        except:
            template = env.get_template('content.html')
        content = template.render(**dictValues)
        with open(f'epub/OEBPS/{filename}', 'w', encoding='utf8') as f:
            f.write(content)


def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')
        for filename in filenames:
            # print(os.path.join(path, filename), os.path.join(fpath, filename))
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


def initDataDict(kCount, keysLetter, length, total_detail_length, total_example_length):
    # uuid 需一致
    uu = uuid.uuid4()
    title = "柯林斯英汉双解"
    dataDict = {
        'content.opf': {
            'title': title,
            'creator': 'JerryChou',
            'uuid': uu,
            'letters': keysLetter
        },
        'toc.ncx': {
            'uuid': uu,
            'title': title,
            # 'letters':list(string.ascii_uppercase),
            'kCount': kCount
        },
        'title.html': {
            'title': title,
            'length': length,
            'total_detail_length': total_detail_length,
            'total_example_length': total_example_length
        },
    }
    return dataDict


def constructOneWordInfo(w, index, length):
    oneWordInfo = {}
    info = queryWordByName(w)
    inf = (info[0], info[1], info[2], list(range(info[3])), f'{index}/{length}')
    oneWordInfo['word'] = inf
    word_id = info[0]
    detail = queryWordDetailByWordId(word_id)
    oneWordInfo['detail_example'] = []
    detail_length = len(detail)
    example_length = 0
    for d in detail:
        detail_id = d[0]
        detail_example = {}
        detail_example['detail'] = d
        examples = queryWordExampleByDetailId(detail_id)
        detail_example['example'] = examples
        oneWordInfo['detail_example'].append(detail_example)
        example_length += len(examples)

    return oneWordInfo, detail_length, example_length


def constructWordInfo(wordList):
    letters = list(string.ascii_uppercase)
    alphabet = {}
    length = 0
    for word in wordList:
        if re.match('[a-zA-Z]', word[0]):
            index = letters.index(word.upper()[0])
            l = letters[index]
            if l in alphabet.keys():
                alphabet[l].append(word)
            else:
                alphabet[l] = [word]

            length += 1

    kCount = {}
    for k, v in alphabet.items():
        kCount[k] = len(v)

    count = 0

    total_detail_length = 0
    total_example_length = 0
    htmlDict = {}
    for k, words in alphabet.items():
        letterWords = []
        for index, w in enumerate(words):
            oneWordInfo, detail_length, example_length = constructOneWordInfo(w, index + 1, len(words))
            total_detail_length += detail_length
            total_example_length += example_length
            letterWords.append(oneWordInfo)
            count += 1
            print(f'\rcount:{count},completed:{round(count / length, 4) * 100}%,leave {length - count} to compute',
                  end="")
        htmlDict[f'{k}.html'] = {
            'title': f'{k}-({kCount[k]})',
            'allWordInfo': letterWords
        }

    dataDict = initDataDict(kCount, alphabet.keys(), length, total_detail_length, total_example_length)
    for k, v in htmlDict.items():
        dataDict[k] = v

    return dataDict


def removeFile():
    letters = list(string.ascii_uppercase)
    for letter in letters:
        filename = f'epub/OEBPS/{letter}.html'
        if os.path.exists(filename):
            os.remove(filename)




def genWordByLevel():
    dic = {
        0: '零',
        1: '一',
        2: '二',
        3: '三',
        4: '四',
        5: '五'
    }
    for level in reversed(range(6)):
        wordList = queryWordByLevel(level)
        dataDict = constructWordInfo(wordList)
        setTemplateValues(dataDict)
        zipDir('epub', f'{dic[level]}星词汇.epub')
        removeFile()


genWordByLevel()

wordList = queryAllWord()
dataDict = constructWordInfo(wordList)
setTemplateValues(dataDict)
zipDir('epub', '柯林斯英汉双解.epub')
removeFile()