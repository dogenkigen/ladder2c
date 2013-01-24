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
