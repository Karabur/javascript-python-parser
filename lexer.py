#tokens

TOK_NL = 1
TOK_SINGLE_COMMENT = 2
TOK_MULTI_COMMENT = 3
TOK_MULTINL_COMMENT = 4
TOK_ID = 5
TOK_NUMERIC = 6
TOK_WS = 7

TOK_UNKNOWN = 999
TOK_EOF = 1000


def isLineTerm(c):
    return c == '\n'


def isIDStart(c):
    return c.isalpha() or c in'_$'


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

    def setSrc(self, js):
        self.src = js
        self.pointer = 0
        self.forward = 0
        self.eof = False

    def getNext(self):
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

        if isIDStart(self.src[self.forward]):
            self.forward += 1
            while isIDPart(self.src[self.forward]):
                self.forward += 1
            return TOK_ID, self.src[self.pointer: self.forward]

        self.forward += 1
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
        while token[0] == TOK_SINGLE_COMMENT or token[0] == TOK_MULTI_COMMENT or token[0]==TOK_WS:
            token = self.getNext()
        if token[0] == TOK_MULTINL_COMMENT:
            return TOK_NL, ''
        return token
