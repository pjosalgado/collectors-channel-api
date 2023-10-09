from flask import Flask, Response
from flask_pymongo import PyMongo
from bson.json_util import dumps
import os
from flask_paginate import get_page_args
from flask import request
import math
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv(os.path.join(os.getcwd(), '.env'))

app = Flask(__name__)
app.config['MONGO_URI'] = os.environ['MONGO_URL']

auth = HTTPBasicAuth()
user_auth = os.environ['AUTH_USER']
password_auth = os.environ['AUTH_PASSWORD']

mongo = PyMongo(app)

SITES_AVAILABLE = [
    'amazon',
    'colecione-classicos',
    'fam-dvd',
    'the-originals',
    'versatil',
    'video-perola'
]
print('SITES_AVAILABLE: <{}>'.format(SITES_AVAILABLE), flush=True)

users_auth = {
    user_auth: generate_password_hash(password_auth)
}


@auth.verify_password
def verify_password(username, password): 
    if username in users_auth and check_password_hash(users_auth.get(username), password):
        return username


@app.route('/movies')
@auth.login_required
def get_all(): 

    key, value = get_filter_parameters()
    sort, direction = get_sort_parameters()
    page, per_page, offset = get_pagination_parameters()
    all_movies = []
    
    for service in SITES_AVAILABLE: 
        service = service.replace('-', '')
        movies = find_in_db(service, key, value, sort, direction)
        all_movies.extend(movies)

    total_size = len(all_movies)
    all_movies, is_last_page = get_data_paginated(all_movies, page, per_page, offset)

    data = []
    
    for item in all_movies: 
        rename_item_id(item)
        data.append(item)

    result = {
        'result': data, 
        'page': page, 
        'size': len(data), 
        'totalPages': math.ceil(total_size / per_page), 
        'totalSize': total_size, 
        'isFirstPage': page == 1, 
        'isLastPage': is_last_page
    }
    
    return Response(dumps(result), mimetype='application/json')


@app.route('/services/<service>/movies')
@auth.login_required
def get_by_service(service): 

    if service not in SITES_AVAILABLE: 
        return site_not_found_response(service)

    service = service.replace('-', '')

    key, value = get_filter_parameters()
    sort, direction = get_sort_parameters()
    page, per_page, offset = get_pagination_parameters()

    movies = find_in_db(service, key, value, sort, direction)
    total_size = len(movies)
    movies, is_last_page = get_data_paginated(movies, page, per_page, offset)
    data = []

    for item in movies: 
        rename_item_id(item)
        data.append(item)
    
    result = {
        'result': data, 
        'page': page, 
        'size': len(data), 
        'totalPages': math.ceil(total_size / per_page), 
        'totalSize': total_size, 
        'isFirstPage': page == 1, 
        'isLastPage': is_last_page
    }
    
    return Response(dumps(result), mimetype='application/json')


@app.route('/status')
def status(): 

    result = {
        'status': 'ok'
    }

    return Response(dumps(result), mimetype='application/json')


def site_not_found_response(service): 
    return Response(dumps({
        'code': 'BAD_REQUEST',
        'message': 'Invalid request',
        'errors': [{
            'message': 'Site {} not found'.format(service)
        }]
    }), mimetype='application/json', status=400)


def get_filter_parameters(): 
    return (request.args.get('key'), request.args.get('value'))


def get_sort_parameters(): 
    return (request.args.get('sort'), request.args.get('direction'))


def get_pagination_parameters(): 
    return get_page_args(page_parameter='page', per_page_parameter='perPage')


def rename_item_id(item): 
    id_item = str(item['_id'])
    del item['_id']
    item.update(id = id_item)


def find_in_db(service, key = None, value = None, sort = None, direction = None): 

    print('find_in_db -> service = {}, key = {}, value = {}, sort = {}, direction = {}'.format(service, key, value, sort, direction), flush=True)

    collection = mongo.db[service]

    if key and value: 
        result = collection.find({key: {'$regex': value, '$options': 'i'}})
    else: 
        result = collection.find()
    
    if sort and direction: 
        direction = int(direction)
        result = result.sort(sort, direction)

    return list(result)


def get_data_paginated(data, page, per_page, offset): 

    data_len = len(data)

    data_paged = data[offset: offset + per_page]
    is_last_page = page * per_page >= data_len

    return data_paged, is_last_page


if __name__ == "__main__": 
    app.run(host='0.0.0.0', port=5000)
