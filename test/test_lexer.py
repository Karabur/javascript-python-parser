__author__ = 'Robur'

import unittest, lexer

class LexerTestCase(unittest.TestCase):
    def testRawComment(self):
        lex = lexer.Lexer()

        lex.setSrc('//sdfsdff\n//asdasd')
        self.assertEqual(lex.getNext(), (lexer.TOK_SINGLE_COMMENT,'sdfsdff'))
        lex.getNext()
        self.assertEqual(lex.getNext(), (lexer.TOK_SINGLE_COMMENT,'asdasd'))

        lex.setSrc("""//sdfdff
        ttttt""")
        self.assertEqual(lex.getNext(), (lexer.TOK_SINGLE_COMMENT,'sdfdff'))

        lex.setSrc('/*asdasd*/')
        self.assertEqual(lex.getNext(), (lexer.TOK_MULTI_COMMENT, 'asdasd'))

        lex.setSrc('/*asd\nasd*/123123')
        self.assertEqual(lex.getNext(), (lexer.TOK_MULTINL_COMMENT, 'asd\nasd'))

    def testCommentToken(self):
        lex = lexer.Lexer()

        lex.setSrc('//asdasd')
        self.assertEqual(lex.getToken(), (lexer.TOK_EOF, ''))

        lex.setSrc('//')
        self.assertEqual(lex.getToken(), (lexer.TOK_EOF, ''))

    def testID(self):
        lex = lexer.Lexer()

        lex.setSrc('aA$34_a bdd')
        self.assertEqual(lex.getToken(), (lexer.TOK_ID, 'aA$34_a'))
        self.assertEqual(lex.getToken(), (lexer.TOK_ID, 'bdd'))

    def testWhitespaceSkipping(self):
        lex = lexer.Lexer()
        lex.setSrc(" \t  \v  ")
        self.assertEqual(lex.getToken(), (lexer.TOK_EOF , ''))

    def testZeroNumber(self):
        lex = lexer.Lexer()
        lex.setSrc("0")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '0'))

    def testSimpleNumber(self):
        lex = lexer.Lexer()
        lex.setSrc("3213")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '3213'))

    def testFloatNumbers(self):
        lex = lexer.Lexer()
        lex.setSrc("22.34 .232")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '22.34'))
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '.232'))
        lex.setSrc("0. 0.3")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '0.'))
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '0.3'))
        lex.setSrc("22. 44.")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '22.'))
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '44.'))

    def testExponentialNumbers(self):
        lex = lexer.Lexer()
        lex.setSrc("22e3 22.34e33 .232E23")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '22e3'))
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '22.34e33'))
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '.232E23'))
        lex.setSrc("22.34e-33 .232E+23")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '22.34e-33'))
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '.232E+23'))
        lex.setSrc("0.e+0")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '0.e+0'))

    def testHexNumbers(self):
        lex = lexer.Lexer()
        lex.setSrc("0x233aD")
        self.assertEqual(lex.getToken(), (lexer.TOK_NUMERIC , '0x233aD'))

    def testNotIDStartAfterNumeric(self):
        lex = lexer.Lexer()
        lex.setSrc("0.233a")
        self.assertEqual(lex.getToken(), (lexer.TOK_ERROR , '0.233'))
        lex.setSrc("233b")
        self.assertEqual(lex.getToken(), (lexer.TOK_ERROR , '233'))
        lex.setSrc("0x233br")
        self.assertEqual(lex.getToken(), (lexer.TOK_ERROR , '0x233b'))

    def testReservedWords(self):
        lex = lexer.Lexer()
        rw = ['break','do','instanceof','typeof','case','else','new','var','catch','finally','return','void','continue','for','switch','while','debugger','function','this','with','default','if','throw','delete','in','try']
        lex.setSrc(' '.join(rw))
        for w in rw:
            self.assertEqual(lex.getToken(), (lexer.TOK_RESERVED , w))

    def testFutureReservedWords(self):
        lex = lexer.Lexer()
        rw = ['class','enum','extends','super','const','export','import']
        lex.setSrc(' '.join(rw))
        for w in rw:
            self.assertEqual(lex.getToken(), (lexer.TOK_FUTURE_RESERVED , w))
    def testFutureStrictReservedWords(self):
        lex = lexer.Lexer()
        rw = ['implements','let','private','public','yield','interface','package','protected','static']
        lex.strictMode = True
        lex.setSrc('  '.join(rw))
        for w in rw:
            self.assertEqual(lex.getToken(), (lexer.TOK_FUTURE_RESERVED , w))
        lex.strictMode = False
        lex.setSrc(' '.join(rw))
        for w in rw:
            self.assertEqual(lex.getToken(), (lexer.TOK_ID , w))

    def testPunctuator(self):
        lex = lexer.Lexer()
        ps = ['^=','{','}','(',')','[',']','.',';',',','<','>','<=','>=','==','!=','===','!==','+','-','*','%','++','--','<<','>>','>>>','&','|','^','!','~','&&','||','?',':','=','+=','-=','*=','%=','<<=','>>=','>>>=','&=','|=','^=']
        lex.setSrc(' '.join(ps))
        for p in ps:
            self.assertEqual(lex.getToken(), (lexer.TOK_PUNCTUATOR , p))

    def testNull(self):
        lex = lexer.Lexer()
        lex.setSrc('null null')
        self.assertEqual(lex.getToken(), (lexer.TOK_NULL, 'null'))
        self.assertEqual(lex.getToken(), (lexer.TOK_NULL, 'null'))

    def testBool(self):
        lex = lexer.Lexer()
        lex.setSrc('true false')
        self.assertEqual(lex.getToken(), (lexer.TOK_BOOL, 'true'))
        self.assertEqual(lex.getToken(), (lexer.TOK_BOOL, 'false'))

    def testStringLiteral(self):
        lex = lexer.Lexer()
        lex.setSrc('"asdasd" "ss\\"" \'\\s\'')
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, 'asdasd'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, 'ss"'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, 's'))

        lex.setSrc('"\\\\" "\\\'" "\\"" "\\b" "\\t" "\\n" "\\v" "\\f" "\\r"')

        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\\'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\''))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '"'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\b'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\t'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\n'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\v'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\f'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\r'))

        lex.setSrc('"asd\\\ndd"')
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, 'asddd'))

        lex.setSrc('"dd\\u2345" \'"s\\x34\'')
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, 'dd\u2345'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '"s\x34'))

        lex.setSrc("'\\0' '\\0a'")
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\0'))
        self.assertEqual(lex.getToken(), (lexer.TOK_STRING, '\0a'))

    def testRegExp(self):
        lex=lexer.Lexer()
        lex.setSrc('/asddd/iuy')
#        self.assertEqual(lex.getRegExpToken(), (lexer.TOK_REGEXP,'/asddd/iuy'))

    def testDivPunctuator(self):
        lex=lexer.Lexer()
        lex.setSrc('asd/333/=')
        lex.getToken()
        self.assertEqual(lex.getToken(), (lexer.TOK_DIV_PUNCTUATOR,'/'))
        lex.getToken()
        self.assertEqual(lex.getToken(), (lexer.TOK_DIV_PUNCTUATOR,'/='))


