from flask import jsonify, request, abort

items = {}
next_id = 1

def ping():
    return jsonify({'message': 'pong'})

def list_items():
    q = request.args.get('q')
    results = list(items.values())
    if q:
        q_lower = q.lower()
        results = [item for item in results if q_lower in item['name'].lower()]
    return jsonify(results)

def create_item():
    """Create a new item with a non-empty string name, integer quantity and numeric price."""
    global next_id
    data = request.get_json(force=True)
    name = data.get('name') if isinstance(data, dict) else None
    quantity = data.get('quantity') if isinstance(data, dict) else None
    price = data.get('price') if isinstance(data, dict) else None
    if not isinstance(name, str) or not name.strip():
        abort(400)
    if not isinstance(quantity, int) or quantity < 0:
        abort(400)
    if not (isinstance(price, int) or isinstance(price, float)) or price < 0:
        abort(400)
    item = {'id': next_id, 'name': name, 'quantity': quantity, 'price': price}
    items[next_id] = item
    next_id += 1
    return jsonify(item), 201

def get_item(id):
    if id not in items:
        abort(404)
    return jsonify(items[id])

def update_item(id):
    """Update an existing item's name, quantity and price."""
    if id not in items:
        abort(404)
    data = request.get_json(force=True)
    name = data.get('name') if isinstance(data, dict) else None
    quantity = data.get('quantity') if isinstance(data, dict) else None
    price = data.get('price') if isinstance(data, dict) else None
    if not isinstance(name, str) or not name.strip():
        abort(400)
    if not isinstance(quantity, int) or quantity < 0:
        abort(400)
    if not (isinstance(price, int) or isinstance(price, float)) or price < 0:
        abort(400)
    items[id]['name'] = name
    items[id]['quantity'] = quantity
    items[id]['price'] = price
    return jsonify(items[id])

def delete_item(id):
    if id not in items:
        abort(404)
    deleted = items.pop(id)
    return jsonify(deleted)

def low_stock():
    """List items with quantity below the given threshold."""
    threshold = request.args.get('threshold', type=int)
    if threshold is None or threshold < 0:
        abort(400)
    results = [item for item in items.values() if item['quantity'] < threshold]
    return jsonify(results)
