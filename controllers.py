from flask import jsonify, request, abort

items = {}
next_id = 1

def ping():
    return jsonify({'message': 'pong'})

def list_items():
    return jsonify(list(items.values()))

def create_item():
    """Create a new item with a non-empty string name."""
    global next_id
    data = request.get_json(force=True)
    name = data.get('name') if isinstance(data, dict) else None
    if not isinstance(name, str) or not name.strip():
        abort(400)
    item = {'id': next_id, 'name': name}
    items[next_id] = item
    next_id += 1
    return jsonify(item), 201

def get_item(id):
    if id not in items:
        abort(404)
    return jsonify(items[id])

def update_item(id):
    """Update an existing item's name."""
    if id not in items:
        abort(404)
    data = request.get_json(force=True)
    name = data.get('name') if isinstance(data, dict) else None
    if not isinstance(name, str) or not name.strip():
        abort(400)
    items[id]['name'] = name
    return jsonify(items[id])

def delete_item(id):
    if id not in items:
        abort(404)
    deleted = items.pop(id)
    return jsonify(deleted)
