from py2neo import Graph, Node, Relationship, Subgraph, walk, NodeMatcher, RelationshipMatcher
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from datetime import timedelta
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
import json
import os
# 国玮代码片段
from flask import Flask, render_template
from py2neo_nandr_export import writefile1, writefile2
from py2neo import Graph

from flask import Flask, render_template, request, jsonify
import json
import random
import time
import datetime
import pymysql

with open("static/json/all_events.json", "r", encoding="utf-8") as f:
    all_events = json.load(f)
with open("static/json/华信.json", "r", encoding="utf-8") as f:
    huaxin_events = json.load(f)
with open("static/json/金茂.json", "r", encoding="utf-8") as f:
    jinmao_events = json.load(f)
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

graph = Graph("http://localhost:7474", username="neo4j", password="neo4j123")
app.send_file_max_age_default = timedelta(seconds=1)

# 主界面密码系统
addcode = "add"
searchcode = "search"
deletecode = "delete"
changecode = "change"


# 国玮代码片段


# 定义OGM的类
class name(GraphObject):
    __primarykey__ = "name"

    name = Property()
    belonging = Property()
    id = Property()
    height = Property()
    age = Property()

    manager = RelatedTo("Company", "经营")
    belongs = RelatedTo("Position", "属于")
    own = RelatedTo("Company", "拥有")
    investigate = RelatedTo("Company", "投资")
    connect = RelatedTo("Company", "关联")
    shareholder = RelatedTo("Company", "股东")
    member = RelatedTo("Company", "成员")


class Position(GraphObject):
    __primarykey__ = "name"

    name = Property()
    belonging = Property()
    code = Property()

    manager = RelatedTo("Shareholder", "经营")
    belongs = RelatedTo("Position", "属于")
    own = RelatedTo("Shareholder", "拥有")
    investigate = RelatedTo("Shareholder", "投资")
    connect = RelatedTo("Shareholder", "关联")
    shareholder = RelatedTo("Shareholder", "股东")
    member = RelatedTo("Shareholder", "成员")


writefile1()

companys = []
for item in graph.run('MATCH (n:主体名称) RETURN n').data():
    company = item.get('n').get('name')
    writefile2(company)
    companys.append(company)


@app.route('/企业关联信息展示', methods=['GET', 'POST'])
def index1():
    return render_template('企业关联信息展示.html')


@app.route('/企业信息展示', methods=['GET', 'POST'])
def index2():
    return render_template('企业信息展示.html', companys=companys)


# 增加系统flask框架
@app.route('/add', methods=['POST', 'GET'])  # 添加路由
def add():
    if request.method == 'POST':

        # rechoose = request.form.get("choose")
        # if len(rechoose) > 0:
        # return redirect("http://0.0.0.0:8091/")

        graph = Graph('http://localhost:7474', username='sgw', password='kk50591388')

        user_input1 = request.form.get("company")
        user_input2 = request.form.get("position")
        user_input3 = request.form.get("name")
        user_input4 = request.form.get("company1")
        user_input5 = request.form.get("position1")

        if len(user_input1) > 0:
            matcher = NodeMatcher(graph)
            # node1 = matcher.match("Company", name=user_input1).first()
            node2 = matcher.match("Position", name=user_input2, company=user_input1).first()
            # node1 = Node("Company", name=user_input1)
            # node2 = Node("Position", name=user_input2)
            node3 = Node("name", name=user_input3)

            relationship1 = Relationship(node3, "属于", node2)

            total_add1 = node3 | relationship1
            graph.create(total_add1)

        elif len(user_input4) > 0:
            matcher = NodeMatcher(graph)
            node4 = matcher.match("Company", name=user_input4).first()
            node5 = Node("Position", name=user_input5, company=user_input4)
            relationship2 = Relationship(node5, "属于", node4)
            total_add2 = node5 | relationship2
            graph.create(total_add2)

    return render_template('add.html')


'''
        user_input1 = request.form.get("label")
        user_input2 = request.form.get("name")
        user_input3 = request.form.get("height")


        user_input4 = request.form.get("new_caption")
        user_input5 = request.form.get("description")

        user_input6 = request.form.get("f_nodename")
        user_input7 = request.form.get("b_nodename")
        user_input8 = request.form.get("new_rel")

        matcher = NodeMatcher(graph)
        x1 = matcher.match("Shareholder", name=user_input6).first()
        x2 = matcher.match("Company", name=user_input7).first()

        #对于新增节点该是新增属性的判定
        if len(user_input4) > 0:
            a = Node(user_input1, name=user_input2, height=user_input3)
            a[user_input4] = user_input5
            graph.create(a)
        if len(user_input6) > 0:
            relationship = Relationship(x1, user_input8, x2)
            graph.create(relationship)
        if (len(user_input4)==0)&(len(user_input6)==0):
            a = Node(user_input1, name=user_input2, height=user_input3)
            graph.create(a)

'''


# 搜索系统flask框架
@app.route('/search', methods=['POST', 'GET'])
def search():
    # 完善一下的话，html的地方写个循环
    if request.method == 'POST':
        information = request.form.get("information")
        graph = Graph('http://localhost:7474', username='sgw', password='kk50591388')

        matcher = NodeMatcher(graph)
        nodelist = list(matcher.match())

        numlist1 = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']
        numlist2 = ['one', 'two', 'three', 'four']

        nodedict = dict(zip(numlist1, nodelist))

        relmatch = RelationshipMatcher(graph)
        relist = list(relmatch.match())
        reldict = dict(zip(numlist2, relist))

        # nodedict1 = json.dumps(nodedict, encoding='UTF-8', ensure_ascii=False)
        # reldict1 = json.dumps(reldict, encoding='UTF-8', ensure_ascii=False)

        return render_template('index.html', **nodedict, **reldict)

    return render_template('search.html')


# 删除系统flask框架
@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':

        graph = Graph('http://localhost:7474', username='sgw', password='kk50591388')

        user_delete = request.form.get("delete_name")  # 需要删除的单节点的反馈节点

        user_delnode = name.match(graph, user_delete).first()

        if len(user_delete) > 0:
            graph.delete(user_delnode)

        '''
        if len(user_del1) > 0:
            if user_del3 == "股东":
                user_delnode1.shareholder.remove(user_delnode2)
                graph.push(user_delnode1)

            if user_del3 == "经营":
                user_delnode.manager.remove(user_delnode2)
                graph.push(user_delnode1)
        '''
    return render_template('delete.html')


# 修改系统flask框架
@app.route('/change', methods=['POST', 'GET'])
def change():
    if request.method == 'POST':
        graph = Graph('http://localhost:7474', username='sgw', password='kk50591388')

        user_change1 = request.form.get("change_company")
        user_change2 = request.form.get("change_position")
        user_change3 = request.form.get("change_name")
        user_change4 = request.form.get("new_name")

        # user_changeposition = Position.match(graph, user_change2).first()

        # user_changenode1 = Shareholder.match(graph, user_changerel1).first()
        # user_changenode2 = Company.match(graph, user_changerel2).first()

        matcher = NodeMatcher(graph)
        company_node = matcher.match("Company", name=user_change1).first()

        position_node = matcher.match("Position", name=user_change2, company=user_change1).first()
        name_node = matcher.match("name", name=user_change3).first()

        graph.delete(name_node)

        new_node = Node("name", name=user_change4)

        new_rel = Relationship(new_node, "属于", position_node)

        total_change = new_rel | new_node
        graph.create(total_change)

        '''
        # 单节点对应属性修改
        if len(user_change1) > 0:

            if user_change2 == "height":
                user_changenode.height = user_change3
            if user_change2 == "age":
                user_changenode.age = user_change3

            graph.push(user_changenode)

        # 节点关系修改
        if len(user_changerel1) > 0:
            if user_changerel3 == "经营":
                user_changenode1.manager.remove(user_changenode2)
                graph.push(user_changenode1)
                relationship = Relationship(x1, user_changerel4, x2)
                graph.create(relationship)

            if user_changerel3 == "股东":
                user_changenode1.shareholder.remove(user_changenode2)
                graph.push(user_changenode1)
                relationship = Relationship(x1, user_changerel4, x2)
                graph.create(relationship)
        '''

    return render_template('change.html')


@app.route('/getJsonData/<string:company>', methods=['GET', 'POST'])
def get_json_data(company):
    if company == "all":
        with open("./static/json/all_events.json", "r", encoding="utf-8") as f:
            all_result = json.load(f)
        relateCompany = request.args['relateCompany']
    else:
        with open("./static/json/{}.json".format(company), "r", encoding="utf-8") as f:
            all_result = json.load(f)
        relateCompany = ""
    riskType = request.args['riskType']
    riskLevel = request.args['riskLevel']
    startTime = request.args['startTime']
    endTime = request.args['endTime']
    if startTime == "":
        startTimeStamp = 0
    else:
        startTimeStamp = int(time.mktime(time.strptime(startTime + " 00:00:00", "%Y-%m-%d %H:%M:%S")))
    if endTime == "":
        endTimeStamp = int(time.time())
    else:
        endTimeStamp = int(time.mktime(time.strptime(endTime + " 23:59:59", "%Y-%m-%d %H:%M:%S")))

    result = []
    for r in all_result:
        news_date = int(time.mktime(time.strptime(r['date'], "%Y-%m-%d")))
        if relateCompany == "" or r['relateCompany'] == relateCompany:
            if riskType == "" or r['riskType'] == riskType:
                if riskLevel == "" or r['riskLevel'] == riskLevel:
                    if endTimeStamp >= news_date >= startTimeStamp:
                        result.append(r)

    return jsonify(result)


size_of_all_event = os.path.getsize("./static/json/all_events.json")
size_of_huaxin = os.path.getsize("./static/json/华信.json")
size_of_jinmao = os.path.getsize("./static/json/金茂.json")


@app.route('/ListenDataChange/<string:company>', methods=['GET', 'POST'])
def ListenDataChange(company):
    global size_of_all_event, size_of_huaxin, size_of_jinmao
    if company == "all":
        temp = os.path.getsize("./static/json/all_events.json")
        isUpdate = (size_of_all_event != temp)
        size_of_all_event = temp
    elif company == "华信":
        temp = os.path.getsize("./static/json/华信.json")
        isUpdate = (size_of_huaxin != temp)
        size_of_huaxin = temp
    elif company == "金茂":
        temp = os.path.getsize("./static/json/金茂.json")
        isUpdate = (size_of_jinmao != temp)
        size_of_jinmao = temp
    else:
        isUpdate = False
    return jsonify({"isUpdate": isUpdate})


# @app.route('/updateNewsData', methods=['GET', 'POST'])
# def update_news_data():
#     re_data = random.choice(all_events)
#     re_data["riskType"] = random.choice(riskType)
#     re_data["riskLevel"] = random.choice(riskLevel)
#     re_data["relateCompany"] = random.choice(relateCompanys)
#     return jsonify(re_data)


@app.route('/updateSingleCompanyNewsData/<string:company>', methods=['GET', 'POST'])
def update_single_company_news_data(company):
    """失效"""
    if company == "华信":
        re_data = random.choice(huaxin_events)
    elif company == "金茂":
        re_data = random.choice(jinmao_events)
    else:
        re_data = random.choice(all_events)
    # re_data["riskType"] = random.choice(riskType)
    # re_data["riskLevel"] = random.choice(riskLevel)
    return jsonify(re_data)


@app.route('/updateBarData/<string:company>/<string:barMonth>', methods=['GET', 'POST'])
def update_bar_data(company, barMonth):
    if barMonth == "init":
        current_month = time.strftime('%Y-%m', time.localtime(time.time()))
    else:
        current_month = barMonth
    with open("static/json/{}.json".format(company), "r", encoding="utf-8") as f:
        events = json.load(f)
    is_current_date = True
    data0 = [0 for _ in range(31)]
    data1 = [0 for _ in range(31)]
    data2 = [0 for _ in range(31)]
    risk_type_weight0 = {
        "经营": 2,
        "信用": 3,
        "法律": 2,
        "高管": 1,
        "子公司": 1,
        "市场": 3,

    }
    risk_type_weight1 = {
        "经营": 4,
        "信用": 1,
        "法律": 5,
        "高管": 2,
        "子公司": 6,
        "市场": 3,

    }
    risk_type_weight2 = {
        "经营": 2,
        "信用": 6,
        "法律": 2,
        "高管": 4,
        "子公司": 2,
        "市场": 3,

    }
    for event in events:
        if event['date'][0:7] == current_month:
            data0[int(event['date'][7:-1]) - 1] += risk_type_weight0[event['riskType']]
            data1[int(event['date'][7:-1]) - 1] += risk_type_weight1[event['riskType']]
            data2[int(event['date'][7:-1]) - 1] += risk_type_weight2[event['riskType']]
            is_current_date = False
        elif is_current_date:
            continue
        else:
            break
    return jsonify({'data0': data0, 'data1': data1, 'data2': data2})


@app.route('/updateRadioData/<string:company>/<string:radioDate>', methods=['GET', 'POST'])
def update_radio_data(company, radioDate):
    # data = json.loads(request.form.get('data'))
    # for i in range(len(data['radio_data'])):
    #     if data['radio_data'][i] < 100:
    #         data['radio_data'][i] += random.randint(1, 3)
    if radioDate == "init":
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    else:
        current_date = radioDate
    with open("static/json/{}.json".format(company), "r", encoding="utf-8") as f:
        events = json.load(f)
    is_current_date = True
    data = [0 for _ in range(6)]
    risk_type_index = {
        "经营": 0,
        "信用": 1,
        "市场": 2,
        "法律": 3,
        "高管": 4,
        "子公司": 5,
    }
    for event in events:
        if event['date'] == current_date:
            data[risk_type_index[event['riskType']]] += 1
            is_current_date = False
        elif is_current_date:
            continue
        else:
            break
    return jsonify({"radio_data": data})


@app.route('/updateGaugeData/<string:company>/<string:gaugeDate>', methods=['GET', 'POST'])
def update_gauge_data(company, gaugeDate):
    # data = json.loads(request.form.get('data'))
    # if random.random() > 0.5 and data['gaugeNum'] < 100:
    #     data['gaugeNum'] += 1
    # current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    if gaugeDate == "init":
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    else:
        current_date = gaugeDate
    gaugeNum = 0
    risk_type_weight = {
        "经营": 2,
        "信用": 3,
        "法律": 2,
        "高管": 1,
        "子公司": 1,
        "市场": 3,

    }
    with open("static/json/{}.json".format(company), "r", encoding="utf-8") as f:
        events = json.load(f)
    is_current_date = True
    for event in events:
        if event['date'] == current_date:
            gaugeNum += risk_type_weight[event['riskType']]
            is_current_date = False
        elif is_current_date:
            continue
        else:
            break
    return jsonify({"gaugeNum": gaugeNum})


@app.route('/index/<string:user>', methods=['GET', 'POST'])
def index(user, name="index"):
    return render_template("index.html", name=name, user=user)


@app.route('/register', methods=['GET', 'POST'])
def register(name="register"):
    return render_template("register.html", name=name)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login(name="login"):
    return render_template("login.html", name=name)


@app.route('/single_company/<string:company>', methods=['GET', 'POST'])
def single_company(company, name="single_company"):
    return render_template("single_company.html", name=name, company=company)


connect = pymysql.Connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='sgxsgwbd',
    db='useraccount',
    charset='utf8'
)


@app.route('/checkUser', methods=['POST'])
def check_user():
    data = json.loads(request.form.get('data'))
    cursor = connect.cursor()
    sql = "select * from users WHERE username ='%s'" % data['user']
    cursor.execute(sql)
    if cursor.rowcount > 0:
        cursor.close()
        return jsonify({'valid': False})

    else:
        cursor.close()
        return jsonify({'valid': True})


@app.route('/reg', methods=['POST'])
def reg():
    data = json.loads(request.form.get('data'))
    cursor = connect.cursor()
    sql = "insert into users values (null,'%s','%s','%s')" % (data['user'], data['pwd'], data['user'] + "的账号");
    result = cursor.execute(sql)
    connect.commit()
    if result:
        return jsonify({'isRegister': True})
    else:
        return jsonify({'isRegister': False})


@app.route('/checkLogin', methods=['POST'])
def check_login():
    data = json.loads(request.form.get('data'))
    cursor = connect.cursor()
    sql = "select * from users where username='%s' and password='%s'" % (data['user'], data['pwd'])
    cursor.execute(sql)
    if cursor.rowcount:
        return jsonify({'isLogin': True})
    else:
        return jsonify({'isLogin': False})


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1")
