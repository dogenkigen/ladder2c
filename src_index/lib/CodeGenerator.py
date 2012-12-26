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

import ConfigParser, os
import string
from Condition import *

class CodeGenerator:
    """Generates all C code."""

    def __init__(self, config, delay=False):#, counters):
        self.config = config
        self.code = ""
        self.delay = delay
        #self.counters = counters
        self.__begin()
    
    def __begin(self):
        """Initialize code. Add includes etc."""
        
        #Add includes
        self.code = self.config.get("base", "header") + "\n"
        for include in string.split(self.config.get("base", "includes"), " "):
            self.code = self.code + "#include <" + include + ">\n"
            
        #Add defines
        self.code = self.code + "\n"
        for define in string.split(self.config.get("base", "defines"), ","):
            self.code = self.code + define + "\n"
        
        #Add functions
        self.code = self.code + "\n"
        self.code = self.code + self.config.get("base", "functions")
            
        #Add delay stuff
        if self.delay:
            self.code = self.code + self.config.get("base", "delay")
            
        #Start main function
        self.code = self.code + "int main(void){"
        
        #Init delay
        if self.delay:
            self.code = self.code + "delay_init();"
        
        #Add counters TODO
        """
        for counter in self.counters:
            self.code = self.code + "int counter_" + counter[0] + " = 0;"
            self.code = self.code + "int count_" + counter[0] + "_to = " + counter[1] + ";"
            self.code = self.code + "bool counter_" + counter[0] + "_target = " + counter[2] + ";"
        """
            
        self.code = self.code + "\n"
        self.code = self.code + "\nwhile(1){"
        # TODO add gpio stuff
    
    def getTimer(self, delayCount, delayUnit="ms"):
        if delayUnit == "us":
            return "delay_us(" + str(delayCount) + ")"
        return "delay_ms(" + str(delayCount) + ")"
    
    def appendCondtion(self, condition, output):
        """Add next if condition."""
        
        if output.startswith("C"):
            outputCode = "int *a = &counter_" + output + ";(*a) ++"
        else:
            outputCode = output
        
        self.code = self.code + "if(" + condition + ") {" + outputCode + "; }" 
        
    def getCode(self):
        """Return generated code."""
        
        return self.code + "}return 0;}"
