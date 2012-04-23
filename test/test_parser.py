import unittest, JSParser
import AST

__author__ = 'Robur'



class ParserTestCase(unittest.TestCase):
    def testEmptyProgram(self):
        parser = JSParser.Parser()
        parser.src = ''
        parser.buildAST()

        self.assertIsNotNone(parser.ASTRoot, 'creation of tree root')
        self.assertEqual(type(parser.ASTRoot), AST.ProgramNode)


