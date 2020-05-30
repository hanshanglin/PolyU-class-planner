from flask import Flask,url_for,render_template,request,redirect,jsonify,current_app
import data_preprocess
import os
import json

app = Flask(__name__)

app.secret_key = os.urandom(24)

@app.route('/api/<name>', methods=['POST'])
def test_api(name):
    if name == 'test':
        data=data_preprocess.test().T.to_dict()
        t = jsonify(data)
        return t
    if name == 'subjectinfo':
        result = request.json
        sem = result.get('sem', None)
        department = result.get('department', None)
        if sem==None or department==None or len(department)==0:
            return jsonify({})
        return jsonify(data_preprocess.df_filter(sem,department))
    if name == 'classinfo':
        result = request.json
        sem = result.get('sem', None)
        code = result.get('subject', None)
        if sem==None or code==None:
            return jsonify({})
        return jsonify(data_preprocess.class_filter(sem,code))
    if name == 'solve':
        result = request.json
        sem = result.get('sem', None)
        data = result.get('data', None)
        if sem==None or data==None:
            return jsonify({})
        return jsonify(data_preprocess.limit_solve(sem,data))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
