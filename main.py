from JSParser import Parser

__author__ = 'Robur'


file = open('jssrc/jquery.js', encoding='UTF8')

js = file.read()
file.close()

parser = Parser()
parser.src = js

tree = parser.buildAST()

