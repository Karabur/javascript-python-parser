import AST
import JSLexer

__author__ = 'Robur'


class Parser:
    def __init__(self):
        self.state = 0
        self.src = ''
        self.nextToken = None
        self.REMode = False
        self.lexer = JSLexer.Lexer()

    def lookup(self):
        if not self.nextToken:
            self.nextToken = self.lexer.getNext(self.REMode)
        return self.nextToken


    def buildAST(self):
        self.lexer.setSrc(self.src)

        self.ASTRoot = AST.ProgramNode()
        if self.match(JSLexer.TOK_EOF): return

        self.error('error parsing Program')

    def match(self, token):
        return self.lookup()[0] == token

    def error(self, msg):
        raise Exception(msg)



