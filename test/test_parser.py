import unittest
import AST
from JSParser import Parser

__author__ = 'Robur'



class ParserTestCase(unittest.TestCase):
    def testEmptyProgram(self):
        parser = Parser()
        parser.src = ''
        parser.buildAST()

        self.assertIsNotNone(parser.ASTRoot, 'creation of tree root')
        self.assertEqual(type(parser.ASTRoot), AST.ProgramNode)

    def testEmptyFunctionDeclaration(self):
        parser = Parser()
        parser.src = 'function name1() {}'
        parser.buildAST()

        self.assertEqual(len(parser.ASTRoot.sourceElements),1)
        self.assertEqual(type(parser.ASTRoot.sourceElements[0]), AST.FunctionDeclaration)
        self.assertEqual(parser.ASTRoot.sourceElements[0].name, 'name1')

    def testArgumentsFunctionDeclaration(self):
        parser = Parser()
        parser.src = 'function asd(aa,a23) {}'
        parser.buildAST()

        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(len(node.arguments),2)
        self.assertEqual(node.arguments[0],'aa')
        self.assertEqual(node.arguments[1],'a23')

    def testFunctionDeclarationAsBodyOfFunctionDeclaration(self):
        parser = Parser()
        parser.src = 'function outer(asd) {\
        function tt() {}\
        }'

        parser.buildAST()

        node = parser.ASTRoot.sourceElements[0]

        self.assertEqual(len(node.sourceElements),1)

    def testParseProgramAsBlockStatements(self):
        parser = Parser()
        parser.src = '{}'

        parser.buildAST()

        self.assertEqual(len(parser.ASTRoot.sourceElements),1)
        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(type(node), AST.Block)
        parser.src = '{}{}'

        parser.buildAST()

        self.assertEqual(len(parser.ASTRoot.sourceElements),2)
        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(type(node), AST.Block)
        node = parser.ASTRoot.sourceElements[1]
        self.assertEqual(type(node), AST.Block)

    def testParseBlockStatementInFunctionBody(self):
        parser = Parser()
        parser.src = 'function a(){ {} }'

        parser.buildAST()
        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(type(node.sourceElements[0]), AST.Block)

    def testParseVariableStatement(self):
        parser = Parser()
        parser.src = 'var x;'

        parser.buildAST()
        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(type(node), AST.VariableStatement)
        self.assertEqual(node.declarations[0].id,'x')



