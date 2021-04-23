import os
import io
import string
from PIL import Image
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator

import matplotlib.pyplot as plt
from urls import *

'''
TODO:
大多数中文字体文件，不能显示Emoji；英文字体又没有汉字。
所以先暂时把所有Emoji都屏蔽了

'''

def __extract_freq(addr, freq_threshold):
    freqs = {}
    with io.open(addr, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            word, freq = line.split('%')
            word = word.strip()
            freq = int(freq.strip())
            if freq > freq_threshold:
                freqs[word.upper()] = freq
            pass
    return freqs

def generate_by_freq(addr, freq_threshold=40, mask_addr='家猪头.png'):
    # Regex
    # the regex used to detect words is a combination of normal words, ascii art, and emojis
    # 2+ consecutive letters (also include apostrophes), e.x It's
    normal_word = r"(?:\w[\w']+)"
    # 2+ consecutive punctuations, e.x. :)
    ascii_art = r"(?:[{punctuation}][{punctuation}]+)".format(punctuation=string.punctuation)
    # a single character that is not alpha_numeric or other ascii printable
    emoji = r"(?:[^\s])(?<![\w{ascii_printable}])".format(ascii_printable=string.printable)
    regexp = r"{normal_word}|{ascii_art}|{emoji}".format(normal_word=normal_word, ascii_art=ascii_art,
                                                         emoji=emoji)
    freqs = __extract_freq(addr, freq_threshold)
    mask = np.array(Image.open(mask_addr))

    wc = WordCloud(
        font_path='msyh.ttf',
        # font_path='segoeui.ttf',
        max_words=300,
        max_font_size=200,
        background_color=None,
        mode='RGBA',
        mask=mask,
        colormap='YlGn',
        width=1920,
        height=1080,
        margin=10,
        random_state=42,
        regexp=regexp,
    )
    wc.generate_from_frequencies(freqs)

    # mask_color = ImageColorGenerator(mask)
    # wc.recolor(color_func=mask_color)
    roomid = addr.split('/')[1]
    period = os.path.basename(addr)[11:-4]
    wc.to_file(f"./{roomid}/wordcloud/wordcloud-{period}.png")
    pass





if __name__ == '__main__':
    print('main')
    generate_by_freq(addr='./138243/segmented/wordscount-2021-4-10~2021-4-18.txt',
                     freq_threshold=50,
                     mask_addr='家猪头.png')