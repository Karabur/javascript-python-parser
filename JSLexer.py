#list of reserved words
RESERVED_WORDS = ['break', 'do', 'instanceof', 'typeof', 'case', 'else', 'new', 'var', 'catch', 'finally', 'return', 'void', 'continue', 'for',
                  'switch', 'while', 'debugger', 'function', 'this', 'with', 'default', 'if', 'throw', 'delete', 'in', 'try']
FUTURE_RESERVED_WORDS = ['class', 'enum', 'extends', 'super', 'const', 'export', 'import']
FUTURE_STRICT_RESERVED_WORDS = ['implements', 'let', 'private', 'public', 'yield', 'interface', 'package', 'protected', 'static']
PUNCTUATORS = ['{', '}', '(', ')', '[', ']', '.', ';', ',', '<', '>', '<=', '>=', '==', '!=', '===', '!==', '+', '-', '*', '%', '++', '--', '<<', '>>'
    , '>>>', '&', '|', '^', '!', '~', '&&', '||', '?', ':', '=', '+=', '-=', '*=', '%=', '<<=', '>>=', '>>>=', '&=', '|=', '^=']
SINGLE_CHARACTER_ESC_SEQ = {'b': '\u0008', 't': '\u0009', 'n': '\u000A', 'v': '\u000B', 'f': '\u000C', 'r': '\u000D', '"': '\u0022', '\'': '\u0027',
                            '\\': '\u005c'}


#tokens

TOK_NL = 1
TOK_SINGLE_COMMENT = 2
TOK_MULTI_COMMENT = 3
TOK_MULTINL_COMMENT = 4
TOK_ID = 5
TOK_NUMERIC = 6
TOK_WS = 7
TOK_RESERVED = 8
TOK_FUTURE_RESERVED = 9
TOK_PUNCTUATOR = 10
TOK_NULL = 11
TOK_BOOL = 12
TOK_STRING = 13
TOK_REGEXP = 14
TOK_DIV_PUNCTUATOR = 15

TOK_UNKNOWN = 999
TOK_EOF = 1000
TOK_ERROR = 1001

def isHexDigit(chr):
    return chr.isdigit() or chr.lower() in 'abcdef'


def isLineTerm(c):
    return c in '\n\u000a\u000d\u2028\u2029'


def isIDStart(c):
    return c.isalpha() or c in '_$'


def isIDPart(c):
    return isIDStart(c) or c.isnumeric()


def isWS(c):
    return c in ['\u0020','\u0009','\n','\r','\u000c','\u000b','\u00a0','\u1680','\u2000','\u2001','\u2002','\u2003','\u2004','\u2005','\u2006','\u2007','\u2008','\u2009','\u200A','\u200B','\u202F','\u3000']


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

    def extract(self, tokenType):
        return tokenType, self.src[self.pointer:self.forward]

    def getNext(self, REMode=False):
        try:
            if self.isEOF():
                return TOK_EOF, ''
            self.pointer = self.forward
            if isWS(self.lookup()):
                self.forward += 1
                return TOK_WS, ''

            if self.lookup() == '/':
                self.forward += 1
                if self.lookup() == '/':
                    return self.getSingleComment()
                if self.lookup() == '*':
                    return self.getMultiComment()

                if REMode:
                    return self.getRegExp()
                else:
                    if not self.isEOF() and self.src[self.forward] == '=':
                        self.forward += 1
                    return self.extract(TOK_DIV_PUNCTUATOR)

            if isIDStart(self.src[self.forward]):
                self.forward += 1
                while not self.isEOF() and isIDPart(self.src[self.forward]):
                    self.forward += 1
                return self.getIDOrReserved()

            if self.src[self.forward] == '0':
                self.forward += 1
                if not self.isEOF() and self.src[self.forward] == '.':
                    self.forward += 1
                    return self.getNumericAfterDot()
                    #hex digits
                if not self.isEOF() and self.src[self.forward] in 'xX':
                    self.forward += 1
                    if isHexDigit(self.src[self.forward]):
                        while not self.isEOF() and (self.src[self.forward].isdigit() or self.src[self.forward].lower() in 'abcdef'):
                            self.forward += 1
                        return self.extractNumeric()
                    raise Exception('Illegal')
                return self.extractNumeric()

            if self.src[self.forward].isnumeric() and self.src[self.forward] != '0':
                self.forward += 1
                while not self.isEOF() and self.src[self.forward].isdigit():
                    self.forward += 1
                if not self.isEOF() and self.src[self.forward] == '.':
                    self.forward += 1
                    return self.getNumericAfterDot()
                if not self.isEOF() and self.src[self.forward] in 'eE':
                    self.forward += 1
                    return self.getNumericExp()
                return self.extractNumeric()

            if self.src[self.forward] == '.':
                self.forward += 1
                if self.src[self.forward].isnumeric():
                    return self.getNumericAfterDot()
                return TOK_PUNCTUATOR, '.'

            #check punctuators - must be after all rules which starts from one of punctuator
            for i in [4, 3, 2, 1]:
                if (self.forward + i <= len(self.src)) and self.src[self.forward:self.forward + i] in PUNCTUATORS:
                    self.forward += i
                    return self.extract(TOK_PUNCTUATOR)

            #string literals
            if self.src[self.forward] in ['"', "'"]:
                return self.getString()
            self.forward += 1
        except:
            pass
        return self.extract(TOK_UNKNOWN)


    def getMultiComment(self):
        state = 2
        nl = False
        self.forward += 1
        while not self.isEOF():
            if self.src[self.forward] == '\n': nl = True
            if state == 2:
                if self.src[self.forward] == '*':
                    state = 3
                    self.forward += 1
                else:
                #                    state = 2
                    self.forward += 1
            if state == 3:
                if self.src[self.forward] == '*':
                #                    state = 3
                    self.forward += 1
                elif self.src[self.forward] == '/':
                #                    state = 4
                    self.forward += 1
                    return TOK_MULTINL_COMMENT if nl else TOK_MULTI_COMMENT, self.src[self.pointer + 2:self.forward - 2]
                else:
                    state = 2
                    self.forward += 1


    def getSingleComment(self):
        while not self.isEOF() and not isLineTerm(self.src[self.forward]):
            self.forward += 1
        return TOK_SINGLE_COMMENT, self.src[self.pointer + 2:self.forward]


    def getToken(self):
        token = self.getNext()
        while token[0] == TOK_SINGLE_COMMENT or token[0] == TOK_MULTI_COMMENT or token[0] == TOK_WS:
            token = self.getNext()
        if token[0] == TOK_MULTINL_COMMENT:
            return TOK_NL, ''
        return token

    def getRegExpToken(self):
        token = self.getNext(True)
        while token[0] == TOK_SINGLE_COMMENT or token[0] == TOK_MULTI_COMMENT or token[0] == TOK_WS:
            token = self.getNext(True)
        if token[0] == TOK_MULTINL_COMMENT:
            return TOK_NL, ''
        return token

    def extractNumeric(self):
        if not self.isEOF() and isIDStart(self.src[self.forward]):
            return self.extract(TOK_ERROR)
        return self.extract(TOK_NUMERIC)

    def getNumericAfterDot(self):
        while not self.isEOF() and self.src[self.forward].isnumeric():
            self.forward += 1
        if not self.isEOF() and self.src[self.forward] in 'eE':
            self.forward += 1
            return self.getNumericExp()
        return self.extractNumeric()


    def getNumericExp(self):
        if self.src[self.forward] in '+-':
            self.forward += 1
        if self.src[self.forward].isnumeric():
            while not self.isEOF() and self.src[self.forward].isnumeric():
                self.forward += 1
            return self.extractNumeric()
        return TOK_UNKNOWN, ''

    def getIDOrReserved(self):
        id = self.src[self.pointer: self.forward]
        if id in RESERVED_WORDS:
            return self.extract(TOK_RESERVED)

        if id in FUTURE_RESERVED_WORDS:
            return self.extract(TOK_FUTURE_RESERVED)

        if self.strictMode and id in FUTURE_STRICT_RESERVED_WORDS:
            return self.extract(TOK_FUTURE_RESERVED)

        if id == 'null':
            return self.extract(TOK_NULL)

        if id == 'true':
            return self.extract(TOK_BOOL)
        if id == 'false':
            return self.extract(TOK_BOOL)

        return self.extract(TOK_ID)

    def getString(self):
        quote = self.src[self.forward]
        token = ''
        self.forward += 1
        try:
            while not self.isEOF() and self.src[self.forward] != quote:
                if self.src[self.forward] == '\\':
                    self.forward += 1
                    if isLineTerm(self.src[self.forward]):
                        self.forward += 1
                    else:
                        token += self.getEscapeSeq()
                else:
                    token += self.src[self.forward]
                    self.forward += 1
            if not self.isEOF() and self.src[self.forward] == quote:
                self.forward += 1
                return TOK_STRING, token
        except:
            pass
        return self.extract(TOK_ERROR)

    def getEscapeSeq(self):
        if not self.isEOF():
            #single escape character
            if self.src[self.forward] in SINGLE_CHARACTER_ESC_SEQ:
                self.forward += 1
                return SINGLE_CHARACTER_ESC_SEQ[self.src[self.forward - 1]]
            if not isLineTerm(self.src[self.forward]) and not self.src[self.forward].isnumeric() and not self.src[self.forward] in 'xu':
                self.forward += 1
                return self.src[self.forward - 1]
            if self.src[self.forward] == 'u':
                if isHexDigit(self.src[self.forward + 1]) and isHexDigit(self.src[self.forward + 2]) and isHexDigit(
                    self.src[self.forward + 1]) and isHexDigit(self.src[self.forward + 2]):
                    code = 4096 * int(self.src[self.forward + 1]) + 256 * int(self.src[self.forward + 2]) + 16 * int(
                        self.src[self.forward + 3]) + int(self.src[self.forward + 4])
                    self.forward += 5
                    return chr(code)
            if self.src[self.forward] == 'x':
                if isHexDigit(self.src[self.forward + 1]) and isHexDigit(self.src[self.forward + 2]):
                    code = 16 * int(self.src[self.forward + 1]) + int(self.src[self.forward + 2])
                    self.forward += 3
                    return chr(code)
            if self.src[self.forward] == '0' and self.forward < len(self.src) - 1 and not self.src[self.forward + 1].isdigit():
                self.forward += 1
                return '\0'

        raise Exception('error parsing string escape sequence')

    def getRegExp(self):
        #RegularExpressionFirstChar
        if not isLineTerm(self.src[self.forward]) and not self.src[self.forward] in '*\\/[':
            self.forward += 1
        elif self.src[self.forward] == '\\':
            self.forward += 1
            if isLineTerm(self.src[self.forward]):
                return self.extract(TOK_ERROR)
            self.forward += 1
        elif self.src[self.forward] == '[':
            self.getRegExpClass()
        else:
            return self.extract(TOK_ERROR)
            #RegularExpressionChars

        while self.src[self.forward] != '/':
            if not isLineTerm(self.src[self.forward]) and not self.src[self.forward] in '\\/[':
                self.forward += 1
            elif self.src[self.forward] == '\\':
                self.forward += 1
                if isLineTerm(self.src[self.forward]):
                    return self.extract(TOK_ERROR)
                self.forward += 1
            elif self.src[self.forward] == '[':
                self.getRegExpClass()
            else:
                return self.extract(TOK_ERROR)

        self.forward += 1

        #RegularExpressionFlags
        while self.forward < len(self.src) and isIDPart(self.src[self.forward]):
            self.forward += 1
        return self.extract(TOK_REGEXP)


    def getRegExpClass(self):
        self.forward += 1
        while self.src[self.forward] != ']':
            if self.src[self.forward] == '\\':
                self.forward += 1
                if isLineTerm(self.src[self.forward]):
                    raise Exception('Error parsing RegExp class - unsuspected LineTerminator')
                self.forward += 1
            elif not isLineTerm(self.src[self.forward]) and not self.src[self.forward] in ']\\':
                self.forward += 1
            else:
                raise Exception('Error parsing RegExp')
        self.forward += 1
