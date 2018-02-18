from flask import Flask, render_template, request, json
from pymongo import MongoClient
from model.gen import gen
import random
import base64
import cStringIO
from elasticsearch import Elasticsearch

es = Elasticsearch()
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/home')
def home():
    data = []
    for i in range(0, 100):
        data.append({
            'molecule': 'Name ' + str(i + 1),
            'logP': round(random.random(), 2),
            'TPSA': round(random.random(), 2),
            'molWeight': random.random() * 500,
            'donors': int(random.random() * 5),
            'acceptors': int(random.random() * 4),
            'image': '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'
        })
    return render_template('home.html', projects=data)

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
    file = request.files['file']
    lines = list(file.read().splitlines())
    print(lines)
    molecules = gen(lines)
    print(molecules)

    res = []
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

        res.append(molecule)

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

    print(res)
    return render_template('home.html', summary = json.dumps(res))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
