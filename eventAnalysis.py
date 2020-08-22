# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name：   eventAnalysis
  Description :
  Author :    sheng
  date：     2020/2/22
  filename:   eventAnalysis 

-------------------------------------------------
  Change Activity:
          2020/2/22:
-------------------------------------------------
"""
__author__ = 'sheng'
"""对事件进行分析，并测试fuzzy包对于关键词判断的准确性"""


def read_file(filename):
    """读取文件，输入文件名称，返回事件标题列表和时间所对应的风险类型"""
    event, category = [], []  # 事件标题列表以及事件风险类型列表
    with open(filename, 'r', encoding="utf-8") as f:
        f.readline()  # 读取标题行
        for line in f.readlines():
            split_line = line.strip().split(',')
            event.append(split_line[3])  # 事件标题在第四列

            if split_line[-1] == '':  # 分线类型为无
                category.append("无")
            else:
                category.append(split_line[-1])
    return event, category


def save2tsv(event, category):
    """将事件标题以及事件风险类型单独存到一个文件中，便于后期处理"""
    with open("documents/events.tsv", "w", encoding="utf-8") as f:
        for e, c in zip(event, category):
            split_c = c.strip().split('、')
            f.write(','.join(split_c))
            f.write("\t" + e + "\n")


def extract_events():
    """将风险事件文件读取并提取其中的风险事件标题以及风险类型"""
    file1 = '华信.csv'
    file2 = '金茂.csv'
    event1, category1 = read_file(file1)
    event2, category2 = read_file(file2)
    save2tsv(event1 + event2, category1 + category2)


def analysis_event_length():
    """分析风险事件标题的长度以及类型的分布特点"""
    event_length = []
    category_numbers = []
    with open("documents/events.tsv", "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip().split('\t')
            event_length.append(len(line[-1]))
            category_numbers.append(len(line[0].split(',')))
    print(event_length)
    print(category_numbers)


if __name__ == '__main__':
    analysis_event_length()
    pass
