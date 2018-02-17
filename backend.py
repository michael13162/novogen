from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/api/account/register', methods=['POST'])
def register():
    return None


@app.route('/api/account/user', methods=['GET'])
def user():
    return None


@app.route('/api/project', methods=['GET'])
def project():
    return None


@app.route('/api/project/upload', methods=['POST'])
def upload():
    return None


if __name__ == '__main__':
    app.run()
