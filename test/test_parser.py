import unittest
import AST
from JSParser import Parser

__author__ = 'Robur'



class ParserTestCase(unittest.TestCase):
    def test01EmptyProgram(self):
        parser = Parser()
        parser.src = ''
        parser.buildAST()

        self.assertIsNotNone(parser.ASTRoot, 'creation of tree root')
        self.assertEqual(type(parser.ASTRoot), AST.ProgramNode)

    def test02EmptyFunctionDeclaration(self):
        parser = Parser()
        parser.src = 'function name1() {}'
        parser.buildAST()

        self.assertEqual(len(parser.ASTRoot.sourceElements),1)
        self.assertEqual(type(parser.ASTRoot.sourceElements[0]), AST.FunctionDeclaration)
        self.assertEqual(parser.ASTRoot.sourceElements[0].name, 'name1')
        self.assertEqual(parser.ASTRoot.sourceElements[0].parent, parser.ASTRoot)

    def test03ArgumentsFunctionDeclaration(self):
        parser = Parser()
        parser.src = 'function asd(aa,a23) {}'
        parser.buildAST()

        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(len(node.arguments),2)
        self.assertEqual(node.arguments[0],'aa')
        self.assertEqual(node.arguments[1],'a23')

    def test04FunctionDeclarationAsBodyOfFunctionDeclaration(self):
        parser = Parser()
        parser.src = 'function outer(asd) {\
        function tt() {}\
        }'

        parser.buildAST()

        node = parser.ASTRoot.sourceElements[0]

        self.assertEqual(len(node.sourceElements),1)

    def test05ParseProgramAsBlockStatements(self):
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

    def test06ParseBlockStatementInFunctionBody(self):
        parser = Parser()
        parser.src = 'function a(){ {} }'

        parser.buildAST()
        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(type(node.sourceElements[0]), AST.Block)

    def test07ParseVariableStatement(self):
        parser = Parser()
        parser.src = 'var x;'
        parser.buildAST()
        node = parser.ASTRoot.sourceElements[0]
        self.assertEqual(type(node), AST.VariableStatement)
        self.assertEqual(node.declarations[0].id,'x')

#        parser.src = 'var x=1;'
#        parser.buildAST()
#        node = parser.ASTRoot.sourceElements[0]
#        self.assertEqual(type(node), AST.VariableStatement)
#        self.assertEqual(node.declarations[0].initializer,'x')

    def test08ParseLeftHandSideExpression(self):
        parser = Parser()
        parser.src = 'a 1'
        parser.reset()
        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.Identifier)
        self.assertEqual(node.name, 'a')

        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.Number)
        self.assertEqual(node.value, '1')


    def test09ParseCallLeftHandSideExpression(self):
        parser = Parser()
        parser.src = 'b() c()() d(1)(2,a) '
        parser.reset()

        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.Call)
        self.assertEqual(type(node.expr), AST.Identifier)
        self.assertEqual(node.expr.name, 'b')

        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.Call)
        self.assertEqual(type(node.expr), AST.Call)
        self.assertEqual(node.expr.expr.name, 'c')

        node = parser.parseLeftHandSideExpression()
        self.assertEqual(len(node.expr.args), 1)
        self.assertEqual(type(node.expr.args[0]), AST.Number)
        self.assertEqual(node.expr.args[0].value, '1')

        self.assertEqual(len(node.args), 2)
        self.assertEqual(type(node.args[0]), AST.Number)
        self.assertEqual(type(node.args[1]), AST.Identifier)
        self.assertEqual(node.args[0].value, '2')
        self.assertEqual(node.args[1].name, 'a')

        parser.src = 'new a()    new new b(a)(23,3)(12,c,b)'
        parser.reset()
        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.New)
        self.assertEqual(type(node.expr), AST.Identifier)
        self.assertEqual(node.expr.name, 'a')
        self.assertEqual(node.args, [])

        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.Call)
        self.assertEqual(len(node.args), 3)
        self.assertEqual(type(node.expr), AST.New)
        self.assertEqual(len(node.expr.args), 2)
        self.assertEqual(type(node.expr.expr), AST.New)
        self.assertEqual(len(node.expr.expr.args), 1)
        self.assertEqual(node.expr.expr.args[0].name, 'a')



    def test10PrimaryExpression(self):
        parser = Parser()
        parser.src = 'this asd false true null [] [1,a,,3]'
        parser.reset()

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.This)

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.Identifier)

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.Literal)
        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.Literal)
        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.Literal)

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.Array)

        node = parser.parsePrimaryExpression()
        self.assertEqual(len(node.items), 4)
        self.assertEqual(node.items[0].value, '1')
        self.assertEqual(node.items[1].name, 'a')
        self.assertEqual(type(node.items[2]), AST.HoleLiteral)

        parser.src ='{} {a:1} {a:1,b:a,1:2} {get a() {var a=1;},set "asd"(val) {}, set a(value) {}}'
        parser.reset()

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.ObjectLiteral)

        node = parser.parsePrimaryExpression()
        self.assertEqual(len(node.properties), 1)
        self.assertEqual(type(node.properties[0]), AST.ObjectProperty)
        self.assertEqual(node.properties[0].key, 'a')
        self.assertEqual(node.properties[0].value.value, '1')

        node = parser.parsePrimaryExpression()
        self.assertEqual(len(node.properties), 3)
        self.assertEqual(node.properties[1].key, 'b')
        self.assertEqual(node.properties[1].value.name, 'a')
        self.assertEqual(node.properties[2].key, '1')
        self.assertEqual(node.properties[2].value.value, '2')

        node = parser.parsePrimaryExpression()
        self.assertEqual(len(node.properties), 2)
        self.assertEqual(type(node.properties[0]), AST.ObjectGetSetProperty)
        self.assertEqual(len(node.properties[0].getterBody), 1)
        self.assertEqual(type(node.properties[0].setterBody), list)
        self.assertEqual(node.properties[0].paramName, 'value')
        self.assertEqual(node.properties[0].key, 'a')

        self.assertEqual(type(node.properties[1]), AST.ObjectGetSetProperty)
        self.assertEqual(node.properties[1].key, 'asd')
        self.assertEqual(node.properties[1].getterBody, None)
        self.assertEqual(type(node.properties[1].setterBody), list)
        self.assertEqual(node.properties[1].paramName, 'val')


        parser.src = '({}) ([],{},asd)'
        parser.reset()

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.ObjectLiteral)

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.BinaryExpression)
        self.assertEqual(type(node.right), AST.Identifier)
        self.assertEqual(node.op, ',')
        self.assertEqual(type(node.left), AST.BinaryExpression)
        self.assertEqual(type(node.left.left), AST.Array)
        self.assertEqual(type(node.left.right), AST.ObjectLiteral)



