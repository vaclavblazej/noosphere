#!/usr/bin/env python3

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

import gr
import gr_data
import gr_types

# == Main ========================================================================


# curl -X GET http://127.0.0.1:5000/graph/clear/
@app.route('/graph/clear/', methods = ['POST'])
def clear():
    graph = gr.Graph(gr_data.FileDB('web.json'))
    graph.clear()
    gr_types.init_type_system(graph)
    return '', 200

# curl -X GET http://127.0.0.1:5000/node/find/ -H "Content-Type: application/json" --data '{"query": "lambda x:True"}'
@app.route('/node/find/', methods = ['GET'])
def find():
    graph = gr.Graph(gr_data.FileDB('web.json'))
    body = request.get_json()
    query_lambda = eval(body['query'])
    res = graph.find(query_lambda)
    print(res)
    return str(res) + '\n', 200

# curl -X GET http://127.0.0.1:5000/node/101/
@app.route('/node/<int:entity_id>/', methods = ['GET'])
def get(entity_id):
    graph = gr.Graph(gr_data.FileDB('web.json'))
    return graph.get(entity_id), 200

@app.route('/node/', methods = ['POST', 'PUT'])
def update_insert():
# curl -X POST http://127.0.0.1:5000/node/ -H "Content-Type: application/json" --data '{"asdf": 111}'
    if request.method == 'POST':
        body = request.get_json()
        graph = gr.Graph(gr_data.FileDB('web.json'))
        graph.insert(body)
# curl -X PUT http://127.0.0.1:5000/node/ -H "Content-Type: application/json" --data '{"id": 113, "test": "hello world"}'
    elif request.method == 'PUT':
        body = request.get_json()
        graph = gr.Graph(gr_data.FileDB('web.json'))
        graph.update(body)
    return '', 200

# == Main Initialization =========================================================

if __name__ == '__main__':
    app.run(debug = True)

#  https://towardsdatascience.com/the-right-way-to-build-an-api-with-python-cd08ab285f8f