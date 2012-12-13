from flask import url_for, render_template, request, jsonify
from src_index import app
from src_index import XmlGenerator

@app.route("/")
def index():
	return render_template('/index.html')

@app.route("/get_json",methods=['POST', 'GET'])
def get_json():
	data = request.json
		
	xml = XmlGenerator.XmlGenerator()
	output = xml.start(data)
	print output
	return 'True'

@app.route("/load_example")
def load_example():
	data = app.open_resource('static/mylist.json', 'r')
	data = eval(data.read())
	return jsonify(data)




