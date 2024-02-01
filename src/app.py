from flask import Flask
from main import run_tests
from os import environ, path

app = Flask(__name__)


@app.route("/integration/")
def hello_world():
    with open(path.join(environ['BASE_DIR'], 'config/test_config.txt'), 'r') as file:
        return file.read()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=False)
