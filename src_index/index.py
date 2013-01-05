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
config.readfp(open("src_index/conf/stm32f103vct6.conf"))

def parseXml(xml):
	elements = xml.find("elements")
	if elements.find(".//timer[@id='T1']") is not None:
		gen = CCodeGenerator.CCodeGenerator(config, True)
	else:
		gen = CCodeGenerator.CCodeGenerator(config, False)

	for output in xml.find("diagram").findall("output"):
	    if output.attrib["id"]. startswith("T"):
	        id = output.attrib["id"]
	        timer = elements.find(".//timer[@id='" + id + "']")
	        gen.appendCondtion(recurse(output.find(".*")), gen.getTimer(timer.attrib["delay"], timer.attrib["unit"]))  # TODO
	    else:
	        gen.appendCondtion(recurse(output.find(".*")), config.get("elements", output.attrib["id"]))
	
	return gen.getCode()

def recurse(object):
	"""Recursive method for parsing XML program"""
	if len(object) > 1:
		elemList = []
		for oneElem in object:
		    if oneElem.tag == "elem":
		        elemList.append(config.get("elements", oneElem.attrib["id"]))
		    else:
				elemList.append(recurse(oneElem))
		
		if object.tag == "and":
		    return LogicCondition.LogicCondition.logicMultiple(elemList, "&&")
		if object.tag == "or":
		    return LogicCondition.LogicCondition.logicMultiple(elemList, "||")        
	else:
		if object.tag == "elem":
		    return config.get("elements", object.attrib["id"])
		if object.tag == "not":
		    return LogicCondition.LogicCondition.logicOne(recurse(object.find(".*")), "!")
    
	raise Exception("Program is invalid!")

def loadParser():
	#load files
	fxsd = open('src_index/schema.xsd')
	
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
	
	try:
		try:
			xml = XmlGenerator.XmlGenerator()
			outputXml = xml.start(data)
			print "-----------XML--------------"
			print outputXml
			print "-----------XML--------------"
			print "-----------C CODE--------------"
			print parseXml(etree.fromstring(outputXml, loadParser()))
			print "-----------C CODE--------------"
			try:
				validate.validate_xml(outputXml)
			except Exception:
				return 'Error, incorrect element name'
			
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
        return '<div style="color:green">Conversion successful!</div>'
	
	

@app.route("/load_example/<num>")
def load_example(num=1):
	data = app.open_resource('static/mylist%s.json' % num, 'r')
	data = eval(data.read())
	return jsonify(data)

