from preprocessing import extract_danmu
from urls import *
from preprocessing import *


'''
TODO:
有些弹幕里含有'\n'等字符，会导致一行读不完全，导致出错
SOLVE:
在每条弹幕结尾添加‘%EOF\n’结束符，若没有读到就读取下一行添加到本行，知道遇到结束符
'''

# 添加自定义终止符
def add_stopsign(addrs, mode='w+'):
    for addr in addrs:
        lines = []
        with open(addr, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(addr, mode, encoding='utf-8') as f:
            for line in f.readlines():
                if not line.endswith('%EOF\n'):
                    f.write(f"{line.rstrip()}%EOF\n")
                else:                   # 有终止符，就直接写回
                    f.write(line)
    pass



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
    # 添加EOF
    addrs = []
    for x in range(16, 17):
        addrs.append(f'./138243/danmu-2021-4-{x}.txt')
        # extract_danmu(dir, mode='a+')
    # add_stopsign(addrs, mode='w+')

    # 获取弹幕信息
    extract_danmu(addrs)

    # count_sentences()