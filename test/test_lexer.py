__author__ = 'Robur'

import unittest
from JSLexer import TOK, Lexer

class LexerTestCase(unittest.TestCase):
    def testRawComment(self):
        lex = Lexer()

        lex.setSrc('//sdfsdff\n//asdasd')
        self.assertEqual(lex.getNext(), (TOK.SINGLE_COMMENT,'sdfsdff'))
        lex.getNext()
        self.assertEqual(lex.getNext(), (TOK.SINGLE_COMMENT,'asdasd'))

        lex.setSrc("""//sdfdff
        ttttt""")
        self.assertEqual(lex.getNext(), (TOK.SINGLE_COMMENT,'sdfdff'))

        lex.setSrc('/*asdasd*/')
        self.assertEqual(lex.getNext(), (TOK.MULTI_COMMENT, 'asdasd'))

        lex.setSrc('/*asd\nasd*/123123')
        self.assertEqual(lex.getNext(), (TOK.MULTINL_COMMENT, 'asd\nasd'))

    def testCommentToken(self):
        lex = Lexer()

        lex.setSrc('//asdasd')
        self.assertEqual(lex.getToken(), (TOK.EOF, ''))

        lex.setSrc('//')
        self.assertEqual(lex.getToken(), (TOK.EOF, ''))

    def testID(self):
        lex = Lexer()

        lex.setSrc('aA$34_a bdd')
        self.assertEqual(lex.getToken(), (TOK.ID, 'aA$34_a'))
        self.assertEqual(lex.getToken(), (TOK.ID, 'bdd'))

    def testWhitespaceSkipping(self):
        lex = Lexer()
        lex.setSrc(" \t  \v  ")
        self.assertEqual(lex.getToken(), (TOK.EOF , ''))

    def testZeroNumber(self):
        lex = Lexer()
        lex.setSrc("0")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '0'))

    def testSimpleNumber(self):
        lex = Lexer()
        lex.setSrc("3213")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '3213'))

    def testFloatNumbers(self):
        lex = Lexer()
        lex.setSrc("22.34 .232")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '22.34'))
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '.232'))
        lex.setSrc("0. 0.3")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '0.'))
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '0.3'))
        lex.setSrc("22. 44.")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '22.'))
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '44.'))

    def testExponentialNumbers(self):
        lex = Lexer()
        lex.setSrc("22e3 22.34e33 .232E23")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '22e3'))
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '22.34e33'))
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '.232E23'))
        lex.setSrc("22.34e-33 .232E+23")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '22.34e-33'))
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '.232E+23'))
        lex.setSrc("0.e+0")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '0.e+0'))

    def testHexNumbers(self):
        lex = Lexer()
        lex.setSrc("0x233aD")
        self.assertEqual(lex.getToken(), (TOK.NUMERIC , '0x233aD'))

    def testNotIDStartAfterNumeric(self):
        lex = Lexer()
        lex.setSrc("0.233a")
        self.assertEqual(lex.getToken(), (TOK.ERROR , '0.233'))
        lex.setSrc("233b")
        self.assertEqual(lex.getToken(), (TOK.ERROR , '233'))
        lex.setSrc("0x233br")
        self.assertEqual(lex.getToken(), (TOK.ERROR , '0x233b'))

    def testReservedWords(self):
        lex = Lexer()
        rw = ['break','do','instanceof','typeof','case','else','new','var','catch','finally','return','void','continue','for','switch','while','debugger','function','this','with','default','if','throw','delete','in','try']
        lex.setSrc(' '.join(rw))
        for w in rw:
            self.assertEqual(lex.getToken(), (TOK.RESERVED , w))

    def testFutureReservedWords(self):
        lex = Lexer()
        rw = ['class','enum','extends','super','const','export','import']
        lex.setSrc(' '.join(rw))
        for w in rw:
            self.assertEqual(lex.getToken(), (TOK.FUTURE_RESERVED , w))
    def testFutureStrictReservedWords(self):
        lex = Lexer()
        rw = ['implements','let','private','public','yield','interface','package','protected','static']
        lex.strictMode = True
        lex.setSrc('  '.join(rw))
        for w in rw:
            self.assertEqual(lex.getToken(), (TOK.FUTURE_RESERVED , w))
        lex.strictMode = False
        lex.setSrc(' '.join(rw))
        for w in rw:
            self.assertEqual(lex.getToken(), (TOK.ID , w))

    def testPunctuator(self):
        lex = Lexer()
        ps = ['^=','{','}','(',')','[',']','.',';',',','<','>','<=','>=','==','!=','===','!==','+','-','*','%','++','--','<<','>>','>>>','&','|','^','!','~','&&','||','?',':','=','+=','-=','*=','%=','<<=','>>=','>>>=','&=','|=','^=']
        lex.setSrc(' '.join(ps))
        for p in ps:
            self.assertEqual(lex.getToken(), (TOK.PUNCTUATOR , p))

    def testNull(self):
        lex = Lexer()
        lex.setSrc('null null')
        self.assertEqual(lex.getToken(), (TOK.NULL, 'null'))
        self.assertEqual(lex.getToken(), (TOK.NULL, 'null'))

    def testBool(self):
        lex = Lexer()
        lex.setSrc('true false')
        self.assertEqual(lex.getToken(), (TOK.BOOL, 'true'))
        self.assertEqual(lex.getToken(), (TOK.BOOL, 'false'))

    def testStringLiteral(self):
        lex = Lexer()
        lex.setSrc('"asdasd" "ss\\"" \'\\s\'')
        self.assertEqual(lex.getToken(), (TOK.STRING, 'asdasd'))
        self.assertEqual(lex.getToken(), (TOK.STRING, 'ss"'))
        self.assertEqual(lex.getToken(), (TOK.STRING, 's'))

        lex.setSrc('"\\\\" "\\\'" "\\"" "\\b" "\\t" "\\n" "\\v" "\\f" "\\r"')

        self.assertEqual(lex.getToken(), (TOK.STRING, '\\'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '\''))
        self.assertEqual(lex.getToken(), (TOK.STRING, '"'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '\b'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '\t'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '\n'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '\v'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '\f'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '\r'))

        lex.setSrc('"asd\\\ndd"')
        self.assertEqual(lex.getToken(), (TOK.STRING, 'asddd'))

        lex.setSrc('"dd\\u2345" \'"s\\x34\'')
        self.assertEqual(lex.getToken(), (TOK.STRING, 'dd\u2345'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '"s\x34'))

        lex.setSrc("'\\0' '\\0a'")
        self.assertEqual(lex.getToken(), (TOK.STRING, '\0'))
        self.assertEqual(lex.getToken(), (TOK.STRING, '\0a'))

    def testRegExp(self):
        lex=Lexer()
        lex.setSrc('asd/asddd/iuy')
        lex.getToken()
        self.assertEqual(lex.getToken(), (TOK.REGEXP,'/asddd/iuy'))
        lex.setSrc('/asddd/')
        self.assertEqual(lex.getToken(), (TOK.REGEXP,'/asddd/'))
        lex.setSrc('/\\dasddd/')
        self.assertEqual(lex.getToken(), (TOK.REGEXP,'/\\dasddd/'))
        lex.setSrc('/[asd\\sdd](e)?:(1)+[a-z,1-9]asddd/')
        self.assertEqual(lex.getToken(), (TOK.REGEXP,'/[asd\\sdd](e)?:(1)+[a-z,1-9]asddd/'))

    def testDivPunctuator(self):
        lex=Lexer()
        lex.setSrc('asd/333/=')
        lex.getToken()
        self.assertEqual(lex.getToken(False), (TOK.DIV_PUNCTUATOR,'/'))
        lex.getToken()
        self.assertEqual(lex.getToken(False), (TOK.DIV_PUNCTUATOR,'/='))


