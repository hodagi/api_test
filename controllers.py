from flask import jsonify, request, abort

import database

def ping():
    return jsonify({'message': 'pong'})

def list_items():
    return jsonify(database.list_items())

def create_item():
    """Create a new item with a non-empty string name."""
    data = request.get_json(force=True)
    name = data.get("name") if isinstance(data, dict) else None
    if not isinstance(name, str) or not name.strip():
        abort(400)
    item = database.create_item(name)
    return jsonify(item), 201

def get_item(id):
    item = database.get_item(id)
    if item is None:
        abort(404)
    return jsonify(item)

def update_item(id):
    """Update an existing item's name."""
    data = request.get_json(force=True)
    name = data.get("name") if isinstance(data, dict) else None
    if not isinstance(name, str) or not name.strip():
        abort(400)
    item = database.update_item(id, name)
    if item is None:
        abort(404)
    return jsonify(item)

def delete_item(id):
    deleted = database.delete_item(id)
    if deleted is None:
        abort(404)
    return jsonify(deleted)
