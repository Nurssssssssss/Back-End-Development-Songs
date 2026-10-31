import pytest
from app import app, _memory, _seed

@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv('MONGO_URI',raising=False)
    monkeypatch.delenv('MONGODB_SERVICE',raising=False)
    _memory.clear();_memory.update({int(s['id']):dict(s) for s in _seed})
    app.config['TESTING']=True
    return app.test_client()

def test_health(client):
    assert client.get('/health').json=={'status':'OK'}

def test_count(client):
    assert client.get('/count').json=={'count':20}

def test_list_song(client):
    r=client.get('/song')
    assert r.status_code==200 and len(r.json['songs'])==20

def test_get_song(client):
    assert client.get('/song/1').json['id']==1
    assert client.get('/song/999').status_code==404

def test_create_duplicate_update_delete(client):
    song={'id':323,'title':'New Song','lyrics':'Words'}
    assert client.post('/song',json=song).status_code==201
    assert client.post('/song',json=song).status_code==302
    assert client.put('/song/323',json={'title':'Updated'}).status_code==201
    assert client.get('/song/323').json['title']=='Updated'
    assert client.put('/song/323',json={'title':'Updated'}).status_code==200
    assert client.delete('/song/323').status_code==204
    assert client.delete('/song/323').status_code==404
