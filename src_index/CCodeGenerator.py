import ConfigParser, os
import string
from src_index import app

class CCodeGenerator:
    """Generates all C code."""

    def __init__(self, config, delay=False, edge=False):#, counters):
        self.config = config
        self.code = ""
        self.delay = delay
        self.edge = edge
        #self.counters = counters
        self.__begin()
    
    def __begin(self):
        """Initialize code. Add includes etc."""
        
        #Add includes
        self.code = self.config.get("base", "header") + "\n"
        for include in string.split(self.config.get("base", "includes"), " "):
            self.code = self.code + "#include &lt" + include + "&gt\n"
            
        #Add defines
        self.code = self.code + "\n"
        for define in string.split(self.config.get("base", "defines"), ","):
            self.code = self.code + define + "\n"
        
        #Add variables
        self.code = self.code + "\n"
        self.code = self.code + self.config.get("base", "variables")
        
        #Add functions
        self.code = self.code + "\n"
        self.code = self.code + self.config.get("base", "functions")
        
        #Add io
        self.code = self.code + "\n"
        self.code = self.code + self.config.get("base", "io")
            
        #Add delay stuff
        if self.delay:
            self.code = self.code + self.config.get("base", "delay")
            self.code = self.code + self.config.get("base", "timer")
        
        if self.edge:
            self.code = self.code + self.config.get("base", "edge")
            
        #Start main function
        self.code = self.code + "\n int main(void){"
        
        #Init GPIO
        self.code = self.code + "init_gpio();"
        
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
    
    def getOutput(self, id, elements):
        """Return output"""
        
        if id.startswith("Y"):
            if elements.find(".//coil[@id='" + id + "']").attrib["type"] == "set":
                return self.config.get("elements_output", id + "_SET")
            else:
                return self.config.get("elements_output", id + "_RESET")
        elif id.startswith("T"):
            delayCount = elements.find(".//timer[@id='" + id + "']").attrib["delay"]
            return 'setTimer(' + id[1:] + ', ' + delayCount + ')'
        else:
            return self.config.get("elements_output", id)
        
    def getEdge(self, id, edge):
        """Return edge type connector C code"""
        
        id = id[id.find('(')+1:id.find(')')]
        if edge == "rising":
            return 'checkEdge(' + id + ', ' + id[-1] +', true)'
        return 'checkEdge(' + id + ', ' + id[-1] +', false)' 
    
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
