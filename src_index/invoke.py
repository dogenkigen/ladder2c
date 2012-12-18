#!/usr/bin/python

from lib.CodeGenerator import *
from lib.Condition import *
from lxml import etree
from xml.etree.ElementTree import tostring
from debian.debtags import output
import xml.etree.ElementTree as ET


#"""

def recurse(object):
    if len(object) > 1:
        elemList = []
        for oneElem in object:
            if oneElem.tag == "elem":
                elemList.append(config.get("elements", oneElem.attrib["id"]))
            else:
                elemList.append(recurse(oneElem))
        if object.tag == "and":
            return Condition.logicMultiple(elemList, "&&")
        if object.tag == "or":
            return Condition.logicMultiple(elemList, "||")        
    else:
        if object.tag == "elem":
            return config.get("elements", object.attrib["id"])
        if object.tag == "not":
            return Condition.logicOne(recurse(object.find(".*")), "!")
    
    raise Exception("Program is invalid!")
    return

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


"""
countersList = []

elements = root.getiterator("elements")

for element in elements:
    for counter in element.getiterator("counter"):
        countersList.append([counter.attrib["id"], counter.attrib["countTo"], counter.attrib["target"]])
"""

gen = CodeGenerator(config, True)



for output in root.find("diagram").findall("output"):
    if output.attrib["id"]. startswith("T"):
        gen.appendCondtion(recurse(output.find(".*")), gen.getTimer()#TODO
    else:
        gen.appendCondtion(recurse(output.find(".*")), config.get("elements", output.attrib["id"]))
        

print gen.getCode()

