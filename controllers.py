from flask import jsonify, request, abort

items = {}
next_id = 1

def ping():
    return jsonify({'message': 'pong'})

def list_items():
    return jsonify(list(items.values()))

def create_item():
    global next_id
    data = request.get_json(force=True)
    if not data or 'name' not in data:
        abort(400)
    item = {'id': next_id, 'name': data['name']}
    items[next_id] = item
    next_id += 1
    return jsonify(item), 201

def get_item(id):
    if id not in items:
        abort(404)
    return jsonify(items[id])

def update_item(id):
    if id not in items:
        abort(404)
    data = request.get_json(force=True)
    if not data or 'name' not in data:
        abort(400)
    items[id]['name'] = data['name']
    return jsonify(items[id])

def delete_item(id):
    if id not in items:
        abort(404)
    deleted = items.pop(id)
    return jsonify(deleted)
