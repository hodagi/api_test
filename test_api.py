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
    assert len(resp.json()) == 2
    resp = client.get('/items?q=app')
    assert len(resp.json()) == 1
    resp = client.get('/items?q=zzz')
    assert len(resp.json()) == 0

def test_low_stock(client):
    client.post('/items', json={'name':'apple','quantity':5,'price':1})
    client.post('/items', json={'name':'banana','quantity':2,'price':1})
    resp = client.get('/items/low-stock?threshold=3')
    assert resp.status_code == 200
    ids = [item['id'] for item in resp.json()]
    assert ids == [2]
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
