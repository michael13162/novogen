from flask import Flask, render_template, request, json, redirect
from pymongo import MongoClient
from model.gen import gen
import random
import base64
import cStringIO
from elasticsearch import Elasticsearch
from urllib import unquote

es = Elasticsearch()
app = Flask(__name__)


class safe:
    def set(self, values):
        self.values = values
        return

my_safe = safe()


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/home')
def home():
    print(my_safe.values)
    return render_template('home.html', projects=my_safe.values['json'])

@app.route('/upload')
def uploadFile():
    return render_template('upload.html')


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

uri = 'mongodb://user:pass@ds123658.mlab.com:23658/novogen'


def mongo_users():
    client = MongoClient(uri)
    db = client['novogen']
    users = db['users']
    return users


def mongo_projects():
    client = MongoClient(uri)
    db = client['novogen']
    projects = db['projects']
    return projects


@app.route('/api/account/register', methods=['POST'])
def register():
    credentials = request.get_json()

    username = credentials['username']
    password = credentials['password']

    cookie = int(username) + int(password)

    users = mongo_users()
    registration = {'user': cookie,
                    'projects': []}
    registration_id = users.insert_one(registration).inserted_id
    print(registration_id)

    response = app.response_class(
        response=json.dumps(registration),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/api/account/user', methods=['GET'])
def user():
    cookie = request.args.get('cookie', '')

    users = mongo_users()
    u = users.find_one({'user': cookie})

    if u is None:
        response = app.response_class(
            response=json.dumps({'error_message': 'This user does not exist'}),
            status=400,
            mimetype='application/json'
        )

        return response

    res = {}
    projects = mongo_projects()
    for pid in u['projects']:
        p = projects.find_one({'project': pid})
        res[pid] = p['name']
    j = res
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/api/project', methods=['GET'])
def project():
    cookie = request.args.get('cookie', '')
    users = mongo_users()
    u = users.find_one({'user': cookie})

    project_id = request.args.get('project_id', '')

    if project_id not in u['projects']:
        response = app.response_class(
            response=json.dumps({'error_message': 'This user does not have permission to access this project'}),
            status=200,
            mimetype='application/json'
        )

        return response

    projects = mongo_projects()
    p = projects.find_one({'project_id': project_id})

    if p is None:
        response = app.response_class(
            response=json.dumps({'error_message': 'This project does not exist'}),
            status=400,
            mimetype='application/json'
        )

        return response

    response = app.response_class(
        response=json.dumps({'molecules': p['molecules']}),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/api/project/upload', methods=['POST'])
def upload():
    lines = request.get_json(force=True)['file']
    print(lines)
    molecules = gen(lines)

    res = {'json': []}
    for m in molecules:
        buffered = cStringIO.StringIO()
        m.molecular_img.save(buffered, format='PNG')
        img_str = base64.b64encode(buffered.getvalue())
        molecule = {'molecule': m.smiles,
                    'log_p': m.log_p,
                    'tpsa': m.tpsa,
                    'num_h_donors': m.num_h_donors,
                    'num_h_acceptors': m.num_h_acceptors,
                    'molecular_weight': m.molecular_weight,
                    'molecular_img': img_str}

        res['json'].append(molecule)

    '''
    projects = mongo_projects()

    molecules = gen(lines)
    project_id = projects.insert_one({'molecules': lines}).inserted_id

    response = app.response_class(
        response=json.dumps({'project_id': project_id,
                             'molecules': molecules}),
        status=200,
        mimetype='application/json'
    )

    cookie = request.args.get('cookie', '')
    users = mongo_users()
    u = users.find_one({'user': cookie})
    users.update(
        {'_id': u['_id']},
        {
            '$push': {'projects': project_id}
        }
    )
    '''

    my_safe.values = res

    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
