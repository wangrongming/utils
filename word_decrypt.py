import io
import json
import math
import re

import requests
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

def get_word_position(url=None):
    if not url:
        url = "http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss" \
              "/9f1d456fb0c5430764a0376d0c700dfa.css"
    else:
        url = url
    res = requests.get(url=url, headers='')
    text = res.text
    # 正则 获取分类的类型
    compile_rex = re.compile("""svgmtsi\[class\^=\"(.*?)\"\]{width.*?middle;}""")
    info = compile_rex.findall(text)
    with open("dianping_dict.txt", "w", encoding="utf-8") as f:
        for type_key in info:  #  eg: 下标由0开始 (3,2)  ('uxesy', '-24.0', '-110.0') 海
            # 解析svg图
            compile_rex_svg = re.compile("""svgmtsi\[class\^=\"%s\"\]{width.*?background-image:\surl\((.*?)\).*?middle;}""" % type_key)
            info_svg_url = compile_rex_svg.findall(text)
            svg_list = get_svg(info_svg_url)
            # 正则 获取当前分类下 字符位置
            compile_rex = re.compile("""\.%s[a-z0-9]{1,3}{background:.*?px (.*?)px;}""" % type_key)
            info = compile_rex.findall(text)

            for info_two in enumerate(sorted(set(info), key=lambda x: abs(float(x)))):
                # 获取对应纵坐标 字体位置 (字体)
                compile_rex_x = re.compile("""\.%s[a-z0-9]{1,3}{background:(-[0-9]{1,3}\.0)px %spx;}""" % (type_key, info_two[1]))
                info_x = compile_rex_x.findall(text)

                print(info_two)
                print(sorted(info_x, key=lambda x: abs(float(x))))
                print(svg_list[info_two[0]])
                svg_str = svg_list[info_two[0]][1]

                for info_three in enumerate(sorted(info_x, key=lambda x: abs(float(x)))):
                    compile_rex_x = re.compile(
                        """\.(%s[a-z0-9]{1,3}){background:%spx %spx;}""" % (type_key, info_three[1], info_two[1]))
                    info_word = compile_rex_x.findall(text)
                    print(info_word)
                    final_dict = {svg_str[info_three[0]]: info_word[0]}
                    f.write(repr(final_dict))
                    f.write("\n")


def get_svg(url_list=None):
    for url in url_list:
        res = requests.get(url="http:{}".format(url))
        text = res.text
        compile_rex_x = re.compile("""<text x="\d+" y="(\d+)">(.*?)</text>""")
        info_x = compile_rex_x.findall(text)
        return sorted(info_x, key=lambda x: int(x[0]))


def parse_woff_type():
    """
    解析woff类型字体
    :return:
    """

    # res = requests.get("http://s3plus.meituan.net/v1/mss_73a511b8f91f43d0bdae92584ea6330b/font/f1c26632.woff")
    # res = requests.get("https://static.tianyancha.com/fonts-styles/fonts/21/21937898/tyc-num.woff")
    # with open("dp_woff.txt", "wb") as f:
    #     f.write(res.content)

    # font = TTFont('dp_woff.txt')  # 打开文件
    # font.saveXML('dp_woff.xml')

    onlineFonts = TTFont('dp_woff.txt')
    keys = onlineFonts.getGlyphNames()
    dic = onlineFonts.getBestCmap()
    print(dic)

    keys.remove('glyph00000')
    keys.remove('x')

    # logger.info('parse woff')

    image = Image.new("L", (1300, math.ceil(len(keys) / 50) * 30))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('dp_woff.txt', size=20)
    font_data = []
    for i in range(0, len(keys), 50):
        font_data.append(keys[i:i + 50])
    for i, item in enumerate(font_data):
        for j, k in enumerate(item):
            draw.text((j * 25, i * 25), chr(list(dic.keys())[list(dic.values()).index(k)]), font=font, fill=255)
            # draw.text((j * 25, i * 25), chr(int(k.replace('uni', '0x'), 16)), font=font, fill=255)
    output_buffer = io.BytesIO()

    image.save(output_buffer, format='JPEG')
    byte_data = output_buffer.getvalue()
    baidu_ocr(byte_data)


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def baidu_ocr(byte_data=None):
    from aip import AipOcr

    """ 你的 APPID AK SK """
    APP_ID = '16186054'
    API_KEY = 'X8cp7OZhR8STurccUUx03qna'
    SECRET_KEY = 'p4bOAUYakCUY6TLQaDG6KZDyUXfrT6eS'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # image = get_file_content('dp_woff.jpg')

    """ 调用通用文字识别, 图片参数为本地图片 """
    pic_json = client.basicAccurate(byte_data)
    pic_str = ""
    for info in pic_json['words_result']:
        pic_str += info['words']

    onlineFonts = TTFont('dp_woff.txt')
    keys = onlineFonts.getGlyphNames()
    keys.remove('glyph00000')
    keys.remove('x')
    for index, info in enumerate(keys):
        print(info, pic_str[index])


if __name__ == '__main__':
    # get_word_position()  # svg图片识别
    parse_woff_type()  # eot,woff 图片字体识别
    # dic = {'a': '1', 'b': '2'}
    # print(list(dic.keys())[list(dic.values()).index("1")])
