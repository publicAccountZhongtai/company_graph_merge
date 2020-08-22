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
from fuzzywuzzy import fuzz
import operator
from tqdm import tqdm
from random import randint

__author__ = 'sheng'
"""风险类型关键词以及所对应的风险类型词典，类型标号0的代表未知权重"""
fenxian_key_word = {"负面": "信用风险1", "股权质押": "信用风险2", "冻结": "信用风险2", "风险提示": "信用风险3", "资产冻结": "信用风险4", "债闪崩": "信用风险5",
                    "暂停交易": "信用风险6", "只偿还特定": "信用风险7",
                    "未按期兑付": "信用风险8", "债券评级调低": "信用风险9", "未能按期兑付": "信用风险7", "债务评级调低": "信用风险6", "违约": "信用风险5",
                    "重大仲裁": "法律风险5", "近期诉讼": "法律风险2", "涉案金额": "法律风险3", "估值波动较大": "市场风险1", "临时停牌": "市场风险2",
                    "交易异常波动": "市场风险3",
                    "退市": "市场风险5", "价格异动": "市场风险4", "子公司债务逾期": "子公司风险1", "子公司累计逾期债务": "子公司风险2", "被调查": "高管风险1",
                    "被指行贿": "高管风险2",
                    "企业起拍": "高管风险3", "陷阱": "高管风险4", "破产重整": "经营风险2", "破产清算": "经营风险3", "业务总量大幅萎缩": "经营风险1",
                    "股份冻结": "经营风险2",
                    "落幕": "经营风险0",
                    "恶化": "信用风险0",
                    "反面": "信用风险0",
                    "警报": "信用风险0",
                    "骤降": "信用风险0",
                    "暴雷": "信用风险0",
                    "爆雷": "信用风险0",
                    "按约偿付": "信用风险0",
                    "债务劫": "信用风险0",
                    "预警": "信用风险0",
                    "警示": "信用风险0",
                    "互保地雷阵": "信用风险0",
                    "异动": "信用风险0",
                    "崩塌": "信用风险0",
                    "下调信用等级": "信用风险0",
                    "只偿还": "信用风险0",
                    "债项评级": "信用风险0",
                    "债务评级": "信用风险0",
                    "信用等级": "信用风险0",
                    "不确定性": "信用风险0",
                    "未足额兑付": "信用风险0",
                    "按期兑付": "信用风险0",
                    "债卷暂停": "信用风险0",
                    "监管处罚": "法律风险0",
                    "合同纠纷": "法律风险0",
                    "罚单": "法律风险0",
                    "侵权": "法律风险0",
                    "欠薪": "法律风险0",
                    "财务造假": "法律风险0",
                    "通报批评": "市场风险0",
                    "子公司起诉": "子公司风险0",
                    "子公司诉讼": "子公司风险0",
                    "取消业务资格": "子公司风险0",
                    "行政清理": "子公司风险0",
                    "撤销": "子公司风险0",
                    "权钱交易": "高管风险0",
                    "限制消费": "高管风险0",
                    "失信": "高管风险0",
                    "公开审理": "高管风险0",
                    "惩戒": "高管风险0",
                    "后台曝光": "高管风险0",
                    "高层震荡": "高管风险0",
                    "深陷": "经营风险0",
                    "资金困局": "经营风险0",
                    "打击": "经营风险0",
                    "收缩": "经营风险0",
                    "定局": "经营风险0",
                    "警钟长鸣": "经营风险0",
                    "踩雷": "经营风险0",
                    "大跌": "经营风险0",
                    "坏账": "经营风险0",
                    "亏损": "经营风险0",
                    "公司重整": "经营风险0",
                    "不良贷款": "经营风险0",
                    }
"""标题中包含以下关键词代表与企业有关"""
huaxin_key_word = ["华信", "叶简明", "秦霞", "苏卫忠", "熊凤生", "李勇", "李山"]
gaoguan = ["叶简明", "秦霞", "苏卫忠", "熊凤生", "李勇", "李山", "许朋明", "纪志强", "李洪彬", "宋丽娜", "徐敏", "高延林"]
jinmao_key_word = ["金茂", "许朋明", "纪志强", "李洪彬", "宋丽娜", "徐敏", "高延林"]


def get_fenxian(title):
    """字典存入每个风险类别所对应的判断分数，
    最后返回分数最高的前三名，并且保证前三名得分都超过80，否则只返回超过80的风险类型
    这一步是为了更好的处理标题中带有多种风险类型的情况"""
    fengxian_score = {}
    for key, word in fenxian_key_word.items():
        fengxian_score[word] = max(fengxian_score.get(word, 0), fuzz.partial_ratio(key, title))
    for g in gaoguan:
        if fuzz.partial_ratio(g, title) > 80:
            fengxian_score['高管风险0'] = max(fengxian_score.get("高管风险0", 0), fuzz.partial_ratio(g, title))
            break
    temp_result = sorted(fengxian_score.items(), key=operator.itemgetter(1), reverse=True)[:3]
    result = []
    for r in temp_result:
        if r[1] > 80:
            result.append(r)
    return result


def from_title_get_fengxian(event):
    if fuzz.partial_ratio("华信", event) > 80:
        company = "华信"
    elif fuzz.partial_ratio("金茂", event) > 80:
        company = "金茂"
    else:
        company = ""
    result = get_fenxian(event)
    if len(result) == 0:
        fengxian = ""
    else:
        fengxian = ""
        for r in result:
            fengxian += r[0]
    return company, fengxian


def from_title_get_radio(event):
    """
    返回雷达图的指标数值
    :param event:
    :return:
    """
    index_one = randint(1, 100)
    index_two = randint(1, 100)
    index_three = randint(1, 100)
    index_four = randint(1, 100)
    index_five = randint(1, 100)
    return index_one, index_two, index_three, index_four, index_five


def input_title_get_fengxian(event):
    if fuzz.partial_ratio("华信", event) > 80:
        print("判断与华信有关")
    elif fuzz.partial_ratio("金茂", event) > 80:
        print("判断与金茂有关")
    else:
        print("无关标题")
    result = get_fenxian(event)
    if len(result) == 0:
        print("判断风险类型为无！")
    else:
        for r in result:
            print("判断的风险类型：%s，获得分数：%s" % (r[0], r[1]))


def input_file_get_accuracy_rate():
    events, categorys = [], []
    # 将事件标题以及所对应的风险类型全部读取到两个列表中
    with open('documents/events.tsv', "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip().split("\t")
            events.append(line[1])
            categorys.append(line[0])
    total, score = 0, 0
    for event, category in tqdm(zip(events, categorys)):
        total += 1
        print(total)
        print("新闻标题：%s,风险类型：%s" % (event, category))
        if fuzz.partial_ratio("华信", event) > 80:
            print("判断与华信有关")
        elif fuzz.partial_ratio("金茂", event) > 80:
            print("判断与金茂有关")
        else:
            print("无关标题")
            if category == "无":
                score += 1
            else:
                print(event, category)
                # input()
            continue
        result = get_fenxian(event)
        if len(result) == 0:
            print("判断风险类型为无！")
            temp_result = "无"
        else:
            temp_result = result[0][0][:-1]
            # for r in result:
            #     print("判断的风险类型：%s，获得分数：%s" % (r[0], r[1]))
        # input()
        if temp_result == category:
            score += 1
        else:
            print(event, category, result)
            # input()
    print("准确率为：%d/%d，%d%%" % (score, total, score / total * 100))


def main():
    # input_file_get_accuracy_rate()
    # return
    while True:
        event_title = input("请输入标题（回车结束）：")
        input_title_get_fengxian(event_title)


if __name__ == '__main__':
    main()
    pass
