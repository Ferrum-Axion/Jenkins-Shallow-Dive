from flask import Flask
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify(success=True,message='Hello World')

@app.route('/<name>')
def hello(name):
    return jsonify(success=True,message=f'Hello {name}')



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
