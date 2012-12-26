from flask import url_for, render_template, request, jsonify
from src_index import app
from src_index import XmlGenerator
from XmlGenerator import NoOutputsError, CellError, Node, Path
import validate

@app.route("/")
def index():
	return render_template('/index.html')

@app.route("/get_json",methods=['POST', 'GET'])
def get_json():
	data = request.json
	
	try:
		try:
			xml = XmlGenerator.XmlGenerator()
			output = xml.start(data)
			print output
			try:
				validate.validate_xml(output)
			except Exception:
				return 'Error, incorrect element name'
			
		except NoOutputsError:
			return 'Error! No output'
		except CellError as e:		
			return 'Error in row: %s, cell: %s'%((e.id_row+1), e.id_cell)
		except Exception:
			return 'Error'
		finally:
			Node.node_counter = 0
			Path.path_counter = 0
	finally:
		Node.node_counter = 0
        Path.path_counter = 0
        return '<div style="color:green">Conversion successful!</div>'
	
	

@app.route("/load_example/<num>")
def load_example(num = 1):
	data = app.open_resource('static/mylist%s.json'%num, 'r')
	data = eval(data.read())
	return jsonify(data)



