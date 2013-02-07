import ConfigParser, os
import string
from src_index import app

class CCodeGenerator:
    """Generates all C code."""

    def __init__(self, config, delay=False, edge=False):
        self.config = config
        self.code = ""
        self.delay = delay
        self.edge = edge
        self.__begin()
    
    def __begin(self):
        """Initialize code. Add includes etc."""
        
        # Add includes
        self.code = self.config.get("base", "header") + "\n"
        for include in string.split(self.config.get("base", "includes"), " "):
            self.code = self.code + "#include &lt" + include + "&gt\n"
            
        # Add defines
        self.code = self.code + "\n"
        for define in string.split(self.config.get("base", "defines"), ","):
            self.code = self.code + define + "\n"
        
        # Add variables
        self.code = self.code + "\n" + self.config.get("base", "variables")
        
        # Add functions
        self.code = self.code + "\n" + self.config.get("base", "functions")
        
        # Add io
        self.code = self.code + "\n" + self.config.get("base", "io")
            
        # Add delay stuff
        if self.delay:
            self.code = self.code + self.config.get("base", "delay")
            self.code = self.code + self.config.get("base", "timer")
        
        if self.edge:
            self.code = self.code + "\n" + self.config.get("base", "edge")
            
        # Start main function
        self.code = self.code + "\n int main(void){"
        
        # Init GPIO
        self.code = self.code + "init_gpio();"
        
        # Init delay
        if self.delay:
            self.code = self.code + "delay_init();"
        
        # TODO Add counters
            
        self.code = self.code + "\n"
        self.code = self.code + "\nwhile(1){"
    
    def getOutput(self, id, elements):
        """Return output"""
        
        # Coil outputs
        if id.startswith("Y"):
            if elements.find(".//coil[@id='" + id + "']").attrib["type"] == "set":
                return self.config.get("elements_output", id + "_SET")
            else:
                return self.config.get("elements_output", id + "_RESET")
        # Timers
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
        
        # For flag outputs condition should have 'else'
        # because when it is not fulfilled flag value
        # should be false.
        if output.startswith("R"):
            self.code = self.code + "if(" + condition + ") {" + output + " = true; }else{" + output + " = false;}"
            return

        self.code = self.code + "if(" + condition + ") {" + output + "; }" 
        
    def getCode(self):
        """Return generated code."""
        
        return self.code + "}return 0;}"
