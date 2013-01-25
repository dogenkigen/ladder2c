import types
from src_index import app

class LogicCondition:
    """Utility to generate logical conditions"""
    
    @staticmethod
    def logicOne(arg, operator):
        code = operator + "(" + arg + ")"
        return code
    
    @staticmethod
    def logicMultiple(args, operator):
        code = "("
        i = 1
        for single in args:
            code = code + single
            if len(args) > i :
                code = code + " " + operator + "\n"
            i += 1
        
        code = code + ")"
        return code
