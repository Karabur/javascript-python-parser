from lexer import Lexer

__author__ = 'Robur'


file = open('jssrc/script.js', encoding='UTF8')

js = file.read()
file.close()

lexer = Lexer()
lexer.setSrc(js)

print(lexer.__class__)
print(lexer.getNext())

