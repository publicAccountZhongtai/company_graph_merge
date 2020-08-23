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
    while True:
        random_index = random.randint(0, 2)
        if random_index == 0:
            with open("./static/json/all_events.json", "w", encoding="utf-8") as f:
                all_events = [random.choice(all_events)] + all_events
                json.dump(all_events, f, ensure_ascii=False)
        elif random_index == 1:
            with open("./static/json/华信.json", "w", encoding="utf-8") as f:
                huaxin = [random.choice(huaxin)] + huaxin
                json.dump(huaxin, f, ensure_ascii=False)
        else:
            with open("./static/json/金茂.json", "w", encoding="utf-8") as f:
                jinmao = [random.choice(jinmao)] + jinmao
                json.dump(jinmao, f, ensure_ascii=False)
        time.sleep(3)


if __name__ == '__main__':
    main()
