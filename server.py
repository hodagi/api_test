from flask import Flask, jsonify, request, abort

app = Flask(__name__)

items = {}
next_id = 1

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'})

@app.route('/items', methods=['GET', 'POST'])
def items_route():
    global next_id
    if request.method == 'GET':
        return jsonify(list(items.values()))
    elif request.method == 'POST':
        data = request.get_json(force=True)
        if not data or 'name' not in data:
            abort(400)
        item = {'id': next_id, 'name': data['name']}
        items[next_id] = item
        next_id += 1
        return jsonify(item), 201

@app.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
def item_route(item_id):
    if item_id not in items:
        abort(404)
    if request.method == 'GET':
        return jsonify(items[item_id])
    elif request.method == 'PUT':
        data = request.get_json(force=True)
        if not data or 'name' not in data:
            abort(400)
        items[item_id]['name'] = data['name']
        return jsonify(items[item_id])
    elif request.method == 'DELETE':
        deleted = items.pop(item_id)
        return jsonify(deleted)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
