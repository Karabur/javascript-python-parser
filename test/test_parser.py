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

    def testEmptyFunctionDefinition(self):
        parser = JSParser.Parser()
        parser.src = 'function name1() {}'
        parser.buildAST()

        self.assertEqual(len(parser.ASTRoot.sourceElements),1)
        self.assertEqual(type(parser.ASTRoot.sourceElements[0]), AST.FunctionDeclaration)
        self.assertEqual(parser.ASTRoot.sourceElements[0].name, 'name1')

    def testArgumentsFunctionDefinition(self):
        parser = JSParser.Parser()
        parser.src = 'function asd(aa,a23) {}'
        parser.buildAST()

        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(len(node.arguments),2)
        self.assertEqual(node.arguments[0],'aa')
        self.assertEqual(node.arguments[1],'a23')

