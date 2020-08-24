import json
import time
import random


def main():
    with open("./static/json/all_events.json", "r", encoding="utf-8") as f:
        all_events = json.load(f)
    with open("./static/json/华信.json", "r", encoding="utf-8") as f:
        huaxin = json.load(f)
    with open("./static/json/金茂.json", "r", encoding="utf-8") as f:
        jinmao = json.load(f)
    with open("./static/json/all_events_add.json", "r", encoding="utf-8") as f:
        all_events_add = json.load(f)
    with open("./static/json/华信_add.json", "r", encoding="utf-8") as f:
        huaxin_add = json.load(f)
    with open("./static/json/金茂_add.json", "r", encoding="utf-8") as f:
        jinmao_add = json.load(f)
    index_all, index_huaxin, index_jinmao = -1, -1, -1
    while True:
        # random_index = random.randint(0, 2)
        random_index = int(input("请输入更新（0，1，2/全部，华信，金茂："))
        if random_index == 0:
            with open("./static/json/all_events.json", "w", encoding="utf-8") as f:
                all_events = [all_events_add[index_all]] + all_events
                json.dump(all_events, f, ensure_ascii=False)
                index_all -= 1
        elif random_index == 1:
            with open("./static/json/华信.json", "w", encoding="utf-8") as f:
                huaxin = [huaxin_add[index_huaxin]] + huaxin
                json.dump(huaxin, f, ensure_ascii=False)
                index_huaxin -= 1
        else:
            with open("./static/json/金茂.json", "w", encoding="utf-8") as f:
                jinmao = [jinmao_add[index_jinmao]] + jinmao
                json.dump(jinmao, f, ensure_ascii=False)
                index_jinmao -= 1


if __name__ == '__main__':
    main()
