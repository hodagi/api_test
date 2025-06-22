from flask import jsonify, request, abort
import math

items = {}
next_id = 1

def paginate_results(results, page=1, per_page=10):
    """Paginate a list of results."""
    total = len(results)
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    # Ensure page is within valid range
    page = max(1, min(page, pages))
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': results[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': pages,
        'has_next': page < pages,
        'has_prev': page > 1
    }

def ping():
    return jsonify({'message': 'pong'})

def list_items():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate pagination parameters
    page = max(1, page)
    per_page = max(1, min(per_page, 100))  # Limit to 100 items per page
    
    results = list(items.values())
    if q:
        q_lower = q.lower()
        results = [item for item in results if q_lower in item['name'].lower()]
    
    return jsonify(paginate_results(results, page, per_page))

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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if threshold is None or threshold < 0:
        abort(400)
    
    # Validate pagination parameters
    page = max(1, page)
    per_page = max(1, min(per_page, 100))  # Limit to 100 items per page
    
    results = [item for item in items.values() if item['quantity'] < threshold]
    return jsonify(paginate_results(results, page, per_page))
