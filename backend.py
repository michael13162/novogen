from flask import Flask, render_template, request, json
from pymongo import MongoClient
from model.gen import gen

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')

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
    molecules = gen(lines)

    res = {}
    for m in molecules:
        molecule = {'log_p': m.log_p,
                    'tpsa': m.tpsa,
                    'num_h_donors': m.num_h_donors,
                    'num_h_acceptors': m.num_h_acceptors,
                    'molecular_weight': m.molecular_weight,
                    'molecular_img': 'temp'}

        res[m.smiles] = molecule

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

    return render_template('home.html', json.dumps(res))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
