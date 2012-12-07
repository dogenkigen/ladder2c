from flask import Flask, url_for, render_template, request, jsonify
import json
import os

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():
	return render_template('/index.html')

@app.route("/add", methods=['POST', 'GET'])
def add_entry():
#	f = app.open_resource('static/mylist.json')
#	return json.dumps(f.read())
	d = app.open_resource('static/mylist.json')
	
	return jsonify(json.load(d))

@app.route("/add2", methods=['POST', 'GET'])
def add_entry2():
	var1 = request.form["var1"]
	var2 = request.form["var2"]
	return jsonify(obj1={'propertyA':var1, 'propertyB':var2})

if __name__ == "__main__":
    #To make this publicly available simply set parameter host='0.0.0.0'.
	app.run(debug=True, host='0.0.0.0')


