import json


def get_data_from_file(file, newscode=1, index_date=2, index_title=3):
    events = []
    with open("documents/{}".format(file), "r", encoding="utf-8") as f:
        f.readline()
        for line in f.readlines():
            line_split = line.split(",")
            if len(line_split[index_date].strip('"').split(" ")) > 1:
                events.append({"newscode": line_split[newscode].strip('"'),
                               "date": line_split[index_date].strip('"').split(" ")[0],
                               "title": line_split[index_title].strip('"'),
                               "Time": line_split[index_date].strip('"').split(" ")[1]})
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
                 "Time": line_split[2].strip('"').split(" ")[1]})
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
