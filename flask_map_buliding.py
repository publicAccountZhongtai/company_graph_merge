# coding=utf-8
from py2neo import Graph
from xlrd_excel_reading import readexcel
from flask import Flask, request, render_template, redirect
from py2neo_nandr_creation import CreateNode,CreateRelationship
import os


app = Flask(__name__)
graph = Graph("http://localhost:7474", username="neo4j", password="neo4j123")


@app.route('/', methods=['GET'])
def index():
    return render_template('HTML上传文件到Python.html')

@app.route('/upload', methods=['POST'])
def do_upload():
    upload_file = request.files.get('file')
    file_path = "static/data/exceldata"

    if upload_file:
        file_name = os.path.join(file_path, upload_file.filename)
        try:
            upload_file.save(file_name)
            elements = readexcel(file_name)
            nodes = CreateNode(elements)
            CreateRelationship(elements, nodes)
            graph.run("match (n) where any(label in labels(n) WHERE label <> '概念') "
                        "WITH n.name as name, COLLECT(n) as nodelist, COUNT(*) as count "
                        "WHERE count > 1 "
                        "CALL apoc.refactor.mergeNodes(nodelist) YIELD node "
                        "RETURN node")
        except IOError:
            return '上传文件失败'
        else:
            return redirect('/')
    else:
        return '上传文件失败'


if __name__ == '__main__':
    app.run(debug=True)