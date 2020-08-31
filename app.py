from py2neo import Graph, Node, Relationship, Subgraph, walk, NodeMatcher, RelationshipMatcher
from datetime import timedelta
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
import os
from py2neo_nandr_export import writefile1, writefile2
from py2neo import Graph

from flask import Flask, render_template, request, jsonify
import json
import time
import pymysql

with open("static/json/all_events.json", "r", encoding="utf-8") as f:
    all_events = json.load(f)
with open("static/json/华信.json", "r", encoding="utf-8") as f:
    hua_xin_events = json.load(f)
with open("static/json/金茂.json", "r", encoding="utf-8") as f:
    jin_mao_events = json.load(f)
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

graph = Graph("http://localhost:7474", username="neo4j", password="neo4j123")
app.send_file_max_age_default = timedelta(seconds=1)


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


# 从图谱中提取主体名称写入  所有公司.json
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

        # graph = Graph('http://localhost:7474', username='sgw', password='kk50591388')

        user_input1 = request.form.get("company")
        user_input2 = request.form.get("position")
        user_input3 = request.form.get("name")
        user_input4 = request.form.get("company1")
        user_input5 = request.form.get("position1")

        if len(user_input1) > 0:
            matcher = NodeMatcher(graph)
            node2 = matcher.match("Position", name=user_input2, company=user_input1).first()
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


# 搜索系统flask框架
@app.route('/search', methods=['POST', 'GET'])
def search():
    # 完善一下的话，html的地方写个循环
    if request.method == 'POST':
        information = request.form.get("information")
        # graph = Graph('http://localhost:7474', username='sgw', password='kk50591388')

        matcher = NodeMatcher(graph)
        nodelist = list(matcher.match())

        numlist1 = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']
        numlist2 = ['one', 'two', 'three', 'four']

        nodedict = dict(zip(numlist1, nodelist))

        relmatch = RelationshipMatcher(graph)
        relist = list(relmatch.match())
        reldict = dict(zip(numlist2, relist))

        return render_template('index.html', **nodedict, **reldict)

    return render_template('search.html')


# 删除系统flask框架
@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        # graph = Graph('http://localhost:7474', username='sgw', password='kk50591388')
        user_delete = request.form.get("delete_name")  # 需要删除的单节点的反馈节点
        user_delnode = name.match(graph, user_delete).first()

        if len(user_delete) > 0:
            graph.delete(user_delnode)
    return render_template('delete.html')


# 修改系统flask框架
@app.route('/change', methods=['POST', 'GET'])
def change():
    if request.method == 'POST':
        # graph = Graph('http://localhost:7474', username='sgw', password='kk50591388')

        user_change1 = request.form.get("change_company")
        user_change2 = request.form.get("change_position")
        user_change3 = request.form.get("change_name")
        user_change4 = request.form.get("new_name")

        matcher = NodeMatcher(graph)
        company_node = matcher.match("Company", name=user_change1).first()

        position_node = matcher.match("Position", name=user_change2, company=user_change1).first()
        name_node = matcher.match("name", name=user_change3).first()

        graph.delete(name_node)

        new_node = Node("name", name=user_change4)

        new_rel = Relationship(new_node, "属于", position_node)

        total_change = new_rel | new_node
        graph.create(total_change)
    return render_template('change.html')


# 获取以及筛选新闻展示页新闻内容
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


# 判断是否有增加新闻，判断依据为存储新闻的文件大小改变
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


# 更新以及筛选柱状图数据信息
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


# 更新及筛选雷达图信息
@app.route('/updateRadioData/<string:company>/<string:radioDate>', methods=['GET', 'POST'])
def update_radio_data(company, radioDate):
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


# 更新及筛选仪表盘数据信息
@app.route('/updateGaugeData/<string:company>/<string:gaugeDate>', methods=['GET', 'POST'])
def update_gauge_data(company, gaugeDate):
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


# 全部新闻展示页面
@app.route('/index', methods=['GET', 'POST'])
def index(name="index"):
    return render_template("index.html", name=name, company="全部")


# 侧边导航栏公关模板
@app.route('/side', methods=['GET', 'POST'])
def side():
    return render_template('side.html')


# 底部公关模板
@app.route('/footer', methods=['GET', 'POST'])
def footer():
    return render_template('footer.html')


# 用户注册页面
@app.route('/register', methods=['GET', 'POST'])
def register(name="register"):
    return render_template("register.html", name=name)


# 用户登陆界面
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login(name="login"):
    return render_template("login.html", name=name)


# 单独企业展示界面
@app.route('/companys/<string:company>', methods=['GET', 'POST'])
def single_company(company, name="companys"):
    return render_template("company.html", name=name, company=company)

    # 用户信息存储mysql数据库


connect = pymysql.Connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='sgxsgwbd',
    db='useraccount',
    charset='utf8'
)


# 判断注册用户名是否重名
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


# 判断注册是否成功
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


# 判断登陆是否成功
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
