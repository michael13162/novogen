from flask import Flask, render_template, request, json
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


SEED_DATA = [
    {
        'decade': '1970s',
        'artist': 'Debby Boone',
        'song': 'You Light Up My Life',
        'weeksAtOne': 10
    },
    {
        'decade': '1980s',
        'artist': 'Olivia Newton-John',
        'song': 'Physical',
        'weeksAtOne': 10
    },
    {
        'decade': '1990s',
        'artist': 'Mariah Carey',
        'song': 'One Sweet Day',
        'weeksAtOne': 16
    }
]

uri = 'mongodb://user:pass@ds123658.mlab.com:23658/novogen'


@app.route('/api/account/register', methods=['POST'])
def register():
    credentials = request.get_json()

    username = credentials['username']
    password = credentials['password']

    cookie = int(username) + int(password)

    client = MongoClient(uri)
    db = client['novogen']
    users = db['users']
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

    return None


@app.route('/api/project', methods=['GET'])
def project():
    return None


@app.route('/api/project/upload', methods=['POST'])
def upload():
    return None


if __name__ == '__main__':
    app.run()
