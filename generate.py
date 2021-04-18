from os import path
import io
import string
import re
from wordcloud import WordCloud, ImageColorGenerator
from urls import *
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

'''
TODO:
大多数中文字体文件，不能显示Emoji；英文字体又没有汉字。
所以先暂时把所有Emoji都屏蔽了

'''

def extract_freq(addr=segmented_dir):
    freqs = {}
    with io.open(addr, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            # word, freq = line.rstrip().split('-')
            line = line.split('-')
            freq =int(line[-1])
            if freq > 40:
                freqs["".join(line[0:-1]).upper()] = freq
            pass
    return freqs

def generate_by_freq(freqs, addr=segmented_dir, mask_addr='家猪头.png'):

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

    mask = np.array(Image.open(mask_addr))

    wc = WordCloud(
        background_color='black',
        font_path='msyh.ttf',
        # font_path='segoeui.ttf',
        max_words=200,
        max_font_size=150,
        mask=mask,
        width=1600,
        height=900,
        margin=10,
        random_state=42,
        regexp=regexp,
    )
    wc.generate_from_frequencies(freqs)

    mask_color = ImageColorGenerator(mask)
    wc.recolor(color_func=mask_color)
    wc.to_file('wordcloud.jpg')
    pass





if __name__ == '__main__':
    print('main')
    generate_by_freq(extract_freq())