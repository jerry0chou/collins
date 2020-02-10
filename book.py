from jinja2 import Template
import uuid, os, zipfile

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml', 'opf', 'opf'])
)


def setTemplateValues(dataDict):
    for filename, dictValues in dataDict.items():
        template = env.get_template(filename)
        string = template.render(**dictValues)
        with open(f'epub/OEBPS/{filename}', 'w') as f:
            f.write(string)


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
            print(os.path.join(path, filename), os.path.join(fpath, filename))
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


# uuid 需一致
uu = uuid.uuid4()
dataDict = {
    'content.opf': {
        'title': "Collins",
        'creator': 'JerryChou',
        'uuid': uu
    },
    'toc.ncx': {
        'uuid': uu,
        'title': "Collins"
    },
    'title.html': {
        'title': "Collins"
    }
}

setTemplateValues(dataDict)
zipDir('epub','test.epub')
