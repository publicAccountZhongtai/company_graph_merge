# coding=utf-8
from py2neo import Graph, Node, Relationship, Subgraph
from xlrd_excel_reading import readexcel


graph = Graph("http://localhost:7474", username="neo4j", password="neo4j123")


def CreateNode(elements):
    nodes = {}

    for key in elements.keys():
        if key not in ['主体代码', '证券代码']:
            nodes[key] = []
            if key == '主体名称':
                for element in elements[key]:
                    nodes[key].append(Node("公司主体", name=element, code=elements['主体代码'][0]))
            elif key == '证券产品':
                for i in range(len(elements[key])):
                    nodes[key].append(Node('属性内容', name=elements['证券产品'][i], code=elements['证券代码'][i], companys=elements['主体名称'][0]))
            elif key == '概念':
                for element in elements[key]:
                    nodes[key].append(Node('公司属性', name=element, companys=elements['主体名称'][0]))
            else:
                for element in elements[key]:
                    nodes[key].append(Node('属性内容', name=element, companys=elements['主体名称'][0]))

    for node in nodes.values():
        graph.create(Subgraph(node))

    return nodes

def CreateRelationship(elements, nodes):
    rels = {}

    for key in nodes.keys():
        if key != '主体名称':
            rels[key] = []
            if key in elements['概念']:
                for node in nodes[key]:
                    rels[key].append(Relationship(node, '属于', nodes['概念'][elements['概念'].index(key)], relation='属于'))
            elif key == '概念':
                for node in nodes[key]:
                    rels[key].append(Relationship(node, '属于', nodes['主体名称'][0], relation='属于'))

    for rels in rels.values():
        graph.create(Subgraph(relationships=rels))