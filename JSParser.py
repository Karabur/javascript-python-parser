import AST
from JSLexer import TOK, Lexer


__author__ = 'Robur'

FOLLOW_SourceElements = [ (TOK.PUNCTUATOR , '}'),
                          (TOK.EOF,None)
                        ]

class Parser:
    def __init__(self):
        self.state = 0
        self.src = ''
        self.lexer = Lexer()

    def lookup(self):
        if not self.lookupToken:
            self.lookupToken = self.lexer.getToken(self.REMode)
        return self.lookupToken


    def reset(self):
        self.lexer.setSrc(self.src)
        self.lookupToken = None
        self.REMode = False
        self.currentNode = None
        self.ASTRoot = None


    def buildAST(self):
        self.reset()
        self.parseProgram()

    def match(self, token, value=None):
        if value == None:
            return self.lookup()[0] == token
        else:
            return self.lookup()[0] == token and self.lookup()[1] == value

    def error(self, msg):
        raise Exception(msg)



    def expect(self, token, value=None):
        if not self.match(token,value):
            if value == None: value = ''
            else: value = ' ' + value
            self.error('Expected:'+ getTokenTypeName(token) + value + ' ,got \''+ self.lookup()[1]+'\'')
        return self.nextToken()

    def nextToken(self):
        if self.lookupToken != None:
            tok = self.lookupToken
            self.lookupToken = None
            return tok
        return self.lexer.getNext()


    def parseProgram(self):
        node = AST.ProgramNode()
        self.ASTRoot = node

#        while not self.match(TOK.EOF):
#            node.sourceElements.append(self.parseSourceElement())
        node.sourceElements = self.parseSourceElements()

    def parseFunctionDeclaration(self):
        self.expect(TOK.RESERVED,'function')
        name = self.expect(TOK.ID)[1]
        arguments = []
        self.expect(TOK.PUNCTUATOR,'(')
        if self.match(TOK.ID):
            arguments.append(self.nextToken()[1])
            while self.match(TOK.PUNCTUATOR,','):
                self.nextToken()
                arguments.append(self.expect(TOK.ID)[1])
        self.expect(TOK.PUNCTUATOR,')')
        self.expect(TOK.PUNCTUATOR,'{')
        sourceElements = self.parseSourceElements()
        self.expect(TOK.PUNCTUATOR,'}')

        return AST.FunctionDeclaration(name,arguments,sourceElements)

    def parseSourceElement(self):
        if self.match(TOK.RESERVED,'function'):
            return self.parseFunctionDeclaration()
        elif self.match(TOK.PUNCTUATOR, '{'):
            return self.parseStatement()

    def parseSourceElements(self):
        sourceElements = []
        while not self.matchList(FOLLOW_SourceElements):
            sourceElements.append(self.parseSourceElement())
        return sourceElements

    def matchList(self, list):
        token = self.lookup()
        for listToken in list:
            if listToken[1] == None:
                if token[0] == listToken[0]: return True
            elif token[1] == listToken[1] and token[0] == listToken[0]:
                return True
        return False

    def parseBlock(self):
        statements = []
        self.expect(TOK.PUNCTUATOR, '{')
        while not self.match(TOK.PUNCTUATOR, '}'):
            statements.append(self.parseStatement())
        self.expect(TOK.PUNCTUATOR, '}')
        return AST.Block(statements)

    def parseStatement(self):
        if self.match(TOK.PUNCTUATOR, '{'):
            return self.parseBlock()



