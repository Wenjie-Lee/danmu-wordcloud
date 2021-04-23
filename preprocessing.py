import os
from urls import *
from typing import List

# from io import StringIO


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

#
def __extract_danmu(addr:str, mode='w+'):
    filedir = os.path.dirname(addr)
    filename = os.path.basename(addr)
    if not filename.startswith('danmu'):        # 保证读取对文件
        return
    # extracted-danmu-2021-4-10.txt
    extracted_name = f"extracted-danmu-{'-'.join(filename.split('-')[1:])}"
    with open(addr, 'r', encoding='utf-8') as f:
        dst = open(os.path.join(filedir, 'extracted', extracted_name), mode, encoding='utf-8')
        while True:
            line = f.readline()
            if not line:        # 读到空串“”，即为末尾；文本中间的空串其实是“\n”
                break
            # while not line.endswith('%EOF\n'):
            splited = line.lower().strip().split(',')
            content = ''.join(splited[5:-1])            # 合成弹幕内容
            send_time = splited[-1].split('.')[0]       # 去掉秒数后的数据
            if content in excludes:      # 排除机器人弹幕
                continue
            dst.write(f"{splited[1]}%{splited[2]}%{splited[3]}%{splited[4]}%{content}%{send_time}\n")

def extract_danmu(addrs:List[str]):
    for addr in addrs:
        __extract_danmu(addr, mode='w+')
        pass
    pass

# 提取弹幕牌子属性
def extract_user(addrs:List[str], mylabel, label_threshold=50, mode='w+'):
    roomid = addrs[0].split('/')[1]
    start = os.path.basename(addrs[0])[11:-4]
    end = os.path.basename(addrs[-1])[11:-4]

    users = {}       # 记录名字和索引
    idx = 0
    data = []       # 记录名字对应的数据, level,label,llevel,freq
    labels = {}     # 记录牌子名字和数量
    levels = {}     # 记录用户等级分布
    mylabel = mylabel   # 主播的牌子名称
    llevels = {}    # 记录主播牌子等级分布
    for addr in addrs:
        with open(addr, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                name, level, label, llevel = line.rstrip().lower().split('%')[0:4]
                level, llevel = int(level), int(llevel)
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
    # 写入数据
    active_user_file = f"./{roomid}/segmented/active_user-{start}~{end}.txt"
    with open(active_user_file, 'w+', encoding='utf-8') as acitve:
        acitve.write(f"统计时间内发过弹幕的活跃用户数量：\n{idx}\n")
        # 分区域 0-4，5-9，10-19，20-29，30-39，40-max
        acitve.write("活跃用户等级分布：\n")
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
        acitve.write(f"0~5: {count[0]}\n")
        acitve.write(f"6~10: {count[1]}\n")
        acitve.write(f"11~20: {count[2]}\n")
        acitve.write(f"21~30: {count[3]}\n")
        acitve.write(f"31~40: {count[4]}\n")
        acitve.write(f"41~Max: {count[5]}\n")
        # 分区域 1-5，6-9，10-15，16-19，20-25，26-29,30-Max
        acitve.write("主播牌子等级分布情况：\n")
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
        acitve.write(f"1~5: {count[0]}\n")
        acitve.write(f"6~9: {count[1]}\n")
        acitve.write(f"10~15: {count[2]}\n")
        acitve.write(f"16~19: {count[3]}\n")
        acitve.write(f"20~25: {count[4]}\n")
        acitve.write(f"26~29: {count[5]}\n")
        acitve.write(f"高于30: {count[6]}\n")
        acitve.write("活跃用户牌子信息：\n")
        labels_sorted = sorted(labels.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
        acitve.writelines([ f"{i}: {j}\n" for i, j in labels_sorted if j >= label_threshold ])
        pass
    pass


if __name__ == '__main__':
    print('main')

    # 向弹幕文件添加自定义终止符
    # add_stopsign([f'./138243/danmu-2021-4-{x}.txt' for x in range(11, 15)])

    # danmus = []
    # for d in os.listdir('./138243/'):
    #     if d.startswith('danmu'):
    #         danmus.append(f"./138243/{d}")
    #     pass
    # print(danmus)
    # extract_danmu(danmus)

    # extract_danmu(['./138243/danmu-2021-4-16.txt'])

    extracted_danmus = []
    for d in os.listdir('./138243/extracted/'):
        if d.startswith('extracted-danmu'):
            extracted_danmus.append(f"./138243/extracted/{d}")
        pass
    print(extracted_danmus)
    extract_user(extracted_danmus, mylabel='驴酱灬', label_threshold=50, mode='w+')
