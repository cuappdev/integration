
from flask import Flask
from main import run_tests

app = Flask(__name__)


@app.route("/integration/")
def hello_world():
    return "<h3>Hello World!</h3>"

# @app.route("/integration/run_tests/", methods=["POST"])
def run():
    run_tests()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=False)
