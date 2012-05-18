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

        self.assertEqual(len(parser.ASTRoot.statements),1)
        self.assertEqual(type(parser.ASTRoot.statements[0]), AST.FunctionDeclaration)
        self.assertEqual(parser.ASTRoot.statements[0].name, 'name1')
        self.assertEqual(parser.ASTRoot.statements[0].parent, parser.ASTRoot)

    def test03ArgumentsFunctionDeclaration(self):
        parser = Parser()
        parser.src = 'function asd(aa,a23) {}'
        parser.buildAST()

        node = parser.ASTRoot.statements[0]
        self.assertEqual(len(node.arguments),2)
        self.assertEqual(node.arguments[0],'aa')
        self.assertEqual(node.arguments[1],'a23')

    def test04FunctionDeclarationAsBodyOfFunctionDeclaration(self):
        parser = Parser()
        parser.src = 'function outer(asd) {\
        function tt() {}\
        }'

        parser.buildAST()

        node = parser.ASTRoot.statements[0]

        self.assertEqual(len(node.statements),1)

    def test05ParseProgramAsBlockStatements(self):
        parser = Parser()
        parser.src = '{}'

        parser.buildAST()

        self.assertEqual(len(parser.ASTRoot.statements),1)
        node = parser.ASTRoot.statements[0]
        self.assertEqual(type(node), AST.Block)
        parser.src = '{}{}'

        parser.buildAST()

        self.assertEqual(len(parser.ASTRoot.statements),2)
        node = parser.ASTRoot.statements[0]
        self.assertEqual(type(node), AST.Block)
        node = parser.ASTRoot.statements[1]
        self.assertEqual(type(node), AST.Block)

    def test06ParseBlockStatementInFunctionBody(self):
        parser = Parser()
        parser.src = 'function a(){ {} }'

        parser.buildAST()
        node = parser.ASTRoot.statements[0]
        self.assertEqual(type(node.statements[0]), AST.Block)

    def test07ParseVariableStatement(self):
        parser = Parser()
        parser.src = 'var x;'
        parser.buildAST()
        node = parser.ASTRoot.statements[0]
        self.assertEqual(type(node), AST.VariableStatement)
        self.assertEqual(node.declarations[0].name,'x')

        parser.src = 'var x=1,b;'
        parser.buildAST()
        node = parser.ASTRoot.statements[0]
        self.assertEqual(type(node), AST.VariableStatement)
        self.assertEqual(node.declarations[0].initializer.value,'1')
        self.assertEqual(node.declarations[0].name,'x')
        self.assertEqual(node.declarations[1].name,'b')
        self.assertEqual(node.declarations[1].initializer,None)

    def test08ParseLeftHandSideExpression(self):
        parser = Parser()
        parser.src = 'a 1'
        parser.reset()
        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.Identifier)
        self.assertEqual(node.name, 'a')

        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.NumericLiteral)
        self.assertEqual(node.value, '1')

        parser.src = 'a[1] asd[b]'
        parser.reset()
        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.Property)
        self.assertEqual(node.object.name, 'a')
        self.assertEqual(node.property.value, '1')
        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.Property)
        self.assertEqual(node.object.name, 'asd')
        self.assertEqual(node.property.name, 'b')

        parser.src = 'a.b.c'
        parser.reset()
        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.Property)
        self.assertEqual(node.property.name, 'c')
        self.assertEqual(node.object.property.name, 'b')
        self.assertEqual(node.object.object.name, 'a')


    def test09ParseCallLeftHandSideExpression(self):
        parser = Parser()
        parser.src = 'b() c()() d(1)(2,a) '
        parser.reset()

        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.Call)
        self.assertEqual(type(node.expr), AST.Identifier)
        self.assertEqual(node.expr.name, 'b')

        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.Call)
        self.assertEqual(type(node.expr), AST.Call)
        self.assertEqual(node.expr.expr.name, 'c')

        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(len(node.expr.args), 1)
        self.assertEqual(type(node.expr.args[0]), AST.NumericLiteral)
        self.assertEqual(node.expr.args[0].value, '1')

        self.assertEqual(len(node.args), 2)
        self.assertEqual(type(node.args[0]), AST.NumericLiteral)
        self.assertEqual(type(node.args[1]), AST.Identifier)
        self.assertEqual(node.args[0].value, '2')
        self.assertEqual(node.args[1].name, 'a')

        parser.src = 'new a()    new new b(a)(23,3)(12,c,b)'
        parser.reset()
        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.New)
        self.assertEqual(type(node.expr), AST.Identifier)
        self.assertEqual(node.expr.name, 'a')
        self.assertEqual(node.args, [])

        node = parser.parseLeftHandSideExpression(False)
        self.assertEqual(type(node), AST.Call)
        self.assertEqual(len(node.args), 3)
        self.assertEqual(type(node.expr), AST.New)
        self.assertEqual(len(node.expr.args), 2)
        self.assertEqual(type(node.expr.expr), AST.New)
        self.assertEqual(len(node.expr.expr.args), 1)
        self.assertEqual(node.expr.expr.args[0].name, 'a')



    def test10PrimaryExpression(self):
        parser = Parser()
        parser.src = 'this asd false true null "dd" 56.7e34 /asd/i [] [1,a,,3]'
        parser.reset()

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.This)

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.Identifier)

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.BoolLiteral)
        self.assertEqual(node.value, 'false')
        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.BoolLiteral)
        self.assertEqual(node.value, 'true')
        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.NullLiteral)
        self.assertEqual(node.value, 'null')
        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.Literal)
        self.assertEqual(node.value, 'dd')
        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.NumericLiteral)
        self.assertEqual(node.value, '56.7e34')
        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.RegExpLiteral)
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

        parser.src ='{get :1, set:3+3}'
        parser.reset()

        node = parser.parsePrimaryExpression()
        self.assertEqual(type(node), AST.ObjectLiteral)
        self.assertEqual(node.properties[0].key, 'get')
        self.assertEqual(node.properties[0].value.value, '1')
        self.assertEqual(node.properties[1].key, 'set')
        self.assertEqual(node.properties[1].value.op, '+')


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

        node = parser.parseBinaryExpression(False, 0)
        self.assertEqual(type(node), AST.BinaryExpression)
        self.assertEqual(node.left.value , '1')
        self.assertEqual(node.right.value, '2')
        self.assertEqual(node.op, '/')

        parser.src = 'a<<1>c>>d'
        parser.reset()

        node = parser.parseBinaryExpression(False, 0)
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

        node = parser.parseBinaryExpression(False, 0)
        self.assertEqual(node.op, '&')
        self.assertEqual(node.left.op, '!=')
        self.assertEqual(node.right.value, '2')
        self.assertEqual(node.left.right.op, 'in')

        parser.src = 'a + b in d'
        parser.reset()

        node = parser.parseBinaryExpression(False, 0)
        self.assertEqual(node.op, 'in')
        self.assertEqual(node.left.op, '+')

        parser.src = 'a + b in d'
        parser.reset()

        node = parser.parseBinaryExpression(True,0)
        self.assertEqual(node.op, '+')
        self.assertEqual(node.left.name, 'a')
        self.assertEqual(node.right.name, 'b')

    def test15parseConditionalExpression(self):
        parser = Parser()

        parser.src = '1+2 ? 4*2 : 5'
        parser.reset()

        node = parser.parseConditionalExpression(False)
        self.assertEqual(type(node), AST.ConditionalExpression)
        self.assertEqual(node.expr.op, '+')
        self.assertEqual(node.left.op, '*')
        self.assertEqual(node.right.value, '5')

    def test16parseAssignmentExpression(self):
        parser = Parser()

        parser.src = 'b[1]=33+=4'
        parser.reset()

        node = parser.parseAssignmentExpression(False)
        self.assertEqual(type(node), AST.AssignmentExpression)
        self.assertEqual(node.left.property.value, '1')
        self.assertEqual(node.right.op, '+=')
        self.assertEqual(node.right.right.value, '4')

        parser.src = 'b/=33'
        parser.reset()

        node = parser.parseAssignmentExpression(False)
        self.assertEqual(type(node), AST.AssignmentExpression)
        self.assertEqual(node.left.name, 'b')
        self.assertEqual(node.op, '/=')

    def test17parseEmptyExpression(self):
        parser = Parser()

        parser.src = ';;'

        parser.buildAST()

        self.assertEqual(len(parser.ASTRoot.statements),2)
        self.assertEqual(type(parser.ASTRoot.statements[0]),AST.EmptyStatement)
        self.assertEqual(type(parser.ASTRoot.statements[1]),AST.EmptyStatement)

    def test18parseIfStatement(self):
        parser = Parser()

        parser.src = 'if (1) ; else var a=1;'

        root = parser.buildAST()

        self.assertEqual(len(root.statements),1)
        self.assertEqual(type(root.statements[0]), AST.IfStatement)
        self.assertEqual(root.statements[0].condition.value, '1')
        self.assertEqual(type(root.statements[0].thenStatement), AST.EmptyStatement)
        self.assertEqual(type(root.statements[0].elseStatement), AST.VariableStatement)

        parser.src = 'if (x==1) {}'

        root = parser.buildAST()

        self.assertEqual(len(root.statements),1)
        self.assertEqual(type(root.statements[0]), AST.IfStatement)
        self.assertEqual(type(root.statements[0].condition), AST.BinaryExpression)
        self.assertEqual(root.statements[0].condition.op, '==')
        self.assertEqual(type(root.statements[0].thenStatement), AST.Block)
        self.assertEqual(type(root.statements[0].elseStatement), AST.EmptyStatement)

        parser.src = 'if (x==1) if (y==2) {;} else {;;} else {;;;}'

        node = parser.buildAST().statements[0]

        self.assertEqual(type(node.thenStatement), AST.IfStatement)
        self.assertEqual(len(node.elseStatement.statements), 3)
        self.assertEqual(len(node.thenStatement.thenStatement.statements), 1)
        self.assertEqual(len(node.thenStatement.elseStatement.statements), 2)

    def test19IterationStatement(self):
        parser = Parser()
        parser.src = 'do do ; while (1===1); while (a!=1+2);'

        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.DoWhileStatement)
        self.assertEqual(type(node.statement), AST.DoWhileStatement)
        self.assertEqual(type(node.condition), AST.BinaryExpression)
        self.assertEqual(node.condition.op, '!=')
        self.assertEqual(node.statement.condition.op, '===')
        self.assertEqual(type(node.statement.statement), AST.EmptyStatement)

        parser.src = 'while (0) {}'

        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.WhileStatement)
        self.assertEqual(type(node.statement), AST.Block)
        self.assertEqual(node.condition.value, '0')

        parser.src = 'for (a=1;a<12;a()) {}'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.ForStatement)
        self.assertEqual(type(node.statement), AST.Block)
        self.assertEqual(type(node.init), AST.AssignmentExpression)
        self.assertEqual(node.init.left.name, 'a')
        self.assertEqual(type(node.condition), AST.BinaryExpression)
        self.assertEqual(node.condition.op, '<')

        self.assertEqual(type(node.next), AST.Call)
        self.assertEqual(node.next.expr.name, 'a')

        parser.src = 'for (var b=1,c=2;a<12;a()) {}'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node.init), AST.Block)
        self.assertEqual(len(node.init.statements), 2)
        self.assertEqual(type(node.init.statements[0]), AST.VariableDeclaration)

        parser.src = 'for (var b=1;a<12;a()) {}'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node.init), AST.VariableDeclaration)
        self.assertEqual(node.init.name, 'b')

        parser.src = 'for (var f in asdd) {}'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.ForInStatement)
        self.assertEqual(node.each.name, 'f')
        self.assertEqual(node.enumerable.name, 'asdd')

        parser.src = 'for (x in dsdd) {}'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.ForInStatement)
        self.assertEqual(node.each.name, 'x')
        self.assertEqual(node.enumerable.name, 'dsdd')

    def test20ContinueStatement(self):
        parser = Parser()
        parser.src = 'continue;'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.ContinueStatement)

        #ASI testing
        parser.src = 'continue\ncontinue'
        statements = parser.buildAST().statements

        self.assertEqual(len(statements), 2)
        self.assertEqual(type(statements[0]), AST.ContinueStatement)
        self.assertEqual(type(statements[1]), AST.ContinueStatement)

        #ASI testing
        parser.src = 'continue asd\ncontinue ddd;'
        statements = parser.buildAST().statements

        self.assertEqual(len(statements),2)
        self.assertEqual(statements[0].label.name,'asd')
        self.assertEqual(statements[1].label.name,'ddd') 

    def test21BreakStatement(self):
        parser = Parser()
        parser.src = 'break;'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.BreakStatement)

        #ASI testing
        parser.src = 'break\nbreak'
        statements = parser.buildAST().statements

        self.assertEqual(len(statements), 2)
        self.assertEqual(type(statements[0]), AST.BreakStatement)
        self.assertEqual(type(statements[1]), AST.BreakStatement)

        parser.src = 'break asd\nbreak ddd;'
        statements = parser.buildAST().statements

        self.assertEqual(len(statements),2)
        self.assertEqual(statements[0].label.name,'asd')
        self.assertEqual(statements[1].label.name,'ddd')

    def test22ReturnStatement(self):
        parser = Parser()
        parser.src = 'return;'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.ReturnStatement)

        #ASI testing
        parser.src = 'return\nreturn'
        statements = parser.buildAST().statements

        self.assertEqual(len(statements), 2)
        self.assertEqual(type(statements[0]), AST.ReturnStatement)
        self.assertEqual(type(statements[1]), AST.ReturnStatement)

        parser.src = 'return 22+1\nreturn asd=3;'
        statements = parser.buildAST().statements

        self.assertEqual(len(statements),2)
        self.assertEqual(statements[0].result.op,'+')
        self.assertEqual(statements[1].result.left.name,'asd')

    def test23WithStatement(self):
        parser = Parser()
        parser.src = 'with (dd) {}'

        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.WithStatement)
        self.assertEqual(node.expr.name,'dd')
        self.assertEqual(type(node.statement),AST.Block)

    def test24SwitchStatement(self):
        parser = Parser()
        parser.src = 'switch (a) {\
        case "aa": {};\n\
                    ;\n\
        default: ;\
        }'

        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.SwitchStatement)
        self.assertEqual(node.expr.name, 'a')
        self.assertEqual(len(node.cases), 2)
        self.assertEqual(node.cases[0].label.value, 'aa')
        self.assertEqual(len(node.cases[0].statements), 3)
        self.assertEqual(type(node.cases[0].statements[0]), AST.Block)
        self.assertEqual(type(node.cases[0].statements[1]), AST.EmptyStatement)

        self.assertEqual(node.cases[1].label, None)
        self.assertEqual(len(node.cases[1].statements), 1)
        self.assertEqual(type(node.cases[1].statements[0]), AST.EmptyStatement)

    def test25ThrowStatement(self):
        parser = Parser()
        parser.src = 'throw 123;'
        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.ThrowStatement)

        #ASI testing
        parser.src = 'throw 33\n throw 23'
        statements = parser.buildAST().statements

        self.assertEqual(len(statements), 2)
        self.assertEqual(type(statements[0]), AST.ThrowStatement)
        self.assertEqual(statements[0].exception.value, '33')
        self.assertEqual(type(statements[1]), AST.ThrowStatement)
        self.assertEqual(statements[1].exception.value, '23')

        parser.src = '{throw 22+1} throw asd=3;'
        statements = parser.buildAST().statements

        self.assertEqual(len(statements),2)
        self.assertEqual(statements[0].statements[0].exception.op,'+')
        self.assertEqual(statements[1].exception.left.name,'asd')

    def test26TryStatement(self):
        parser = Parser()
        parser.src = 'try { ; } catch (ff) {}'

        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.TryStatement)
        self.assertEqual(len(node.block.statements), 1)
        self.assertEqual(node.catchClause.id.name, 'ff')
        self.assertEqual(len(node.catchClause.block.statements), 0)

        parser.src = 'try { ; } finally {try {} catch (d) {} finally {}}'

        node = parser.buildAST().statements[0]

        self.assertEqual(node.catchClause, None)
        self.assertEqual(type(node.finClause.block.statements[0]), AST.TryStatement)

    def test27LabelledStatement(self):
        parser = Parser()
        parser.src = 'dd: {}'

        node = parser.buildAST().statements[0]

        self.assertEqual(type(node), AST.LabelledStatement)
        self.assertEqual(node.label.name, 'dd')
        self.assertEqual(type(node.statement), AST.Block)

    def test28ExpressionStatement(self):
        parser = Parser()
        parser.src = '123;a+1;x/=4\nrrr'

        statements = parser.buildAST().statements

        self.assertEqual(type(statements[0]), AST.ExpressionStatement)
        self.assertEqual(statements[0].expr.value, '123')
        self.assertEqual(statements[1].expr.op, '+')
        self.assertEqual(statements[2].expr.op, '/=')
        self.assertEqual(statements[3].expr.name, 'rrr')