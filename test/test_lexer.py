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

        lex.setSrc('aA$34_a 33')
        self.assertEqual(lex.getToken(), (lexer.TOK_ID, 'aA$34_a'))

    def testWhitespaceSkipping(self):
        lex = lexer.Lexer()
        lex.setSrc(" \t  \v  ")
        self.assertEqual(lex.getToken(), (lexer.TOK_EOF , ''))

