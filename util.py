from preprocessing import extract_danmu
from urls import *




'''
此文件用来分析辨别=识处理danmu文件中的机器弹幕


'''



def count_sentences():
    dict = {}
    with open(danmu_dir, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            dict[line] = dict.get(line, 0) + 1
            pass
        # 根据value对dict排序
        dict = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
        count = open(count_dir, 'w+', encoding='utf-8')
        count.writelines([f'{word[0]}-{word[1]}\n' for word in dict if word[1]>50])
    pass


if __name__ == '__main__':
    extract_danmu('./138243/danmu-2021-4-10.txt', mode='w+')
    for x in range(11, 15):
        dir = f'./138243/danmu-2021-4-{x}.txt'
        extract_danmu(dir, mode='a+')
    count_sentences()