from flask import Flask, render_template, request, json
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

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
    return None


@app.route('/api/project/upload', methods=['POST'])
def upload():
    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
