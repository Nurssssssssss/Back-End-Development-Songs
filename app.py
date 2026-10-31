"""Flask Songs API with optional MongoDB; use MONGO_URI for persistence."""
import json
import os
from pathlib import Path
from flask import Flask, request, jsonify
app=Flask(__name__)
_seed=json.loads((Path(__file__).parent/'backend'/'data'/'songs.json').read_text(encoding='utf8'))
_memory={int(record['id']):dict(record) for record in _seed}
_mongo_collection=None

def collection():
    global _mongo_collection
    uri=os.environ.get('MONGO_URI')
    if not uri and os.environ.get('MONGODB_SERVICE'):
        from urllib.parse import quote_plus
        server=os.environ['MONGODB_SERVICE']
        username=os.environ.get('MONGODB_USERNAME')
        password=os.environ.get('MONGODB_PASSWORD')
        cred=f'{quote_plus(username)}:{quote_plus(password)}@' if username and password else ''
        uri=f'mongodb://{cred}{server}'
    if not uri:return None
    if _mongo_collection is None:
        from pymongo import MongoClient
        client=MongoClient(uri,serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        coll=client[os.environ.get('MONGO_DB','songs')]['songs']
        if os.environ.get('SEED_MONGO','0')=='1' and coll.count_documents({})==0:
            coll.insert_many([dict(item) for item in _seed])
        _mongo_collection=coll
    return _mongo_collection

def all_songs():
    coll=collection()
    if coll is None:return list(_memory.values())
    return list(coll.find({}, {'_id':0}))

def find_song(id):
    coll=collection()
    if coll is None:return _memory.get(id)
    return coll.find_one({'id':id},{'_id':0})

@app.get('/health')
def health():return jsonify(status='OK'),200

@app.get('/count')
def count():return jsonify(count=len(all_songs())),200

@app.get('/song')
def get_songs():return jsonify(songs=all_songs()),200

@app.get('/song/<int:id>')
def get_song(id):
    item=find_song(id)
    return (jsonify(item),200) if item is not None else (jsonify(message=f'song with id {id} not found'),404)

@app.post('/song')
def create_song():
    item=request.get_json(silent=True)
    if not isinstance(item,dict) or not isinstance(item.get('id'),int) or not item.get('title'):
        return jsonify(message='id integer and title required'),400
    if find_song(item['id']) is not None:
        return jsonify(Message=f"song with id {item['id']} already present"),302
    coll=collection()
    if coll is None:_memory[item['id']]=item.copy()
    else:coll.insert_one(item.copy())
    return jsonify(item),201

@app.put('/song/<int:id>')
def update_song(id):
    item=request.get_json(silent=True)
    if not isinstance(item,dict):return jsonify(message='JSON object required'),400
    old=find_song(id)
    if old is None:return jsonify(message='song not found'),404
    updated={**old,**{k:v for k,v in item.items() if k not in ('_id','id')},'id':id}
    if updated==old:return jsonify(message='song found, but nothing updated'),200
    coll=collection()
    if coll is None:_memory[id]=updated
    else:coll.replace_one({'id':id},updated)
    return jsonify(updated),201

@app.delete('/song/<int:id>')
def delete_song(id):
    coll=collection()
    if coll is None:
        deleted=_memory.pop(id,None) is not None
    else:deleted=coll.delete_one({'id':id}).deleted_count>0
    return ('',204) if deleted else (jsonify(message='song not found'),404)

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.getenv('PORT','5000')))
