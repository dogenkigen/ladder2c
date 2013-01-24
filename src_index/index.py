from flask import url_for, render_template, request, jsonify
from src_index import app
from src_index import XmlGenerator
from XmlGenerator import NoOutputsError, CellError, Node, Path
import validate
from ConfigParser import ConfigParser
from lxml import etree
from src_index import CCodeGenerator
from src_index import LogicCondition 

config = ConfigParser()
# just for now. should load from form
config.readfp(app.open_resource("conf/stm32f103vct6.conf", 'r'))

def getInput(id, elements):
	if elements.find(".//contact[@id='" + id + "']").attrib["normal"] == "true":
		return config.get("elements_input", id)
	else:
		return "!(" + config.get("elements_input", id) + ")"

def getOutput(id, elements):
	if id.startswith("Y"):
		if elements.find(".//coil[@id='" + id + "']").attrib["type"] == "set":
			return config.get("elements_output", id + "_SET")
		else:
			return config.get("elements_output", id + "_RESET")
	else:
		return config.get("elements_output", id)

def parseXml(xml):
	elements = xml.find("elements")
	if elements.find(".//timer") is not None:
		gen = CCodeGenerator.CCodeGenerator(config, True)
	else:
		gen = CCodeGenerator.CCodeGenerator(config, False)

	for output in xml.find("diagram").findall("output"):
	    if output.attrib["id"]. startswith("T"):
	        id = output.attrib["id"]
	        timer = elements.find(".//timer[@id='" + id + "']")
	        gen.appendCondtion(recurse(output.find(".*"), elements), gen.getTimer(timer.attrib["delay"], timer.attrib["unit"]))  # TODO
	    else:
	        gen.appendCondtion(recurse(output.find(".*"), elements), getOutput(output.attrib["id"], elements))

	return gen.getCode()

def recurse(object, elements):
	"""Recursive method for parsing XML program"""
	if len(object) > 1:
		elemList = []
		for oneElem in object:
		    if oneElem.tag == "elem":
		        elemList.append(getInput(oneElem.attrib["id"], elements))
		    else:
				elemList.append(recurse(oneElem, elements))

		if object.tag == "and":
		    return LogicCondition.LogicCondition.logicMultiple(elemList, "&&")
		if object.tag == "or":
		    return LogicCondition.LogicCondition.logicMultiple(elemList, "||")        
	else:
		if object.tag == "elem":
		    return getInput(object.attrib["id"], elements)#config.get("elements", object.attrib["id"])
		if object.tag == "not":
		    return LogicCondition.LogicCondition.logicOne(recurse(object.find(".*"), elements), "!")
    
	raise Exception("Program is invalid!")

def loadParser():
	#load files
	fxsd = app.open_resource('schema.xsd', 'r')

	#create parser which will be validate xsd schema
	parser = etree.XMLParser(dtd_validation=True)

	#convert files to strings
	xsdStr = ""
	for line in fxsd:
	    xsdStr = xsdStr + line
	schema_root = etree.XML(xsdStr)
	schema = etree.XMLSchema(schema_root)
	#load schema to parser
	return etree.XMLParser(schema=schema)

@app.route("/")
def index():
	return render_template('/index.html')

@app.route("/get_json", methods=['POST', 'GET'])
def get_json():
	data = request.json
	ccode = ''
	try:
		try:
			xml = XmlGenerator.XmlGenerator()
			outputXml = xml.start(data)
			try:
				validate.validate_xml(outputXml)
			except Exception:
				return 'Error, incorrect element name'
			print "-----------XML--------------"
			print outputXml
			print "-----------XML--------------"
			print "-----------C CODE--------------"
			ccode = parseXml(etree.fromstring(outputXml, loadParser()))
			print ccode
			print "-----------C CODE--------------"
			f = app.open_instance_resource('tmp', 'w')
			f.write(ccode)
			f.close()
			
		except NoOutputsError:
			return 'Error! No output'
		except CellError as e:		
			return 'Error in row: %s, cell: %s' % ((e.id_row + 1), e.id_cell)
		except Exception as e:
			return 'Error'
		finally:
			Node.node_counter = 0
			Path.path_counter = 0
	finally:
		Node.node_counter = 0
        Path.path_counter = 0
        import os
        eval("os.system('astyle %s/tmp')"%app.instance_path)
        f = app.open_instance_resource('tmp', 'rb')
        ccode = f.read()
        msg = '''[msg]<div style=\'color:green\'>Conversion successful!</div>
        		[ccode]%s'''%ccode
        return msg
		
	
	

@app.route("/load_example/<num>")
def load_example(num=1):
	data = app.open_resource('static/mylist%s.json' % num, 'r')
	data = eval(data.read())
	return jsonify(data)

