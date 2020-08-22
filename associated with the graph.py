# coding=utf-8
from py2neo import Graph
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
graph = Graph("http://localhost:7474", username="neo4j", password="neo4j123")


def buildNodes(nodeRecord):
    name = nodeRecord.get('name')
    return name


def Get_associated_content(keyword):
    x = 'where n.name =' + "'" + keyword + "'"
    y = graph.run("match (n)-[*2..3]->(m) "
                  + x +
                  "return m")
    z = []
    for a in y.data():
        z.append(list(map(buildNodes, a.values()))[0])
    return z


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('获取关联内容.html')

@app.route('/show', methods=['POST'])
def do_show():
    keyword = request.values.get("text")
    Get_associated_content(keyword)
    return render_template('关联内容.html', associated_content=Get_associated_content(keyword))

if __name__ == '__main__':
    app.run(debug=True)