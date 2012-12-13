#!/usr/bin/python

from lib.CodeGenerator import *
from lib.Condition import *



config = ConfigParser.ConfigParser()
config.readfp(open("conf/stm32f103vct6.conf"))

gen = CodeGenerator(config)

gen.appendCondtion(Condition.logicAnd(config.get("elements", "y1"), config.get("elements", "y2")), config.get("elements", "y1_type_set"))
gen.appendCondtion(Condition.logicNot(config.get("elements", "y1")), config.get("elements", "y1_type_set"))


print gen.getCode()