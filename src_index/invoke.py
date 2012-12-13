#!/usr/bin/python

from CodeGenerator import *
from Condition import *



config = ConfigParser.ConfigParser()
config.readfp(open("stm32f103vct6.cfg"))

gen = CodeGenerator(config)

gen.appendCondtion(Condition.logicAnd(config.get("elements", "y1"), config.get("elements", "y2")), config.get("elements", "y1_type_set"))
gen.appendCondtion(Condition.logicNot(config.get("elements", "y1")), config.get("elements", "y1_type_set"))


print gen.getCode()