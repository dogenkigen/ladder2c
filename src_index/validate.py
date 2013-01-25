#!/usr/bin/python
from lxml import etree
from src_index import app

def validate_xml(output):
    #load files
    fxml = output
    fxsd = app.open_resource('schema.xsd', 'r')
    
    #create parser which will be validate xsd schema
    parser = etree.XMLParser(dtd_validation=True)
    
    #convert files to strings
    xsdStr = ""
    for line in fxsd:
        xsdStr = xsdStr + line
       
    xmlStr = fxml
    
    schema_root = etree.XML(xsdStr)
    schema = etree.XMLSchema(schema_root)
    #load schema to parser
    parser = etree.XMLParser(schema = schema)
    
    #validate xml
    root = etree.fromstring(xmlStr, parser)
    
    
