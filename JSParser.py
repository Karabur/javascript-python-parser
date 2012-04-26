import AST
import JSLexer

__author__ = 'Robur'


class Parser:
    def __init__(self):
        self.state = 0
        self.src = ''
        self.lookupToken = None
        self.REMode = False
        self.lexer = JSLexer.Lexer()
        self.currentNode = None
        self.ASTRoot = None

    def lookup(self):
        if not self.lookupToken:
            self.lookupToken = self.lexer.getToken(self.REMode)
        return self.lookupToken


    def buildAST(self):
        self.lexer.setSrc(self.src)
        self.parseProgram()

    def match(self, token, value=None):
        if value == None:
            return self.lookup()[0] == token
        else:
            return self.lookup()[0] == token and self.lookup()[1] == value

    def error(self, msg):
        raise Exception(msg)

    def parseProgram(self):
        node = AST.ProgramNode()
        self.ASTRoot = node

        while not self.match(JSLexer.TOK_EOF):
            if self.match(JSLexer.TOK_RESERVED, 'function'):
                node.sourceElements.append(self.parseFunctionDeclaration())
            else:
                self.error('error paring program')

    def parseFunctionDeclaration(self):
        self.expect(JSLexer.TOK_RESERVED,'function')
        name = self.expect(JSLexer.TOK_ID)[1]
        self.expect(JSLexer.TOK_PUNCTUATOR,'(')
        self.expect(JSLexer.TOK_PUNCTUATOR,')')
        self.expect(JSLexer.TOK_PUNCTUATOR,'{')
        self.expect(JSLexer.TOK_PUNCTUATOR,'}')

        return AST.FunctionDeclaration(name)

    def expect(self, token, value=None):
        if not self.match(token,value):
            if value == None: value = ''
            else: value = ' ' + value
            self.error('Expected:'+ JSLexer.getTokenTypeName(token) + value + ' ,got \''+ self.lookup()[1]+'\'')
        return self.nextToken()

    def nextToken(self):
        if self.lookupToken != None:
            tok = self.lookupToken
            self.lookupToken = None
            return tok
        return self.lexer.getNext()


