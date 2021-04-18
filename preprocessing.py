import os
from urls import *
# from io import StringIO

curdir = os.getcwd()


'''
                  0        1  2     3 4                  -1                         结束符
Danmaku: 128697369,bbbaifei,14,驴酱灬,8,今天不直播的，理解一下,2021-04-14 18:46:55.468033%EOF

'''

# 根据excludes.txt构造一个集合，排除匹配的弹幕
def excludes():
    s = set()
    with open(excludes_dir, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            # 我来学技术来了-177
            s.add(line.strip().split('-')[0])         # 去除前后空格, \t, \n等
            pass
    return s
    pass

# 根据stopwords.txt和user_blocked.txt构造一个集合
def stopwords():
    s = set()
    with open(stopwords_dir, 'r', encoding='utf-8')as f:
        for line in f:
            s.add(line.rstrip('\n'))      # 去掉换行符
            pass
    with open(user_blocked_dir, 'r', encoding='utf-8')as f:
        for line in f:
            s.add(line.rstrip('\n'))      # 去掉换行符
            pass
    return s

excludes = excludes()

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
            f.writelines([ f"{line.rstrip()}%EOF\n" for line in lines ])
    pass

# 提取文本包含’弹幕-时间‘属性
def extract_danmu_time(addr, mode='w+'):
    with open(addr, 'r', encoding='utf-8') as f:
        dst = open(os.path.join(txt_dir, 'extract_danmu_time.txt'), mode, encoding='utf-8')
        while True:
            line = f.readline()
            if not line:        # 读到空串“”，即为末尾；文本中间的空串其实是“\n”
                break
            # while not line.endswith('%EOF\n'):
            #     line = line.rstrip() + f.readline()
            line = line.strip().lower().split(',')[5:]
            # print(line)
            if line[0] in excludes:      # 排除机器人弹幕
                continue
            dst.write(f"{line[-1].split('.')[0]}_{''.join(line[0:-1])}\n")


# 提取文本仅包含’弹幕‘属性
def extract_danmu(addr, mode='w+'):
    with open(addr, 'r', encoding='utf-8') as f:
        dst = open(extract_danmu_dir, mode, encoding='utf-8')
        while True:
            line = f.readline()
            if not line:        # 读到空串“”，即为末尾；文本中间的空串其实是“\n”
                break
            # while not line.endswith('%EOF\n'):
            #     line = line.rstrip() + f.readline()
            line = ''.join(line.strip().lower().split(',')[5:-1])
            if line in excludes:      # 排除机器人弹幕
                continue
            dst.write(f"{line}\n")

# 提取弹幕牌子属性
def extract_user(addr, mylabel, mode='w+'):
    with open(addr, 'r', encoding='utf-8') as f:
        users = {}       # 记录名字和索引
        idx = 0
        data = []       # 记录名字对应的数据, level,label,llevel,freq
        labels = {}     # 记录牌子名字和数量
        levels = {}     # 记录用户等级分布
        mylabel = mylabel   # 主播的牌子名称
        llevels = {}    # 记录主播牌子等级分布
        dst = open(extract_user_dir, mode, encoding='utf-8')
        for line in f.readlines():
            if line.endswith('EOF\n'):
                splited = line.rstrip().lower().split(',')
                name, level, label, llevel = splited[1:5]
                level, llevel = int(level), int(llevel)
                content = ''.join(splited[5:-1])
                # 排除机器人弹幕
                if line in excludes:
                    continue
                if name not in users:           # 新用户
                    users[name] = idx
                    idx += 1
                    data.append([level, label, llevel, 0])
                    # 更新等级信息
                    levels[level] = levels.get(level, 0) + 1
                    # 更新牌子信息
                    if label == '':
                        continue
                    labels[label] = labels.get(label, 0) + 1
                    #更新主播牌子的等级信息
                    if label == mylabel:
                        llevels[llevel] = llevels.get(llevel, 0) + 1

                else:                           # 旧用户，更新频率
                    data[users[name]][-1] += 1
            pass

        # 写入数据
        with open(active_user_dir, 'w+', encoding='utf-8') as f:
            f.write(f"活跃用户数量：\n{idx}\n")
            # 分区域 0-4，5-9，10-19，20-29，30-39，40-max
            f.write("活跃用户等级分布：\n")
            count = [0]*6
            for i,j in levels.items():
                if 0 <= i <= 4:
                    count[0] += j
                elif 5 <= i <= 9:
                    count[1] += j
                elif 10 <= i <= 19:
                    count[2] += j
                elif 20 <= i <= 29:
                    count[3] += j
                elif 30 <= i <= 39:
                    count[4] += j
                else:
                    count[5] += j
                pass
            count = [str(x) for x in count]
            f.write(f"0~5: {count[0]}\n")
            f.write(f"6~10: {count[1]}\n")
            f.write(f"11~20: {count[2]}\n")
            f.write(f"21~30: {count[3]}\n")
            f.write(f"31~40: {count[4]}\n")
            f.write(f"41~Max: {count[5]}\n")
            # 分区域 1-5，6-9，10-15，16-19，20-25，26-29,30-Max
            f.write("主播牌子等级分布情况：\n")
            count = [0]*7
            for i,j in llevels.items():
                if 1 <= i <= 5:
                    count[0] += j
                elif 6 <= i <= 9:
                    count[1] += j
                elif 10 <= i <= 15:
                    count[2] += j
                elif 16 <= i <= 19:
                    count[3] += j
                elif 20 <= i <= 25:
                    count[4] += j
                elif 26 <= i <= 29:
                    count[5] += j
                else:
                    count[6] += j
                pass
            count = [str(x) for x in count]
            f.write(f"1~5: {count[0]}\n")
            f.write(f"6~9: {count[1]}\n")
            f.write(f"10~15: {count[2]}\n")
            f.write(f"16~19: {count[3]}\n")
            f.write(f"20~25: {count[4]}\n")
            f.write(f"26~29: {count[5]}\n")
            f.write(f"高于30: {count[6]}\n")
            f.write("活跃用户牌子信息：\n")
            labels_sorted = sorted(labels.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
            f.writelines([ f"{i}: {j}\n" for i, j in labels_sorted if j >= 10 ])
        # with open(labels_dir, 'w+', encoding='utf-8') as f:


    pass


if __name__ == '__main__':
    print('main')
    # extract_danmu_time('138243/danmu-2021-4-14.txt')
    # extract_danmu('138243/danmu-2021-4-14.txt')
    # extract_danmu('./txt/test.txt')
    # extract_danmu_time('./txt/test.txt')
    # for s in stopwords():
    #     print(s)
    #     pass

    # 向弹幕文件添加自定义终止符
    # add_stopsign([f'./138243/danmu-2021-4-{x}.txt' for x in range(11, 15)])

    # extract_danmu('./138243/danmu-2021-4-10.txt', mode='w+')
    # for x in range(11, 15):
    #     dir = f'./138243/danmu-2021-4-{x}.txt'
    #     extract_danmu(dir, mode='a+')
    #
    # extract_danmu_time('./138243/danmu-2021-4-10.txt', mode='w+')
    # for x in range(11, 15):
    #     dir = f'./138243/danmu-2021-4-{x}.txt'
    #     extract_danmu_time(dir, mode='a+')

    extract_user('./138243/danmu-2021-4-10.txt', mylabel='驴酱灬', mode='w+')


    # line = 'Danmaku: 175404208,3东大学尹志凯,30,自宇,11,大粪凯：我们队伍有个NT就坐在我旁边，我知道是谁，但是我不说,2021-04-10 22:56:32.581509%EOF'
    # line = line.strip().lower().split(',')[3:5]
    # print(line)