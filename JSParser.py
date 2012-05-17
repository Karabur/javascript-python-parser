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

#lowest precedence - first (index as a precedence)
Precedence = [
    ['||'],
    ['&&'],
    ['|'],
    ['^'],
    ['&'],
    ['==', '!=', '===', '!==', ],
    ['<', '>', '<=', '>=', 'instanceof', 'in'],
    ['<<', '>>', '>>>'],
    ['+', '-'],
    ['*', '/', '%']
]

AssignmentOperators = [
    (TOK.PUNCTUATOR, '*='),
    (TOK.PUNCTUATOR, '/='),
    (TOK.PUNCTUATOR, '%='),
    (TOK.PUNCTUATOR, '+='),
    (TOK.PUNCTUATOR, '-='),
    (TOK.PUNCTUATOR, '<<='),
    (TOK.PUNCTUATOR, '>>='),
    (TOK.PUNCTUATOR, '>>>='),
    (TOK.PUNCTUATOR, '&='),
    (TOK.PUNCTUATOR, '^='),
    (TOK.PUNCTUATOR, '|=]'),
    (TOK.PUNCTUATOR, '=')
]

class Parser:
    def __init__(self):
        self.state = 0
        self.src = ''
        self.lexer = Lexer()

    def lookup(self):
        if not self.lookupToken or self.LTLookup == None:
            self.lookupToken = self.lexer.getToken(False, True)
            if self.lookupToken[0] == TOK.LT:
                self.LTLookup = True
                self.lookupToken = self.lexer.getToken()
            else:
                self.LTLookup = False
        return self.lookupToken

    def nextToken(self, REMode=False):
        if self.lookupToken != None and not REMode:
            tok = self.lookupToken
            self.lookupToken = self.LTLookup = None
            return tok
        return self.lexer.getToken(REMode)


    def reset(self):
        self.lexer.setSrc(self.src)
        self.lookupToken = None
        self.currentNode = None
        self.ASTRoot = None
        self.LTLookup = None


    def buildAST(self):
        self.reset()
        self.parseProgram()
        return self.ASTRoot

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
        statements = self.parseSourceElements()
        self.expect(TOK.PUNCTUATOR, '}')

        return AST.FunctionDeclaration(name, arguments, statements)

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
            if type(listToken) == tuple:
                if listToken[1] == None:
                    if token[0] == listToken[0]: return True
                elif token[1] == listToken[1] and token[0] == listToken[0]:
                    return True
            else:
                if token[0] == listToken: return True
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
        if self.match(TOK.PUNCTUATOR, ';'):
            self.nextToken()
            return AST.EmptyStatement()
        if self.match(TOK.RESERVED, 'if'):
            return self.parseIfStatement()
        if self.match(TOK.RESERVED, 'do'):
            return self.parseDoWhileStatement()
        if self.match(TOK.RESERVED, 'while'):
            return self.parseWhileStatement()
        if self.match(TOK.RESERVED, 'for'):
            return self.parseForStatement()
        if self.match(TOK.RESERVED, 'continue'):
            return self.parseContinueStatement()
        if self.match(TOK.RESERVED, 'break'):
            return self.parseBreakStatement()
        if self.match(TOK.RESERVED, 'return'):
            return self.parseReturnStatement()
        if self.match(TOK.RESERVED, 'with'):
            return self.parseWithStatement()
        if self.match(TOK.RESERVED, 'switch'):
            return self.parseSwitchStatement()
        if self.match(TOK.RESERVED, 'throw'):
            return self.parseThrowStatement()
        if self.match(TOK.RESERVED, 'try'):
            return self.parseTryStatement()
        if self.match(TOK.RESERVED, 'debugger'):
            self.nextToken()
            self.expectSemicolon()
            return AST.DebuggerStatement()

        self.unexpected()

    def unexpected(self):
        token = self.lookup()
        self.error('Unexpected: ' + JSLexer.tokenToStr(token))

    def parseVariableStatement(self):
        declarations = []
        self.expect(TOK.RESERVED, 'var')
        declarations = self.parseVariableDeclarationsList(False)
        if type(declarations) != list: declarations = [declarations]
        self.expectSemicolon()
        return AST.VariableStatement(declarations)

    def parseVariableDeclaration(self, noIn):
        name = self.expect(TOK.ID)[1]
        initializer = None
        if self.match(TOK.PUNCTUATOR, '='):
            self.nextToken()
            initializer = self.parseAssignmentExpression(noIn)
        return AST.VariableDeclaration(name, initializer)

    def parseAssignmentExpression(self, noIn):
        result = self.parseConditionalExpression(noIn)
        if self.matchList(AssignmentOperators):
            op = self.nextToken()[1]
            result = AST.AssignmentExpression(result, self.parseAssignmentExpression(noIn), op)
        return result

    def parseLeftHandSideExpression(self, noIn):
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
            elif self.match(TOK.PUNCTUATOR, '['):
                self.nextToken()
                property = self.parseExpression(noIn)
                result = AST.Property(result, property)
                self.expect(TOK.PUNCTUATOR, ']')
            elif self.match(TOK.PUNCTUATOR, '.'):
                self.nextToken()
                propName = self.parseIdentifierName()
                result = AST.Property(result, propName)
            else:
                return result

    def parseNewExpression(self):
        newCount = [0]
        while self.match(TOK.RESERVED, 'new'):
            newCount[0] += 1
            self.nextToken()
        result = self.parseMemberExpression(newCount)
        while newCount[0]:
            result = AST.New(result, [])
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
            if self.match(TOK.PUNCTUATOR, '('):
                if not newCount[0]: return result
                args = self.parseArguments()
                newCount[0] -= 1
                result = AST.New(result, args)
            else:
                return result


    def parsePrimaryExpression(self):
        if self.match(TOK.RESERVED, 'this'):
            self.nextToken()
            return AST.This()

        if self.match(TOK.BOOL):
            return AST.BoolLiteral(self.nextToken()[1])

        if self.match(TOK.STRING):
            return AST.Literal(self.nextToken()[1])

        if self.match(TOK.NULL):
            return AST.NullLiteral(self.nextToken()[1])

        if self.match(TOK.ID):
            token = self.nextToken()
            return AST.Identifier(token[1])

        if self.match(TOK.NUMERIC):
            token = self.nextToken()
            return AST.NumericLiteral(token[1])

        if self.match(TOK.PUNCTUATOR, '['):
            return self.parseArrayLiteral()

        if self.match(TOK.PUNCTUATOR, '{'):
            return self.parseObjectLiteral()

        if self.match(TOK.PUNCTUATOR, '('):
            self.expect(TOK.PUNCTUATOR, '(')
            result = self.parseExpression(False)
            self.expect(TOK.PUNCTUATOR, ')')
            return result

        if self.match(TOK.DIV_PUNCTUATOR):
            self.rewind()#reparse as a regexp
            return AST.RegExpLiteral(self.nextToken(True)[1])

        self.unexpected()

    def parseArguments(self):
        arguments = []
        self.expect(TOK.PUNCTUATOR, '(')
        done = self.match(TOK.PUNCTUATOR, ')')
        while not done:
            arguments.append(self.parseAssignmentExpression(False))
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
                list.append(self.parseAssignmentExpression(False))
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
            value = self.parseAssignmentExpression(False)

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
                properties.append(AST.ObjectGetSetProperty(key, getterBody, setterBody, paramName))
        else:
            self.unexpected()

    def parseExpression(self, noIn):
        result = self.parseAssignmentExpression(noIn)
        while self.match(TOK.PUNCTUATOR, ','):
            self.nextToken()
            result = AST.BinaryExpression(result, self.parseAssignmentExpression(noIn), ',')
        return result

    def parseIdentifierName(self):
        if self.matchList([TOK.ID, TOK.FUTURE_RESERVED, TOK.RESERVED]):
            return AST.Identifier(self.nextToken()[1])
        self.unexpected()

    def parsePostfixExpression(self):
        result = self.parseLeftHandSideExpression(False)
        if not self.LTAhead() and self.matchList([(TOK.PUNCTUATOR, '++'), (TOK.PUNCTUATOR, '--')]):
            next = self.nextToken()[1]
            result = AST.PostfixExpression(result, next)
        return result

    def LTAhead(self):
        if self.LTLookup == None:
            self.lookup()
        return self.LTLookup

    def parseUnaryExpression(self):
        next = self.lookup()
        if (next[0] == TOK.PUNCTUATOR
            and (next[1] == '++' or next[1] == '--' or next[1] == '-' or next[1] == '+' or next[1] == '~' or next[1] == '!'))\
        or (next[0] == TOK.RESERVED
            and (next[1] == 'delete' or next[1] == 'typeof' or next[1] == 'void')):
            next = self.nextToken()
            return AST.UnaryExpression(self.parseUnaryExpression(), next[1])
        else:
            return self.parsePostfixExpression()

    def parseBinaryExpression(self, noIn, precedence):
        x = self.parseUnaryExpression()

        for i in reversed(range(precedence, self.Precedence(self.lookup(), noIn) + 1)):
            while self.Precedence(self.lookup(), noIn) == i:
                op = self.nextToken()[1]
                x = AST.BinaryExpression(x, self.parseBinaryExpression(noIn, i), op)

        return x

    #return -1 if not an binary op
    def Precedence(self, token, noIn):
        if token[1] == 'in' and noIn: return -1
        for prec, ops in enumerate(Precedence):
            for op in ops:
                if op == token[1]:
                    return prec
        return -1

    def rewind(self):
        self.lexer.rewind()
        self.lookupToken = self.LTLookup = None

    def parseConditionalExpression(self, noIn):
        result = self.parseBinaryExpression(noIn, 0)

        if self.match(TOK.PUNCTUATOR, '?'):
            self.nextToken()
            #left is always accept in
            left = self.parseAssignmentExpression(False)
            self.expect(TOK.PUNCTUATOR, ':')
            right = self.parseAssignmentExpression(noIn)
            result = AST.ConditionalExpression(result, left, right)

        return result

    def parseIfStatement(self):
        self.expect(TOK.RESERVED, 'if')
        self.expect(TOK.PUNCTUATOR, '(')
        condition = self.parseExpression(False)
        self.expect(TOK.PUNCTUATOR, ')')
        thenStatement = self.parseStatement()
        if self.match(TOK.RESERVED, 'else'):
            self.nextToken()
            elseStatement = self.parseStatement()
        else:
            elseStatement = AST.EmptyStatement()

        return AST.IfStatement(condition, thenStatement, elseStatement)

    def parseDoWhileStatement(self):
        self.expect(TOK.RESERVED, 'do')
        statement = self.parseStatement()
        self.expect(TOK.RESERVED, 'while')
        self.expect(TOK.PUNCTUATOR, '(')
        condition = self.parseExpression(False)
        self.expect(TOK.PUNCTUATOR, ')')
        self.expectSemicolon()
        return AST.DoWhileStatement(condition, statement)

    def parseWhileStatement(self):
        self.expect(TOK.RESERVED, 'while')
        self.expect(TOK.PUNCTUATOR, '(')
        condition = self.parseExpression(False)
        self.expect(TOK.PUNCTUATOR, ')')
        statement = self.parseStatement()
        return AST.WhileStatement(condition, statement)

    def parseForStatement(self):
        condition = next = None
        self.expect(TOK.RESERVED, 'for')
        self.expect(TOK.PUNCTUATOR, '(')
        if not self.match(TOK.PUNCTUATOR, ';'):
            if self.match(TOK.RESERVED, 'var'):
                self.nextToken()
                init = self.parseVariableDeclarationsList(True)
                if self.match(TOK.RESERVED, 'in'):
                    if type(init) == list:
                        self.error('Must be only one variable declaration in for..in statement')
                    self.nextToken()
                    enum = self.parseExpression(False)
                    self.expect(TOK.PUNCTUATOR, ')')
                    body = self.parseStatement()
                    return AST.ForInStatement(init, enum, body)
                if type(init) == list: init = AST.Block(init)
            else:
            #we parse both LeftHandSideExpression and ExpressionNoIn as an ExpressionNoIn
            #because ExpressionNoIn produces LHSE
            #additional checks may be done after that for valid LHSE if next token is 'in'
                init = self.parseExpression(True)
            if self.match(TOK.RESERVED, 'in'):
                self.nextToken()
                enum = self.parseExpression(False)
                self.expect(TOK.PUNCTUATOR, ')')
                body = self.parseStatement()
                return AST.ForInStatement(init, enum, body)
        else:
            init = AST.EmptyStatement
        self.expect(TOK.PUNCTUATOR, ';')
        if not self.match(TOK.PUNCTUATOR, ';'):
            condition = self.parseExpression(False)
        else:
            condition = AST.EmptyStatement
        self.expect(TOK.PUNCTUATOR, ';')
        if not self.match(TOK.PUNCTUATOR, ')'):
            next = self.parseExpression(False)
        else:
            next = AST.EmptyStatement
        self.expect(TOK.PUNCTUATOR, ')')
        statement = self.parseStatement()

        return AST.ForStatement(init, condition, next, statement)

    def parseVariableDeclarationsList(self, noIn):
        declarations = [self.parseVariableDeclaration(noIn)]
        while self.match(TOK.PUNCTUATOR, ','):
            self.nextToken()
            declarations.append(self.parseVariableDeclaration(noIn))
        if len(declarations) == 1: return declarations[0]
        return declarations

    def parseContinueStatement(self):
        self.expect(TOK.RESERVED, 'continue')
        label = None
        if self.LTAhead() or self.match(TOK.PUNCTUATOR, ';') or self.match(TOK.EOF):
            return AST.ContinueStatement(label)
        label = AST.Identifier(self.expect(TOK.ID)[1])
        self.expectSemicolon()
        return AST.ContinueStatement(label)

    def parseBreakStatement(self):
        self.expect(TOK.RESERVED, 'break')
        label = None
        if self.LTAhead() or self.match(TOK.PUNCTUATOR, ';') or self.match(TOK.EOF):
            return AST.BreakStatement(label)
        label = AST.Identifier(self.expect(TOK.ID)[1])
        self.expectSemicolon()
        return AST.BreakStatement(label)

    def parseReturnStatement(self):
        self.expect(TOK.RESERVED, 'return')
        result = None
        if self.LTAhead() or self.match(TOK.PUNCTUATOR, ';') or self.match(TOK.EOF):
            return AST.ReturnStatement(result)
        result = self.parseExpression(False)
        self.expectSemicolon()
        return AST.ReturnStatement(result)

    def parseWithStatement(self):
        self.expect(TOK.RESERVED, 'with')
        self.expect(TOK.PUNCTUATOR, '(')
        expr = self.parseExpression(False)
        self.expect(TOK.PUNCTUATOR, ')')
        stmt = self.parseStatement()
        return AST.WithStatement(expr, stmt)

    def parseSwitchStatement(self):
        self.expect(TOK.RESERVED, 'switch')
        self.expect(TOK.PUNCTUATOR, '(')
        expr = self.parseExpression(False)
        self.expect(TOK.PUNCTUATOR, ')')
        self.expect(TOK.PUNCTUATOR, '{')
        cases = []
        default = [False]
        while not self.match(TOK.PUNCTUATOR, '}'):
            cases.append(self.parseCaseClause(default))
        self.expect(TOK.PUNCTUATOR, '}')
        return AST.SwitchStatement(expr, cases)

    def parseCaseClause(self, default):
        label = None
        if self.match(TOK.RESERVED, 'default'):
            if default[0]: self.error('Multiple default cases not allowed')
            default[0] = True
            self.nextToken()
        else:
            self.expect(TOK.RESERVED, 'case')
            label = self.parseExpression(False)
        self.expect(TOK.PUNCTUATOR, ':')
        statements = []
        while not self.match(TOK.RESERVED, 'case') and not self.match(TOK.RESERVED, 'default') and not self.match(TOK.PUNCTUATOR, '}'):
            statements.append(self.parseStatement())
        return AST.CaseCause(label, statements)

    def expectSemicolon(self):
        if self.match(TOK.PUNCTUATOR, ';'):
            return self.nextToken()
        if self.LTAhead() or self.match(TOK.PUNCTUATOR, '}') or self.match(TOK.EOF):
            return TOK.PUNCTUATOR, ';'

        return self.expect(TOK.PUNCTUATOR, ';')

    def parseThrowStatement(self):
        self.expect(TOK.RESERVED, 'throw')
        if self.LTAhead():
            self.error('No line-terminator in throw statement allowed')
        exception = self.parseExpression(False)
        self.expectSemicolon()
        return AST.ThrowStatement(exception)

    def parseTryStatement(self):
        self.expect(TOK.RESERVED, 'try')
        block = self.parseBlock()
        catchBlock = finBlock = None
        if self.match(TOK.RESERVED,'catch'):
            catchBlock = self.parseCatchClause()
        if self.match(TOK.RESERVED,'finally'):
            finBlock = self.parseFinallyClause()

        if catchBlock == None and finBlock == None:
            self.error('try statement must have catch or finally clause')

        return AST.TryStatement(block, catchBlock, finBlock)

    def parseCatchClause(self):
        self.expect(TOK.RESERVED, 'catch')
        self.expect(TOK.PUNCTUATOR, '(')
        id = AST.Identifier(self.expect(TOK.ID)[1])
        self.expect(TOK.PUNCTUATOR, ')')
        block = self.parseBlock()
        return AST.CatchClause(id,block)

    def parseFinallyClause(self):
        self.expect(TOK.RESERVED, 'finally')
        block = self.parseBlock()
        return AST.FinallyClause(block)
















