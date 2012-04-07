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
    return c == '\n'


def isIDStart(c):
    return c.isalpha() or c in '_$'


def isIDPart(c):
    return isIDStart(c) or c.isnumeric()


def isWS(c):
    return c in ' \t\n\r\f\v'


class Lexer:
    def __init__(self):
        self.state = 0
        self.src = ''
        self.pointer = -1
        self.forward = -1
        self.eof = False
        self.strictMode = False

    def setSrc(self, js):
        self.src = js
        self.pointer = 0
        self.forward = 0
        self.eof = False

    def getNext(self, REMode = False):
        try:
            if self.forward >= len(self.src):
                return TOK_EOF, ''
            self.pointer = self.forward
            if isWS(self.src[self.forward]):
                self.forward += 1
                return TOK_WS, ''

            if self.src[self.forward] == '/':
                self.forward += 1
                if self.src[self.forward] == '/':
                    return self.getSingleComment()
                if self.src[self.forward] == '*':
                    return self.getMultiComment()

                if REMode:
                    return self.getRegExp()
                else:
                    if self.forward < len(self.src) and self.src[self.forward] == '=':
                        self.forward += 1
                    return TOK_DIV_PUNCTUATOR, self.src[self.pointer:self.forward]

            if isIDStart(self.src[self.forward]):
                self.forward += 1
                while self.forward < len(self.src) and isIDPart(self.src[self.forward]):
                    self.forward += 1
                return self.getIDOrReserved()

            if self.src[self.forward] == '0':
                self.forward += 1
                if self.forward < len(self.src) and self.src[self.forward] == '.':
                    self.forward += 1
                    return self.getNumericAfterDot()
                    #hex digits
                if self.forward < len(self.src) and self.src[self.forward] in 'xX':
                    self.forward += 1
                    if isHexDigit(self.src[self.forward]):
                        while self.forward < len(self.src) and (self.src[self.forward].isdigit() or self.src[self.forward].lower() in 'abcdef'):
                            self.forward += 1
                        return self.extractNumeric()
                    raise Exception('Illegal')
                return self.extractNumeric()

            if self.src[self.forward].isnumeric() and self.src[self.forward] != '0':
                self.forward += 1
                while self.forward < len(self.src) and self.src[self.forward].isdigit():
                    self.forward += 1
                if self.forward < len(self.src) and self.src[self.forward] == '.':
                    self.forward += 1
                    return self.getNumericAfterDot()
                if self.forward < len(self.src) and self.src[self.forward] in 'eE':
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
                    return TOK_PUNCTUATOR, self.src[self.pointer:self.forward]

            #string literals
            if self.src[self.forward] in ['"', "'"]:
                return self.getString()
            self.forward += 1
        except:
            pass
        return TOK_UNKNOWN, self.src[self.pointer: self.forward]


    def getMultiComment(self):
        state = 2
        nl = False
        self.forward += 1
        while self.forward < len(self.src):
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
        while self.forward < len(self.src) and not isLineTerm(self.src[self.forward]):
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
        token = self.getNext()
        while token[0] == TOK_SINGLE_COMMENT or token[0] == TOK_MULTI_COMMENT or token[0] == TOK_WS:
            token = self.getNext(true)
        if token[0] == TOK_MULTINL_COMMENT:
            return TOK_NL, ''
        return token

    def extractNumeric(self):
        if self.forward < len(self.src) and isIDStart(self.src[self.forward]):
            return TOK_ERROR, self.src[self.pointer:self.forward]
        return TOK_NUMERIC, self.src[self.pointer:self.forward]

    def getNumericAfterDot(self):
        while self.forward < len(self.src) and self.src[self.forward].isnumeric():
            self.forward += 1
        if self.forward < len(self.src) and self.src[self.forward] in 'eE':
            self.forward += 1
            return self.getNumericExp()
        return self.extractNumeric()


    def getNumericExp(self):
        if self.src[self.forward] in '+-':
            self.forward += 1
        if self.src[self.forward].isnumeric():
            while self.forward < len(self.src) and self.src[self.forward].isnumeric():
                self.forward += 1
            return self.extractNumeric()
        return TOK_UNKNOWN, ''

    def getIDOrReserved(self):
        id = self.src[self.pointer: self.forward]
        if id in RESERVED_WORDS:
            return TOK_RESERVED, self.src[self.pointer: self.forward]

        if id in FUTURE_RESERVED_WORDS:
            return TOK_FUTURE_RESERVED, self.src[self.pointer: self.forward]

        if self.strictMode and id in FUTURE_STRICT_RESERVED_WORDS:
            return TOK_FUTURE_RESERVED, self.src[self.pointer: self.forward]

        if id == 'null':
            return TOK_NULL, self.src[self.pointer: self.forward]

        if id == 'true':
            return TOK_BOOL, self.src[self.pointer: self.forward]
        if id == 'false':
            return TOK_BOOL, self.src[self.pointer: self.forward]

        return TOK_ID, self.src[self.pointer: self.forward]

    def getString(self):
        quote = self.src[self.forward]
        token = ''
        self.forward += 1
        try:
            while self.forward < len(self.src) and self.src[self.forward] != quote:
                if self.src[self.forward] == '\\':
                    self.forward += 1
                    if isLineTerm(self.src[self.forward]):
                        self.forward += 1
                    else:
                        token += self.getEscapeSeq()
                else:
                    token += self.src[self.forward]
                    self.forward += 1
            if self.forward < len(self.src) and self.src[self.forward] == quote:
                self.forward += 1
                return TOK_STRING, token
        except:
            pass
        return TOK_ERROR, self.src[self.pointer:self.forward]

    def getEscapeSeq(self):
        if self.forward < len(self.src):
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