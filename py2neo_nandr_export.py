# coding=utf-8
from py2neo import Graph
import json


graph = Graph("http://localhost:7474", username="neo4j", password="neo4j123")


def buildallNodes(nodeRecord):
    for item in nodeRecord.values():
        id = item.identity
        data = {"name": str(nodeRecord.get('n').get('name')),
                "id": str(id)}
        return data

def buildallEdges(relationRecord):
    for item in relationRecord.values():
        start_id = item.start_node.identity
        relation = item.get('relation')
        end_id = item.end_node.identity
        data = {"source": str(start_id),
                "name": str(relation),
                "target": str(end_id)}
        return data

def writefile1():
    allnodes = graph.run('MATCH (n) RETURN n')
    allrelations = graph.run('MATCH ()-[r]->() RETURN r')
    nodes = list(map(buildallNodes, allnodes.data()))
    edges = list(map(buildallEdges, allrelations.data()))
    jsonData = json.dumps({'data': nodes, 'links': edges}, ensure_ascii=False)
    fileObject = open('static/data/jsondata/所有公司.json', 'w', encoding='utf-8')
    fileObject.write(jsonData)
    fileObject.close()


def buildNodes(nodeRecord):
    id = nodeRecord.identity
    name = nodeRecord.get('name')
    data = {"name": str(name),
            "id": str(id)}
    return data

def buildEdges(relationRecord):
    start_id = relationRecord.start_node.identity
    relation = relationRecord.get('relation')
    end_id = relationRecord.end_node.identity
    data = {"source": str(start_id),
            "name": str(relation),
            "target": str(end_id)}
    return data

def writefile2(company):
    x = 'match (na:主体名称)-[re1]-(nb) where na.name=' + "'" + company + "'"
    y = graph.run(x +
              "with na,re1,nb match (nb)-[re2]-(nc) "
              "with apoc.coll.union(collect(na),collect(nb)) as one,collect(nc) as two "
              "return apoc.coll.union(one,two) as n")
    z = graph.run(x +
              "with na,re1,nb match(nb)-[re2]-(nc) "
              "return apoc.coll.union(collect(re1),collect(re2)) as r")
    for a in y.data()[0].values():
        nodes = list(map(buildNodes, a))
    for b in z.data()[0].values():
        edges = list(map(buildEdges, b))
    jsonData = json.dumps({'data': nodes, 'links': edges}, ensure_ascii=False)
    filepath = 'static/data/jsondata/' + company + '.json'
    fileObject = open(filepath, 'w', encoding='utf-8')
    fileObject.write(jsonData)
    fileObject.close()