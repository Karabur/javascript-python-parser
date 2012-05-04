import AST
from JSLexer import TOK, Lexer
import JSLexer


__author__ = 'Robur'

class FOLLOW:
    SourceElements = [
        (TOK.PUNCTUATOR, '}'),
        (TOK.EOF, None)
    ]


#noinspection PyTypeChecker
class FIRST:
    Statement = [
        (TOK.PUNCTUATOR, '{'),
        (TOK.RESERVED, 'var'),
        (TOK)
    ]
    FunctionDeclaration = [(TOK.RESERVED, 'function')]


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
        self.REMode = True
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
        if not self.match(token, value):
            if value == None: value = ''
            else: value = ' ' + value
            self.error('Expected:' + JSLexer.tokenToStr(token, value) + ' ,got \'' + self.lookup()[1] + '\'')
        return self.nextToken()

    def nextToken(self):
        if self.lookupToken != None:
            tok = self.lookupToken
            self.lookupToken = None
            return tok
        return self.lexer.getNext()


    def parseProgram(self):
        self.ASTRoot = AST.ProgramNode(self.parseSourceElements())

    def parseFunctionDeclaration(self):
        self.expect(TOK.RESERVED, 'function')
        name = self.expect(TOK.ID)[1]
        arguments = []
        self.expect(TOK.PUNCTUATOR, '(')
        if self.match(TOK.ID):
            arguments.append(self.nextToken()[1])
            while self.match(TOK.PUNCTUATOR, ','):
                self.nextToken()
                arguments.append(self.expect(TOK.ID)[1])
        self.expect(TOK.PUNCTUATOR, ')')
        self.expect(TOK.PUNCTUATOR, '{')
        sourceElements = self.parseSourceElements()
        self.expect(TOK.PUNCTUATOR, '}')

        return AST.FunctionDeclaration(name, arguments, sourceElements)

    def parseSourceElement(self):
        if self.matchList(FIRST.FunctionDeclaration):
            return self.parseFunctionDeclaration()
        return self.parseStatement()

    def parseSourceElements(self):
        sourceElements = []
        while not self.matchList(FOLLOW.SourceElements):
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
        if self.match(TOK.RESERVED, 'var'):
            return self.parseVariableStatement()

        self.unexpected()

    def unexpected(self):
        token = self.lookup()
        if token[1] != None:
            self.error('Unexpected: ' + token[1])
        else:
            self.error('Unexpected: ' + JSLexer.tokenToStr(token[0]))

    def parseVariableStatement(self):
        declarations = []
        self.expect(TOK.RESERVED, 'var')
        declarations.append(self.parseVariableDeclaration())
        while self.match(TOK.PUNCTUATOR, ','):
            declarations.append(self.parseVariableDeclaration())
        self.expect(TOK.PUNCTUATOR, ';')
        return AST.VariableStatement(declarations)

    def parseVariableDeclaration(self):
        id = self.expect(TOK.ID)[1]
        initializer = None
        if self.match(TOK.PUNCTUATOR, '='):
            self.nextToken()
            initializer = self.parseAssignmentExpression()
        return AST.VariableDeclaration(id, initializer)

    def parseAssignmentExpression(self):
        #todo: unfinished!
        return self.parseLeftHandSideExpression()

    def parseLeftHandSideExpression(self):
        # LeftHandSideExpression ::
        # (NewExpression | MemberExpression) ...
        result = None
        if self.match(TOK.RESERVED, 'new'):
            result = self.parseNewExpression()
        else:
            result = self.parseMemberExpression()

        while True:
            if self.match(TOK.PUNCTUATOR, '('):
                args = self.parseArguments()
                result = AST.Call(result, args)
            else:
                return result

    def parseNewExpression(self):
        newCount = [0]
        while self.match(TOK.RESERVED,'new'):
            newCount[0] += 1
            self.nextToken()
        result = self.parseMemberExpression(newCount)
        while newCount[0]:
            result = AST.New(result,[])
            newCount[0] -= 1
        return result

    #we use array trick to pass mutable list and use modified value in caller
    def parseMemberExpression(self, newCount=None):
        # MemberExpression ::
        #(PrimaryExpression | FunctionLiteral)
        #   ('[' Expression ']' | '.' Identifier | Arguments)*
        result = None
        if not newCount: newCount = [0]
        if self.match(TOK.RESERVED, 'function'):
            #todo: parse function expression
            pass
        else:
            result = self.parsePrimaryExpression()


        while True:
            #todo:parse [] . ()
            if self.match(TOK.PUNCTUATOR,'('):
                if not newCount[0]: return result
                args = self.parseArguments()
                newCount[0] -= 1
                result = AST.New(result,args)
            else:
                return result


    def parsePrimaryExpression(self):
        if self.match(TOK.RESERVED, 'this'):
            self.nextToken()
            return AST.This()

        if self.match(TOK.BOOL):
            return AST.Literal(self.nextToken())

        if self.match(TOK.NULL):
            return AST.Literal(self.nextToken())

        if self.match(TOK.ID):
            token = self.nextToken()
            return AST.Identifier(token[1])

        if self.match(TOK.NUMERIC):
            token = self.nextToken()
            return AST.Number(token[1])

        if self.match(TOK.PUNCTUATOR, '['):
            return self.parseArrayLiteral()

        if self.match(TOK.PUNCTUATOR, '{'):
            return self.parseObjectLiteral()

        if self.match(TOK.PUNCTUATOR, '('):
            return self.parseExpression()

        if self.match(TOK.REGEXP):
            return AST.Literal(self.nextToken()[1])

        #todo: not finished
        self.unexpected()

    def parseArguments(self):
        arguments = []
        self.expect(TOK.PUNCTUATOR, '(')
        done = self.match(TOK.PUNCTUATOR, ')')
        while not done:
            arguments.append(self.parseAssignmentExpression())
            if self.match(TOK.PUNCTUATOR, ','):
                self.nextToken()
            else:
                done = True
        self.expect(TOK.PUNCTUATOR, ')')
        return arguments

    def parseArrayLiteral(self):
        list = []
        self.expect(TOK.PUNCTUATOR, '[')
        done = self.match(TOK.PUNCTUATOR, ']')
        while not done:
            if self.match(TOK.PUNCTUATOR, ','):
                list.append(AST.HoleLiteral())
            else:
                list.append(self.parseAssignmentExpression())
            if not self.match(TOK.PUNCTUATOR, ']'):
                self.expect(TOK.PUNCTUATOR, ',')
            else:
                done = True
        self.expect(TOK.PUNCTUATOR, ']')
        return AST.Array(list)

    def parseObjectLiteral(self):
        self.expect(TOK.PUNCTUATOR, '{')
        properties = []

        while not self.match(TOK.PUNCTUATOR, '}'):
            if self.match(TOK.ID) or self.match(TOK.RESERVED) or self.match(TOK.FUTURE_RESERVED):
                key = self.nextToken()[1]
                if key == 'get' or key == 'set':
                    #pass properties to parse function because of tricky parsing of getter-setter
                    #they must be combined to one accessor property
                    self.parseGetSetProperty(key != 'get', properties)
                    if not self.match(TOK.PUNCTUATOR, '}'): self.expect(TOK.PUNCTUATOR, ',')
                    continue
            elif self.match(TOK.NUMERIC):
                key = self.nextToken()[1]
            else:
                key = self.expect(TOK.STRING)[1]
            self.expect(TOK.PUNCTUATOR, ':')
            value = self.parseAssignmentExpression()

            #todo: check if accessor property exists
            properties.append(AST.ObjectProperty(key, value))

            if not self.match(TOK.PUNCTUATOR, '}'): self.expect(TOK.PUNCTUATOR, ',')

        self.expect(TOK.PUNCTUATOR, '}')
        return AST.ObjectLiteral(properties)

    def parseGetSetProperty(self, isSetter, properties):
        paramName = getterBody = setterBody = None

        if self.match(TOK.ID) or self.match(TOK.RESERVED) or self.match(TOK.FUTURE_RESERVED)\
           or self.match(TOK.NUMERIC) or self.match(TOK.STRING):
            key = self.nextToken()[1]
            self.expect(TOK.PUNCTUATOR, '(')
            if isSetter: paramName = self.expect(TOK.ID)[1]
            self.expect(TOK.PUNCTUATOR, ')')
            self.expect(TOK.PUNCTUATOR, '{')
            if isSetter: setterBody = self.parseSourceElements()
            else: getterBody = self.parseSourceElements()
            self.expect(TOK.PUNCTUATOR, '}')

            founded = None
            for s in properties:
                if s.key == key:
                    if type(s) != AST.ObjectGetSetProperty:
                        self.error('Can not have both data and accessor property with same name!')
                    else:
                        if setterBody and s.setterBody: self.error('Can not have multiple accessor property with same name!')
                        if getterBody and s.getter: self.error('Can not have multiple accessor property with same name!')
                    if isSetter:
                        s.setterBody = setterBody
                        s.paramName = paramName
                    else:
                        s.getterBody = getterBody
                    founded = s
                break
            if not founded:
                properties.append(AST.ObjectGetSetProperty(key,getterBody,setterBody,paramName))
        else:
            self.unexpected()

    def parseExpression(self):
        self.expect(TOK.PUNCTUATOR,'(')
        result = self.parseAssignmentExpression()
        while self.match(TOK.PUNCTUATOR,','):
            self.nextToken()
            result = AST.BinaryExpression(',', result, self.parseAssignmentExpression())
        self.expect(TOK.PUNCTUATOR,')')
        return result




