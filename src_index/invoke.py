#!/usr/bin/python

from lib.CodeGenerator import *
from lib.Condition import *
from lxml import etree
from xml.etree.ElementTree import tostring
from debian.debtags import output
import xml.etree.ElementTree as ET


#"""

def recurse(object, super=None):
    if object.tag != "elem":
        return recurse(object.find(".//*"), object.tag)
    else:
        if super == "not":
            print object.attrib["id"]
            return Condition.logicNot(config.get("elements", object.attrib["id"]))
        
        elif super == "and":
            elemsList = []
            for elem in object:
                elemsList.append(object.attrib["id"])
                
            return Condition.logicNot(config.get("elements", elemsList))
        
        elif super == "or":
            elemsList = []
            for elem in object:
                elemsList.append(object.attrib["id"])
        
            return Condition.logicNot(config.get("elements", elemsList))
                                      
        
                
            
        #"""
            
#"""    
           

#load files
fxml = open('program.xml')
fxsd = open('schema.xsd')

#create parser which will be validate xsd schema
parser = etree.XMLParser(dtd_validation=True)

#convert files to strings
xsdStr = ""
for line in fxsd:
    xsdStr = xsdStr + line
    
xmlStr = ""
for line in fxml:
    xmlStr = xmlStr + line

schema_root = etree.XML(xsdStr)
schema = etree.XMLSchema(schema_root)
#load schema to parser
parser = etree.XMLParser(schema=schema)

#validate xml
root = etree.fromstring(xmlStr, parser)
config = ConfigParser.ConfigParser()
config.readfp(open("conf/stm32f103vct6.conf"))



countersList = []

elements = root.getiterator("elements")

for element in elements:
    #print tostring(element)
    for counter in element.getiterator("counter"):
        #print tostring(counter)
        countersList.append([counter.attrib["id"], counter.attrib["countTo"], counter.attrib["target"]])


gen = CodeGenerator(config, countersList)



for output in root.find("diagram").findall("output"):
    gen.appendCondtion(recurse(output), config.get("elements", output.attrib["id"]))
        


"""

gen.appendCondtion(Condition.logicAnd(config.get("elements", "y1"), config.get("elements", "y2")), config.get("elements", "y1_type_set"))
gen.appendCondtion(Condition.logicNot(config.get("elements", "y1")), config.get("elements", "y1_type_set"))

gen.appendCondtion(Condition.logicNot(config.get("elements", "y1")), "C1")




"""
print gen.getCode()


"""
            for counter in elements.getiterator("counter"):
                if output == counter.attrib["id"]:"""
