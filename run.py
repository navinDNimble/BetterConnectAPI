from flask import jsonify

from app import app


@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, API!'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=False)
