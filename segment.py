import os
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
def segment_whole(freq=10):
    dict = {}
    with open(extract_danmu_dir, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            segs = jieba.lcut(line)
            for word in segs:
                if word not in stopwords:
                    dict[word] = dict.get(word, 0) + 1

    dict = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
    dst = open(segmented_dir, 'w+', encoding='utf-8')
    dst.writelines([f'{word[0]}_{word[1]}\n' for word in dict if word[1] >= freq])
    pass

# 比较月、天、时
def next_hour(t1, t2):
    if t1[0] == t2[0]:              # mm
        if t1[1] == t2[1]:          # dd
            if t1[2] == t2[2]:      # hh
                return False
            return t1[2] > t2[2]
        return t1[1] > t2[1]
    return t1[0] > t2[0]

# 以小时为单位统计词频，并记录到文件中
# 以小时为单位，统计当前时间文本词汇的词频。词频阈值val
# 且每小时保存一下当前dict中，超过val的词汇以及词频
def segment_per_hour(freq=10):
    dict = {}
    def _getdate(first):
        # 2021-04-10 18:00:42_还不来？？
        date = first.split('_')[0]
        # print(date)
        x = date.split(' ')
        _,mm,dd = x[0].split('-')
        hh = x[1].split(':')[0]
        return mm,dd,hh
    with open(extract_danmu_time_dir, 'r', encoding='utf-8') as f:
        dst = open(segmented_hour_dir, 'w+', encoding='utf-8')
        lines = f.readlines()
        fmm,fdd,fhh = _getdate(lines[0])
        for line in lines:
            mm,dd,hh = _getdate(line)
            if next_hour((mm, dd, hh), (fmm, fdd, fhh)):        # 这条弹幕属于下一个小时段
                print(f'>>>>>>>>>>>>>>>>>>写入month:{fmm} day:{fdd} hour:{fhh}>>>>>>>>>>>>>>>>>>>>')
                # 对dict排序，并写入文件
                l = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
                dst.write(f"Date-{fmm}-{fdd}-{fhh}%")
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
                # 更新时间，清理dict
                dict.clear()
                fmm, fdd, fhh = mm, dd, hh
            # 这条弹幕属于这一小时段
            segs = jieba.lcut(''.join(line.rstrip().split('_')[1:]))      # 截取弹幕文本部分
            for word in segs:
                if word not in stopwords:
                    dict[word] = dict.get(word, 0) + 1

        # 可能有剩余
        print(f'>>>>>>>>>>>>>>>>>>写入month:{fmm} day:{fdd} hour:{fhh}>>>>>>>>>>>>>>>>>>>>')
        if not dict:      # 有可能这个时段没有弹幕，dict为空
            l = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
            dst.write(f"Date-{fmm}-{fdd}-{fhh}%")
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
            # 更新时间，清理dict
            dict.clear()
    pass

def competitor_per_hour(freq=10):
    # 建立一个包含所有词汇的表table，和idx记录词汇索引
    f = open(segmented_dir, 'r', encoding='utf-8')
    idx = {}        # 用来记录（词汇，索引）对
    i = 0
    table = []
    dates = []
    for line in f.readlines():
        wordfreq = line.split('_')      # 乌迪尔_142
        if wordfreq[0] not in idx:
            idx[wordfreq[0]] = i
            i += 1
        table.append([wordfreq[0], 0])
    with open(segmented_hour_dir, 'r', encoding='utf-8') as f:
        dst = open(competitor_dir, 'w+', encoding='utf-8')
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
            datestr.append(f"{mm}/{dd}/{hh}")
        dst.write(f"{','.join(datestr)}\n")
        for t in table:
            tstr = [ str(x) for x in t]
            dst.write(f"{','.join(tstr)}\n")
            pass

def next_minutes(t1, t2, val=2):
    if t1[0] == t2[0]:              # mm
        if t1[1] == t2[1]:          # dd
            if t1[2] == t2[2]:      # hh
                if t1[3] == t2[3]:
                    return False
                return t1[3] > (t2[3] + val)  # 隔val分钟
            if t1[2] == t2[2] + 1:  # 隔1个小时，仍需要考虑分钟
                return t1[3] > (t2[3] + val) % 60
            return t1[2] > t2[2]
        return t1[1] > t2[1]
    return t1[0] > t2[0]

# 以val分钟为单位统计词频，只统计频率较高的一部分
def segment_per_minute(freq=5, val=5):
    dict = {}
    def _getdate(first):
        # 2021-04-10 18:00:42_还不来？？
        date = first.split('_')[0]
        # print(date)
        x = date.split(' ')
        _,mm,dd = x[0].split('-')
        hh,mi = x[1].split(':')[0:2]
        return int(mm),int(dd),int(hh),int(mi)
    with open(extract_danmu_time_dir, 'r', encoding='utf-8') as f:
        dst = open(segmented_minutes_dir, 'w+', encoding='utf-8')
        lines = f.readlines()
        fmm,fdd,fhh,fmi = _getdate(lines[0])
        for line in lines:
            mm,dd,hh,mi = _getdate(line)
            if next_minutes((mm, dd, hh, mi), (fmm, fdd, fhh, fmi), val=val):           # 这条弹幕属于下一个时段
                print(f'>>>>>>>>>>>>>写入month:{fmm} day:{fdd} hour:{fhh} minute:{fmi}>>>>>>>>>>>>>>>')
                # 对dict排序，并写入文件
                # print(dict)
                l = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
                dst.write(f"Date-{fmm}-{fdd}-{fhh}-{fmi}%")
                # 只有词频超过freq，才写入
                dst.writelines([f"@{li[0]}_{li[1]}" for li in l[:1] if li[1] > freq])
                dst.writelines([f"@{li[0]}_{li[1]}" for li in l[1:] if li[1] > freq])
                dst.write('%EOF\n')
                # 更新时间，清理dict
                dict.clear()
                fmm, fdd, fhh, fmi = mm, dd, hh, mi
            # 这条弹幕属于这一时段
            # print(''.join(line.rstrip().split('_')[1:]))
            segs = jieba.lcut(''.join(line.rstrip().split('_')[1:]))      # 截取弹幕文本部分
            # print(segs)
            for word in segs:
                if word not in stopwords:
                    dict[word] = dict.get(word, 0) + 1

        # 可能有剩余
        print(f'>>>>>>>>>>>>>写入month:{fmm} day:{fdd} hour:{fhh} minute:{fmi}>>>>>>>>>>>>>>>')
        # 对dict排序，并写入文件
        l = sorted(dict.items(), key=lambda kv:(kv[1],kv[0]), reverse=True)
        dst.write(f"Date-{fmm}-{fdd}-{fhh}-{fmi}%")
        dst.writelines([f"@{li[0]}_{li[1]}" for li in l if li[1] > freq])
        dst.write('%EOF\n')
        # 更新时间，清理dict
        dict.clear()
    pass



if __name__ == '__main__':
    print('main')
    # add_user_words()
    # segment_whole('./txt/extract_danmu.txt')
    # segment_whole('./txt/test.txt')

    # str = '还不来？？_2021-04-10 18:00:42.189514'
    # date = str.split('-')
    # mm = date[1]
    # dd, hh = date[2].split(' ')
    # hh = hh.split(':')[0]
    # print(mm,dd,hh)

    # t1 = (5,9,18)
    # t2 = (4,10,19)
    # print(is_closer(t1,t2))

    # segment_whole(freq=10)
    # segment_per_hour(freq=10)
    competitor_per_hour()

    # t1 = (4,10,17,54)
    # t2 = (4,10,15,59)
    # print(minutes_closer(t1, t2, val=3))
    # preprocessing.extract_danmu_time('./txt/test.txt')
    # segment_per_minute(freq=5, val=2)

    # t1 = '驴来驴来驴来驴来驴来驴来驴来驴来驴来驴来'
    # print(jieba.cut(t1))
    # print(jieba.lcut(t1))