import json
import pytest
import controllers
from server import app as connexion_app

@pytest.fixture(autouse=True)
def reset_items():
    controllers.items.clear()
    controllers.next_id = 1
    yield

@pytest.fixture
def client():
    with connexion_app.test_client() as c:
        yield c

def test_ping(client):
    resp = client.get('/ping')
    assert resp.status_code == 200
    assert resp.json() == {'message': 'pong'}

def test_create_and_get_item(client):
    resp = client.post('/items', json={'name':'apple','quantity':3,'price':1.2})
    assert resp.status_code == 201
    item = resp.json()
    assert item['id'] == 1
    assert item['name'] == 'apple'
    assert item['quantity'] == 3
    assert item['price'] == 1.2
    resp = client.get('/items/1')
    assert resp.status_code == 200
    assert resp.json() == item

def test_create_invalid_cases(client):
    cases = [
        {},
        {'name':'','quantity':1,'price':1},
        {'name':123,'quantity':1,'price':1},
        {'name':'bad','quantity':'x','price':1},
        {'name':'bad','quantity':-1,'price':1},
        {'name':'bad','quantity':1}
    ]
    for data in cases:
        resp = client.post('/items', json=data)
        assert resp.status_code == 400

def test_list_items_and_search(client):
    client.post('/items', json={'name':'apple','quantity':5,'price':1})
    client.post('/items', json={'name':'banana','quantity':2,'price':0.5})
    resp = client.get('/items')
    assert resp.status_code == 200
    data = resp.json()
    assert 'items' in data
    assert len(data['items']) == 2
    assert data['total'] == 2
    assert data['page'] == 1
    assert data['per_page'] == 10
    assert data['pages'] == 1
    assert data['has_next'] == False
    assert data['has_prev'] == False
    
    resp = client.get('/items?q=app')
    data = resp.json()
    assert len(data['items']) == 1
    assert data['total'] == 1
    
    resp = client.get('/items?q=zzz')
    data = resp.json()
    assert len(data['items']) == 0
    assert data['total'] == 0

def test_low_stock(client):
    client.post('/items', json={'name':'apple','quantity':5,'price':1})
    client.post('/items', json={'name':'banana','quantity':2,'price':1})
    resp = client.get('/items/low-stock?threshold=3')
    assert resp.status_code == 200
    data = resp.json()
    assert 'items' in data
    ids = [item['id'] for item in data['items']]
    assert ids == [2]
    assert data['total'] == 1
    assert data['page'] == 1
    
    resp = client.get('/items/low-stock?threshold=-1')
    assert resp.status_code == 400

def test_update_item(client):
    client.post('/items', json={'name':'apple','quantity':5,'price':1})
    resp = client.put('/items/1', json={'name':'pear','quantity':4,'price':2})
    assert resp.status_code == 200
    item = resp.json()
    assert item['name'] == 'pear'
    assert item['quantity'] == 4
    assert item['price'] == 2
    resp = client.put('/items/1', json={'name':'','quantity':1,'price':1})
    assert resp.status_code == 400
    resp = client.put('/items/999', json={'name':'x','quantity':1,'price':1})
    assert resp.status_code == 404

def test_delete_item(client):
    client.post('/items', json={'name':'apple','quantity':5,'price':1})
    resp = client.delete('/items/1')
    assert resp.status_code == 200
    resp = client.get('/items/1')
    assert resp.status_code == 404
    resp = client.delete('/items/1')
    assert resp.status_code == 404

def test_pagination(client):
    # Create 15 items
    for i in range(15):
        client.post('/items', json={'name':f'item{i}','quantity':i,'price':i*0.5})
    
    # Test default pagination
    resp = client.get('/items')
    data = resp.json()
    assert len(data['items']) == 10
    assert data['total'] == 15
    assert data['page'] == 1
    assert data['per_page'] == 10
    assert data['pages'] == 2
    assert data['has_next'] == True
    assert data['has_prev'] == False
    
    # Test page 2
    resp = client.get('/items?page=2')
    data = resp.json()
    assert len(data['items']) == 5
    assert data['page'] == 2
    assert data['has_next'] == False
    assert data['has_prev'] == True
    
    # Test custom per_page
    resp = client.get('/items?per_page=5')
    data = resp.json()
    assert len(data['items']) == 5
    assert data['pages'] == 3
    
    # Test per_page limit
    resp = client.get('/items?per_page=200')
    data = resp.json()
    assert data['per_page'] == 100  # Should be capped at 100
    
    # Test invalid page (should clamp to valid range)
    resp = client.get('/items?page=100')
    data = resp.json()
    assert data['page'] == 2  # Should be clamped to last page
    
    # Test page 0 (should default to 1)
    resp = client.get('/items?page=0')
    data = resp.json()
    assert data['page'] == 1

def test_pagination_with_search(client):
    # Create items
    for i in range(10):
        client.post('/items', json={'name':f'apple{i}','quantity':i,'price':i*0.5})
    for i in range(5):
        client.post('/items', json={'name':f'banana{i}','quantity':i,'price':i*0.5})
    
    # Search with pagination
    resp = client.get('/items?q=apple&per_page=3')
    data = resp.json()
    assert len(data['items']) == 3
    assert data['total'] == 10
    assert data['pages'] == 4
    assert all('apple' in item['name'] for item in data['items'])

def test_pagination_low_stock(client):
    # Create items with varying quantities
    for i in range(15):
        client.post('/items', json={'name':f'item{i}','quantity':i % 5,'price':i*0.5})
    
    # Test low stock with pagination
    resp = client.get('/items/low-stock?threshold=3&per_page=5')
    data = resp.json()
    assert len(data['items']) == 5
    assert all(item['quantity'] < 3 for item in data['items'])
    assert data['total'] == 9  # items with quantity 0, 1, 2
    assert data['pages'] == 2
