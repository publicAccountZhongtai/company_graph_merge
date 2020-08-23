import json
import random
import datetime
import time

riskType = ["信用", "法律", "市场", "子公司", "高管", "经营"]
riskLevel = ["1", "2", "3", "4", "5"]
relateCompanys = ["华信", "金茂"]


def get_data_from_file(file, newscode=1, index_date=2, index_title=3):
    events = []
    with open("documents/{}".format(file), "r", encoding="utf-8") as f:
        f.readline()
        for line in f.readlines():
            line_split = line.split(",")
            data = line_split[index_date].strip('"').split(" ")[0]
            data_year = data.split("/")[0]
            data_month = data.split("/")[1]
            data_day = data.split("/")[2]
            if len(data_month) == 1:
                data_month = "0" + data_month
            if len(data_day) == 1:
                data_day = "0" + data_day
            data = "/".join([data_year, data_month, data_day])
            data = time.strftime("%Y-%m-%d", time.strptime(data, "%Y/%m/%d"))

            if len(line_split[index_date].strip('"').split(" ")) > 1:
                Time = line_split[index_date].strip('"').split(" ")[1]
                if len(Time) < 8:
                    Time = "0" + Time
                events.append({"newscode": line_split[newscode].strip('"'),
                               "date": data,
                               "title": line_split[index_title].strip('"'),
                               "Time": Time,
                               "riskType": random.choice(riskType),
                               "riskLevel": random.choice(riskLevel),
                               "relateCompany": random.choice(relateCompanys)
                               })
    return events


def extract_csv_json(file):
    events = []
    with open("documents/{}.csv".format(file), "r", encoding="utf-8") as f:
        f.readline()
        for line in f.readlines():
            line_split = line.split(",")
            events.append(
                {"Url": "http://fcnews.finchina.com/newsview/default.aspx?newscode=20171130020005934461",
                 "date": line_split[2].strip('"').split(" ")[0],
                 "title": line_split[3].strip('"'),
                 "Time": line_split[2].strip('"').split(" ")[1],
                 "riskType": random.choice(riskType),
                 "riskLevel": random.choice(riskLevel),
                 })
    with open("static/json/{}.json".format(file), "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False)


def main():
    file3 = "系统开发相关资料/T_NEWS_TEXT_FCDB_新闻主表（新版负面）.csv"
    events = []
    events += get_data_from_file(file3, 1, 2, 4)
    with open("static/json/all_events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False)
    extract_csv_json("华信")
    extract_csv_json("金茂")


if __name__ == '__main__':
    main()
