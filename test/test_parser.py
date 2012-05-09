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

        parser.src = 'a[1] asd[b]'
        parser.reset()
        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.Property)
        self.assertEqual(node.object.name, 'a')
        self.assertEqual(node.property.value, '1')
        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.Property)
        self.assertEqual(node.object.name, 'asd')
        self.assertEqual(node.property.name, 'b')

        parser.src = 'a.b.c'
        parser.reset()
        node = parser.parseLeftHandSideExpression()
        self.assertEqual(type(node), AST.Property)
        self.assertEqual(node.property.name, 'c')
        self.assertEqual(node.object.property.name, 'b')
        self.assertEqual(node.object.object.name, 'a')


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
        parser.src = 'this asd false true null /asd/i [] [1,a,,3]'
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
        self.assertEqual(type(node), AST.Literal)
        self.assertEqual(node.value, '/asd/i')

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

    def test11LTLookAhead(self):
        parser = Parser()
        parser.src = 'asd eee\nddd\n'
        parser.reset()

        self.assertEqual(parser.lookup()[1], 'asd')
        parser.nextToken()
        self.assertEqual(parser.LTAhead(), False)
        parser.nextToken()
        self.assertEqual(parser.lookup()[1], 'ddd')
        self.assertEqual(parser.LTAhead(), True)
        parser.nextToken()
        self.assertEqual(parser.LTAhead(), True)

    def test12PostfixExpression(self):
        parser = Parser()
        parser.src='a ++ b-- c\n++'
        parser.reset()

        node = parser.parsePostfixExpression()
        self.assertEqual(type(node), AST.PostfixExpression)
        self.assertEqual(node.expr.name, 'a')
        self.assertEqual(node.op, '++')

        node = parser.parsePostfixExpression()
        self.assertEqual(node.expr.name, 'b')
        self.assertEqual(node.op, '--')

        node = parser.parsePostfixExpression()
        self.assertEqual(type(node), AST.Identifier)
        self.assertEqual(node.name, 'c')

        self.assertEqual(parser.nextToken()[1],'++')

    def test13UnaryExpression(self):
        parser = Parser()
        parser.src = 'a++ delete c void d typeof e\n ++f \n --g +h -i ~j !k'
        parser.reset()

        node = parser.parseUnaryExpression()
        self.assertEqual(type(node), AST.PostfixExpression)

        node = parser.parseUnaryExpression()
        self.assertEqual(type(node), AST.UnaryExpression)
        self.assertEqual(node.expr.name, 'c')
        self.assertEqual(node.op, 'delete')

        node = parser.parseUnaryExpression()
        self.assertEqual(node.expr.name, 'd')
        self.assertEqual(node.op, 'void')

        node = parser.parseUnaryExpression()
        self.assertEqual(node.expr.name, 'e')
        self.assertEqual(node.op, 'typeof')

        node = parser.parseUnaryExpression()
        self.assertEqual(node.expr.name, 'f')
        self.assertEqual(node.op, '++')

        node = parser.parseUnaryExpression()
        self.assertEqual(node.expr.name, 'g')
        self.assertEqual(node.op, '--')

        node = parser.parseUnaryExpression()
        self.assertEqual(node.expr.name, 'h')
        self.assertEqual(node.op, '+')

        node = parser.parseUnaryExpression()
        self.assertEqual(node.expr.name, 'i')
        self.assertEqual(node.op, '-')

        node = parser.parseUnaryExpression()
        self.assertEqual(node.expr.name, 'j')
        self.assertEqual(node.op, '~')

        node = parser.parseUnaryExpression()
        self.assertEqual(node.expr.name, 'k')
        self.assertEqual(node.op, '!')


    def test14parseBinaryExpression(self):
        parser = Parser()

        parser.src = '1/2'
        parser.reset()

        node = parser.parseBinaryExpression()
        self.assertEqual(type(node), AST.BinaryExpression)
        self.assertEqual(node.left.value , '1')
        self.assertEqual(node.right.value, '2')
        self.assertEqual(node.op, '/')

        parser.src = 'a<<1>c>>d'
        parser.reset()

        node = parser.parseBinaryExpression()
        self.assertEqual(type(node.left), AST.BinaryExpression)
        self.assertEqual(type(node.right), AST.BinaryExpression)
        self.assertEqual(node.op, '>')
        self.assertEqual(node.left.op, '<<')
        self.assertEqual(node.left.left.name, 'a')
        self.assertEqual(node.left.right.value, '1')
        self.assertEqual(node.right.op, '>>')
        self.assertEqual(node.right.left.name, 'c')
        self.assertEqual(node.right.right.name, 'd')

        parser.src = 'a != b in c &2'
        parser.reset()

        node = parser.parseBinaryExpression()
        self.assertEqual(node.op, '&')
        self.assertEqual(node.left.op, '!=')
        self.assertEqual(node.right.value, '2')
        self.assertEqual(node.left.right.op, 'in')

        parser.src = 'a + b in d'
        parser.reset()

        node = parser.parseBinaryExpression()
        self.assertEqual(node.op, 'in')
        self.assertEqual(node.left.op, '+')

        parser.src = 'a + b in d'
        parser.reset()

        node = parser.parseBinaryExpression(True)
        self.assertEqual(node.op, '+')
        self.assertEqual(node.left.name, 'a')
        self.assertEqual(node.right.name, 'b')

