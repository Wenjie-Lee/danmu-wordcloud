import os
from typing import List
from urls import *
import jieba
import preprocessing


curdir = os.getcwd()


# 添加用户自定义词汇
def add_user_words():
    jieba.load_userdict(user_words_dir)
    # with open(user_words_dir, 'r', encoding='utf-8') as f:
    #     for line in f:
    #         jieba.add_word(line.rstrip('\n'))
    #         pass
    pass

add_user_words()
stopwords = preprocessing.stopwords()
# excludes = excludes()

# 将文本分解为词，统计词频
def segment_whole(addrs:List[str], freq=50):
    print('Segment whole...')
    dict = {}
    for addr in addrs:
        if not os.path.basename(addr).startswith('extracted-danmu'):
            continue
        with open(addr, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                segs = jieba.lcut(line.split('%')[4])
                for word in segs:
                    if word in stopwords:
                        continue
                    dict[word] = dict.get(word, 0) + 1
    dict = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
    roomid = addrs[0].split('/')[1]
    start = os.path.basename(addrs[0])[16:-4]
    end = os.path.basename(addrs[-1])[16:-4]
    file = f"./{roomid}/segmented/wordscount-{start}~{end}.txt"
    dst = open(file, 'w+', encoding='utf-8')
    dst.writelines([f'{word[0]} % {word[1]}\n' for word in dict if word[1] >= freq])
    pass

# 以小时为单位统计词频，并记录到文件中
# 以小时为单位，统计当前时间文本词汇的词频。词频阈值val
# 且每小时保存一下当前dict中，超过val的词汇以及词频
def segment_per_hour(addr:str, freq=30):
    dict = {}
    def _getdate(first):
        # 还不来？？%2021-04-10 18:00:42\n
        date = first.split('%')[-1]
        x = date.split(' ')
        _,mm,dd = x[0].split('-')
        hh = x[1].split(':')[0]
        return int(mm),int(dd),int(hh)
    with open(addr, 'r', encoding='utf-8') as f:
        _,filedir,_,filename = addr.split('/')
        filename = f"segment-per-hour-{filename[16:]}"
        dst = open(os.path.join(filedir,'extracted',filename), 'w+', encoding='utf-8')
        # 转而根据实际时间来记录弹幕词频
        # 每天开始时间 00
        hour = 0
        mm,dd,hh = 0,0,0
        while hour < 24:
            line = f.readline()
            if not line:                                            # 若读到文件尾，跳出
                break
            mm,dd,hh = _getdate(line)
            if hh > hour:    # 已经达到下一个时段
                # 写入数据
                print(f'>>>>>>>>>>>>> 写入month:{mm} day:{dd} hour:{hour} >>>>>>>>>>>>>>>')
                l = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
                dst.write(f"Date-{mm}-{dd}-{hour}%")
                # 只有词频超过freq，才写入
                # 保证单词被@分开，且只有一个单词时不用@
                if len(l) != 0:
                    first = True
                    for li in l:
                        if li[1] >= freq:
                            if first:
                                dst.write(f"{li[0]}_{li[1]}")
                                first = False
                            else:
                                dst.write(f"@{li[0]}_{li[1]}")
                dst.write('%EOF\n')
                # 更新时间
                hour += 1
                # 清理dict
                dict.clear()
                pass
            segs = jieba.lcut(line.split('%')[-2])      # 截取弹幕文本部分
            for word in segs:
                if word in stopwords:
                    continue
                dict[word] = dict.get(word, 0) + 1
            pass

        # 弹幕读取完毕，但时间可能有剩余
        while hour < 24:
            print(f'>>>>>>>>>>>>> 写入month:{mm} day:{dd} hour:{hour} >>>>>>>>>>>>>>>')
            # 对dict排序，并写入文件
            dst.write(f"Date-{mm}-{dd}-{hour}%")
            if not dict:
                l = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
                # 保证单词被@分开，且只有一个单词时不用@
                if len(l) != 0:
                    first = True
                    for li in l:
                        if li[1] >= freq:
                            if first:
                                dst.write(f"{li[0]}_{li[1]}")
                                first = False
                            else:
                                dst.write(f"@{li[0]}_{li[1]}")
                dict.clear()
            dst.write('%EOF\n')
            hour += 1
            pass
    pass

def group_segment_per_hour(addrs:List[str], freq):
    print('Group segment per hour...')
    for addr in addrs:
        if not os.path.basename(addr).startswith('extracted-danmu'):
            continue
        print('处理：', addr)
        segment_per_hour(addr, freq=freq)
        pass
    pass

def competitor_per_hour(addrs:List[str], freq=10):
    # 建立一个包含所有词汇的表table，和idx记录词汇索引
    roomid = addrs[0].split('/')[1]
    start = os.path.basename(addrs[0])[17:-4]
    end = os.path.basename(addrs[-1])[17:-4]
    idx = {}        # 用来记录（词汇，索引）对
    i = 0
    table = []
    dates = []
    # 先构建词汇字典
    with open(f"./{roomid}/segmented/wordscount-{start}~{end}.txt", 'r', encoding='utf-8') as f:
        for line in f.readlines():
            word = line.split('%')[0].rstrip()      # 乌迪尔 % 142
            if word not in idx:
                idx[word] = i
                i += 1
            table.append([word, 0])

    for addr in addrs:
        with open(addr, 'r', encoding='utf-8') as f:
            dst = open(f"./{roomid}/csv/csv-{start}~{end}.csv", 'w+', encoding='utf-8')
            for line in f.readlines():
                # 默认当前时段所有词的词频为0
                for t in table:
                    t.append(t[1])

                # 再更新这个小时新增的词汇词频
                date,words = line.split('%')[0:2]
                dates.append(date)
                if words == '':
                    continue
                words = words.split('@')
                for word in words:
                    # print(word)
                    lword, lfreq = word.split('_')
                    table[idx[lword]].append(lfreq)
            datestr = []
            # 按csv格式打印数据
            dst.write('name,')
            for date in dates:
                _,mm,dd,hh = date.rstrip().split('-')
                datestr.append(f"{mm}/{dd} {hh}")
            dst.write(f"{','.join(datestr)}\n")
            for t in table:
                tstr = [ str(x) for x in t]
                dst.write(f"{','.join(tstr)}\n")
                pass
        pass

def next_minutes(t1, t2, val=2):
    if t1[0] == t2[0]:                  # hour
        if t1[1] == t2[1]:              # minute
            return False
        return t1[1] > (t2[1] + val)
    elif t1[0] == t2[0] + 1:
        return t1[1] > (t2[1] + val) % 60
    return t1[1] > t2[1]

# 以val分钟为单位统计词频，只统计频率较高的一部分
def segment_per_minute(addr, freq=5, val=5):
    dict = {}
    def _getdate(first):
        # 2021-04-10 18:00:42_还不来？？
        # 还不来？？%2021-04-10 18:00:42\n
        date = first.split('%')[-1]
        x = date.split(' ')
        _,mm,dd = x[0].split('-')
        hh,mi = x[1].split(':')[0:2]
        return int(mm),int(dd),int(hh),int(mi)
    with open(addr, 'r', encoding='utf-8') as f:
        _,filedir,_,filename = addr.split('/')
        filename = f"segment_per_minute-{filename[16:]}"
        dst = open(os.path.join(filedir,'extracted',filename), 'w+', encoding='utf-8')
        # 转而根据实际时间来记录弹幕词频
        # 每天开始时间 00:00
        hour, minute = 0, 0
        mm,dd,hh,mi = 0,0,0,0
        while hour < 24:
            line = f.readline()
            if not line:                                            # 若读到文件尾，跳出
                break
            mm,dd,hh,mi = _getdate(line)
            if next_minutes((hh,mi), (hour, minute), val=val):    # 已经达到下一个时段
                # 写入数据
                print(f'>>>>>>>>>>>>>写入month:{mm} day:{dd} hour:{hour} minute:{minute}>>>>>>>>>>>>>>>')
                l = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
                dst.write(f"Date-{mm}-{dd}-{hour}-{minute}%")
                # 只有词频超过freq，才写入
                # 保证单词被@分开，且只有一个单词时不用@
                if len(l) != 0:
                    first = True
                    for li in l:
                        if li[1] >= freq:
                            if first:
                                dst.write(f"{li[0]}_{li[1]}")
                                first = False
                            else:
                                dst.write(f"@{li[0]}_{li[1]}")
                dst.write('%EOF\n')
                # 更新时间
                minute += val
                if minute >= 60:
                    hour += 1
                    minute %= 60
                # 清理dict
                dict.clear()
                pass
            segs = jieba.lcut(line.split('%')[-2])      # 截取弹幕文本部分
            for word in segs:
                if word not in stopwords:
                    dict[word] = dict.get(word, 0) + 1
            pass
        # 最后val分钟有剩余
        # 弹幕读取完毕，但时间可能有剩余
        while hour < 24:
            print(f'>>>>>>>>>>>>>写入month:{mm} day:{dd} hour:{hour} minute:{minute}>>>>>>>>>>>>>>>')
            # 对dict排序，并写入文件
            dst.write(f"Date-{mm}-{dd}-{hour}-{minute}%")
            if not dict:
                l = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
                # 保证单词被@分开，且只有一个单词时不用@
                if len(l) != 0:
                    first = True
                    for li in l:
                        if li[1] >= freq:
                            if first:
                                dst.write(f"{li[0]}_{li[1]}")
                                first = False
                            else:
                                dst.write(f"@{li[0]}_{li[1]}")
                dict.clear()
            dst.write('%EOF\n')
            # 更新时间
            minute += val
            if minute >= 60:
                hour += 1
                minute %= 60
            pass
    pass

def group_segment_per_minute(addrs:List[str], freq, val):
    for addr in addrs:
        if not os.path.basename(addr).startswith('extracted-danmu'):
            continue
        print('处理：', addr)
        segment_per_minute(addr, freq=freq, val=val)
        pass
    pass

if __name__ == '__main__':
    print('main')

    # t1 = (5,9,18)
    # t2 = (4,10,19)
    # print(is_closer(t1,t2))

    extracted_danmus = []
    for d in os.listdir('./138243/extracted/'):
        if d.startswith('extracted-danmu'):
            extracted_danmus.append(f"./138243/extracted/{d}")
        pass
    print(extracted_danmus)

    my_freq = 50
    # segment_whole(extracted_danmus, freq=my_freq)

    # segment_per_hour(addr='./138243/extracted/extracted-danmu-2021-4-16.txt', freq=my_freq)
    # group_segment_per_hour(extracted_danmus, freq=my_freq)

    # segment_per_minute(addr='./138243/extracted/extracted-danmu-2021-4-16.txt', freq=my_freq, val=5)
    #                                       词频最低为5， 统计时间为5分钟
    # group_segment_per_minute(extracted_danmus, freq=5, val=5)

    segment_per_hour = []
    for d in os.listdir('./138243/extracted/'):
        if d.startswith('segment-per-hour'):
            segment_per_hour.append(f"./138243/extracted/{d}")
        pass
    print(segment_per_hour)

    competitor_per_hour(segment_per_hour, freq=my_freq)
