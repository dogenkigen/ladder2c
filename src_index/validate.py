#!/usr/bin/python
# Ladder2c is ladder logic to C code converter.
# Copyright (C) 2012  Maciej Laskowski

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

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
    
    