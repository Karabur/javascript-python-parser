#list of reserved words
RESERVED_WORDS = ['break', 'do', 'instanceof', 'typeof', 'case', 'else', 'new', 'var', 'catch', 'finally', 'return',
                  'void', 'continue', 'for',
                  'switch', 'while', 'debugger', 'function', 'this', 'with', 'default', 'if', 'throw', 'delete', 'in',
                  'try']
FUTURE_RESERVED_WORDS = ['class', 'enum', 'extends', 'super', 'const', 'export', 'import']
FUTURE_STRICT_RESERVED_WORDS = ['implements', 'let', 'private', 'public', 'yield', 'interface', 'package', 'protected',
                                'static']
PUNCTUATORS = ['{', '}', '(', ')', '[', ']', '.', ';', ',', '<', '>', '<=', '>=', '==', '!=', '===', '!==', '+', '-',
               '*', '%', '++', '--', '<<', '>>'
    , '>>>', '&', '|', '^', '!', '~', '&&', '||', '?', ':', '=', '+=', '-=', '*=', '%=', '<<=', '>>=', '>>>=', '&=',
               '|=', '^=']
SINGLE_CHARACTER_ESC_SEQ = {'b': '\u0008', 't': '\u0009', 'n': '\u000A', 'v': '\u000B', 'f': '\u000C', 'r': '\u000D',
                            '"': '\u0022', '\'': '\u0027',
                            '\\': '\u005c'}


#tokens

class TOK:
    LT = 1
    SINGLE_COMMENT = 2
    MULTI_COMMENT = 3
    MULTINL_COMMENT = 4
    ID = 5
    NUMERIC = 6
    WS = 7
    RESERVED = 8
    FUTURE_RESERVED = 9
    PUNCTUATOR = 10
    NULL = 11
    BOOL = 12
    STRING = 13
    REGEXP = 14
    DIV_PUNCTUATOR = 15
    UNKNOWN = 999
    EOF = 1000
    ERROR = 1001

class LexerException(Exception):
    pass


def isHexDigit(chr):
    return chr.isdigit() or chr.lower() in 'abcdef'


def isLineTerm(c):
    return c in '\n\u000a\u000d\u2028\u2029'


def isIDStart(c):
    return c.isalpha() or c in '_$'


def isIDPart(c):
    return isIDStart(c) or c.isnumeric()


def isWS(c):
    return c in ['\u0020', '\u0009', '\n', '\r', '\u000c', '\u000b', '\u00a0', '\u1680', '\u2000', '\u2001', '\u2002',
                 '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008', '\u2009', '\u200A', '\u200B', '\u202F',
                 '\u3000']


def hexToDec(char):
    return '0123456789abcdef'.index(char.lower())


class Lexer:
    def __init__(self):
        self.state = 0
        self.src = ''
        self.pointer = -1
        self.forward = -1
        self.eof = False
        self.strictMode = False

    def isEOF(self):
        return self.forward >= len(self.src)

    def lookup(self):
        return self.src[self.forward]

    def setSrc(self, js):
        self.src = js
        self.pointer = 0
        self.forward = 0
        self.eof = False
        self.prevPos = 0
        self.line = self.lastLine = 1
        self.column = self.lastColumn = 1

    def extract(self, tokenType):
        return tokenType, self.src[self.pointer:self.forward]

    def getNext(self, REMode=False):
        try:
            if self.isEOF():
                return TOK.EOF, ''
            self.pointer = self.forward
            if isLineTerm(self.lookup()):
                self.goForward()
                return self.extract(TOK.LT)
            if isWS(self.lookup()):
                self.goForward()
                return TOK.WS, ''

            if self.lookup() == '/':
                self.goForward()
                if self.lookup() == '/':
                    return self.getSingleComment()
                if self.lookup() == '*':
                    return self.getMultiComment()

                if REMode:
                    return self.getRegExp()
                else:
                    if not self.isEOF() and self.src[self.forward] == '=':
                        self.goForward()
                    return self.extract(TOK.DIV_PUNCTUATOR)

            if isIDStart(self.src[self.forward]):
                self.goForward()
                while not self.isEOF() and isIDPart(self.src[self.forward]):
                    self.goForward()
                return self.getIDOrReserved()

            if self.src[self.forward] == '0':
                self.goForward()
                if not self.isEOF() and self.src[self.forward] == '.':
                    self.goForward()
                    return self.getNumericAfterDot()
                    #hex digits
                if not self.isEOF() and self.src[self.forward] in 'xX':
                    self.goForward()
                    if isHexDigit(self.src[self.forward]):
                        while not self.isEOF() and (
                            self.src[self.forward].isdigit() or self.src[self.forward].lower() in 'abcdef'):
                            self.goForward()
                        return self.extractNumeric()
                    raise LexerException('Illegal')
                return self.extractNumeric()

            if self.src[self.forward].isnumeric() and self.src[self.forward] != '0':
                self.goForward()
                while not self.isEOF() and self.src[self.forward].isdigit():
                    self.goForward()
                if not self.isEOF() and self.src[self.forward] == '.':
                    self.goForward()
                    return self.getNumericAfterDot()
                if not self.isEOF() and self.src[self.forward] in 'eE':
                    self.goForward()
                    return self.getNumericExp()
                return self.extractNumeric()

            if self.src[self.forward] == '.':
                self.goForward()
                if self.src[self.forward].isnumeric():
                    return self.getNumericAfterDot()
                return TOK.PUNCTUATOR, '.'

            #check punctuators - must be after all rules which starts from one of punctuator
            for i in [4, 3, 2, 1]:
                if (self.forward + i <= len(self.src)) and self.src[self.forward:self.forward + i] in PUNCTUATORS:
                    self.goForward(i)
                    return self.extract(TOK.PUNCTUATOR)

            #string literals
            if self.src[self.forward] in ['"', "'"]:
                return self.getString()
            self.goForward()
        except LexerException as e:
            print(e)
        return self.extract(TOK.UNKNOWN)


    def getMultiComment(self):
        state = 2
        nl = False
        self.goForward()
        while not self.isEOF():
            if self.src[self.forward] == '\n': nl = True
            if state == 2:
                if self.src[self.forward] == '*':
                    state = 3
                    self.goForward()
                else:
                #                    state = 2
                    self.goForward()
            if state == 3:
                if self.src[self.forward] == '*':
                #                    state = 3
                    self.goForward()
                elif self.src[self.forward] == '/':
                #                    state = 4
                    self.goForward()
                    return TOK.MULTINL_COMMENT if nl else TOK.MULTI_COMMENT, self.src[self.pointer + 2:self.forward - 2]
                else:
                    state = 2
                    self.goForward()


    def getSingleComment(self):
        while not self.isEOF() and not isLineTerm(self.src[self.forward]):
            self.goForward()
        return TOK.SINGLE_COMMENT, self.src[self.pointer + 2:self.forward]


    #NLMode - is the NL must be returned,
    #REMode - RegularExpression mode
    def getToken(self, REMode=False, LTMode=False):
        self.prevPos = self.forward
        self.lastLine = self.line
        self.lastColumn = self.column
        token = self.getNext(REMode)
        while token[0] == TOK.SINGLE_COMMENT or token[0] == TOK.MULTI_COMMENT or token[0] == TOK.WS\
              or (token[0] == TOK.LT and not LTMode) or (token[0] == TOK.MULTINL_COMMENT and not LTMode):
            self.lastLine = self.line
            self.lastColumn = self.column
            token = self.getNext(REMode)
        if token[0] == TOK.MULTINL_COMMENT and LTMode:
            return TOK.LT, ''
        return token

    def extractNumeric(self):
        if not self.isEOF() and isIDStart(self.src[self.forward]):
            return self.extract(TOK.ERROR)
        return self.extract(TOK.NUMERIC)

    def getNumericAfterDot(self):
        while not self.isEOF() and self.src[self.forward].isnumeric():
            self.goForward()
        if not self.isEOF() and self.src[self.forward] in 'eE':
            self.goForward()
            return self.getNumericExp()
        return self.extractNumeric()


    def getNumericExp(self):
        if self.src[self.forward] in '+-':
            self.goForward()
        if self.src[self.forward].isnumeric():
            while not self.isEOF() and self.src[self.forward].isnumeric():
                self.goForward()
            return self.extractNumeric()
        return TOK.UNKNOWN, ''

    def getIDOrReserved(self):
        id = self.src[self.pointer: self.forward]
        if id in RESERVED_WORDS:
            return self.extract(TOK.RESERVED)

        if id in FUTURE_RESERVED_WORDS:
            return self.extract(TOK.FUTURE_RESERVED)

        if self.strictMode and id in FUTURE_STRICT_RESERVED_WORDS:
            return self.extract(TOK.FUTURE_RESERVED)

        if id == 'null':
            return self.extract(TOK.NULL)

        if id == 'true':
            return self.extract(TOK.BOOL)
        if id == 'false':
            return self.extract(TOK.BOOL)

        return self.extract(TOK.ID)

    def getString(self):
        quote = self.src[self.forward]
        token = ''
        self.goForward()
        try:
            while not self.isEOF() and self.src[self.forward] != quote:
                if self.src[self.forward] == '\\':
                    self.goForward()
                    if isLineTerm(self.src[self.forward]):
                        self.goForward()
                    else:
                        token += self.getEscapeSeq()
                else:
                    token += self.src[self.forward]
                    self.goForward()
            if not self.isEOF() and self.src[self.forward] == quote:
                self.goForward()
                return TOK.STRING, token
        except:
            pass
        return self.extract(TOK.ERROR)

    def getEscapeSeq(self):
        if not self.isEOF():
            #single escape character
            if self.src[self.forward] in SINGLE_CHARACTER_ESC_SEQ:
                self.goForward()
                return SINGLE_CHARACTER_ESC_SEQ[self.src[self.forward - 1]]
            if not isLineTerm(self.src[self.forward]) and not self.src[self.forward].isnumeric() and not self.src[
                                                                                                         self.forward] in 'xu':
                self.goForward()
                return self.src[self.forward - 1]
            if self.src[self.forward] == 'u':
                if isHexDigit(self.src[self.forward + 1]) and isHexDigit(self.src[self.forward + 2]) and isHexDigit(
                    self.src[self.forward + 1]) and isHexDigit(self.src[self.forward + 2]):
                    code = 4096 * int(self.src[self.forward + 1]) + 256 * int(self.src[self.forward + 2]) + 16 * int(
                        self.src[self.forward + 3]) + int(self.src[self.forward + 4])
                    self.goForward(5)
                    return chr(code)
            if self.src[self.forward] == 'x':
                if isHexDigit(self.src[self.forward + 1]) and isHexDigit(self.src[self.forward + 2]):
                    code = 16 * hexToDec(self.src[self.forward + 1]) + hexToDec(self.src[self.forward + 2])
                    self.goForward(3)
                    return chr(code)
            if self.src[self.forward] == '0' and self.forward < len(self.src) - 1 and not self.src[
                                                                                          self.forward + 1].isdigit():
                self.goForward()
                return '\0'

        raise LexerException('error parsing string escape sequence')

    def getRegExp(self):
        #RegularExpressionFirstChar
        if not isLineTerm(self.src[self.forward]) and not self.src[self.forward] in '*\\/[':
            self.goForward()
        elif self.src[self.forward] == '\\':
            self.goForward()
            if isLineTerm(self.src[self.forward]):
                return self.extract(TOK.ERROR)
            self.goForward()
        elif self.src[self.forward] == '[':
            self.getRegExpClass()
        else:
            return self.extract(TOK.ERROR)
            #RegularExpressionChars

        while self.src[self.forward] != '/':
            if not isLineTerm(self.src[self.forward]) and not self.src[self.forward] in '\\/[':
                self.goForward()
            elif self.src[self.forward] == '\\':
                self.goForward()
                if isLineTerm(self.src[self.forward]):
                    return self.extract(TOK.ERROR)
                self.goForward()
            elif self.src[self.forward] == '[':
                self.getRegExpClass()
            else:
                return self.extract(TOK.ERROR)

        self.goForward()

        #RegularExpressionFlags
        while self.forward < len(self.src) and isIDPart(self.src[self.forward]):
            self.goForward()
        return self.extract(TOK.REGEXP)


    def getRegExpClass(self):
        self.goForward()
        while self.src[self.forward] != ']':
            if self.src[self.forward] == '\\':
                self.goForward()
                if isLineTerm(self.src[self.forward]):
                    raise LexerException('Error parsing RegExp class - unsuspected LineTerminator')
                self.goForward()
            elif not isLineTerm(self.src[self.forward]) and not self.src[self.forward] in ']\\':
                self.goForward()
            else:
                raise LexerException('Error parsing RegExp')
        self.goForward()

    def rewind(self):
        self.position = self.forward = self.prevPos

    def getLastTokenPos(self):
        return {'line': self.lastLine, 'column': self.lastColumn}

    def goForward(self, step=1):
        while step > 0:
            if self.forward < len(self.src) and isLineTerm(self.src[self.forward]):
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.forward += 1
            step -= 1



def tokenToStr(token, value=None):
    if value == None and type(token) == tuple:
        value = token[1]
        token = token[0]
    if token == TOK.ID: return 'Identifier'
    if token == TOK.EOF: return 'EOF'
    if token == TOK.PUNCTUATOR: return value
    if token == TOK.STRING: return 'String'
    return 'token:' + str(token) + ' \'' + value + '\''