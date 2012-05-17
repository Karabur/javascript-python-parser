__author__ = 'Robur'


class Node:
    def __init__(self):
        self.parent = None


class ProgramNode(Node):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
        for s in self.statements: s.parent = self

class FunctionDeclaration(Node):
    def __init__(self,name,arguments,statements):
        super().__init__()
        self.name = name
        self.arguments = arguments
        self.statements = statements
        for s in self.statements: s.parent = self

class Block(Node):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
        for s in self.statements: s.parent = self


class VariableStatement(Node):
    def __init__(self, varDeclarations):
        super().__init__()
        self.declarations = varDeclarations
        for s in self.declarations: s.parent = self



class VariableDeclaration(Node):
    def __init__(self, name, initializer):
        super().__init__()
        self.name = name
        self.initializer = initializer
        if initializer != None: self.initializer.parent = self


class Identifier(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

class This(Node):
    def __init__(self):
        super().__init__()

class Call(Node):
    def __init__(self, expr, args):
        super().__init__()
        self.expr = expr
        self.args = args
        self.expr.parent = self
        for a in self.args: a.parent = self




class Array(Node):
    def __init__(self, items):
        super().__init__()
        self.items = items
        for i in self.items: i.parent = self


class HoleLiteral(Node):
    def __init__(self):
        super().__init__()


class ObjectLiteral(Node):
    def __init__(self, properties):
        super().__init__()
        self.properties = properties
        for p in properties: p.parent = self

#we store all keys as a string
#but value always a node
class ObjectProperty(Node):
    def __init__(self, key, value):
        super().__init__()
        self.key = key
        self.value = value
        value.parent = self

#key is still the string as for the object property
class ObjectGetSetProperty(Node):
    def __init__(self, key, getterBody=None, setterBody=None, paramName = None):
        super().__init__()
        self.key = key
        self.getterBody = getterBody
        if self.getterBody:
            for s in self.getterBody: s.parent = self
        self.setterBody = setterBody
        if self.setterBody:
            for s in self.setterBody: s.parent = self
        self.paramName = paramName

class String(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value


class BinaryExpression(Node):
    def __init__(self, left, right, op):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
        self.left.parent = self
        self.right.parent = self


class Literal(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class NullLiteral(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class BoolLiteral(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class NumericLiteral(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

class RegExpLiteral(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value


class New(Node):
    def __init__(self, expr, args):
        super().__init__()
        self.expr = expr
        self.args = args
        self.expr.parent = self
        for s in self.args: s.parent = self


class Property(Node):
    def __init__(self, object, property):
        super().__init__()
        self.object = object
        self.property = property
        self.object.parent = self
        self.property.parent = self


class PostfixExpression(Node):
    def __init__(self, expr, op):
        super().__init__()
        self.expr = expr
        self.op = op
        self.expr.parent = self


class UnaryExpression(Node):
    def __init__(self, expr, op):
        super().__init__()
        self.expr = expr
        self.op = op
        self.expr.parent = self


class ConditionalExpression(Node):
    def __init__(self, expr, left, right):
        super().__init__()
        self.expr = expr
        self.left = left
        self.right = right
        self.expr.parent = self
        self.left.parent = self
        self.right.parent = self


class AssignmentExpression(Node):
    def __init__(self, left, right, op):
        super().__init__()
        self.left = left
        self.right = right
        self.op = op
        self.left.parent = self
        self.right.parent = self


class EmptyStatement(Node):
    def __init__(self):
        super().__init__()


class IfStatement(Node):
    def __init__(self, condition, thenStatement, elseStatement):
        super().__init__()
        self.condition = condition
        self.thenStatement = thenStatement
        self.elseStatement = elseStatement

        self.condition.parent = self
        self.thenStatement.parent = self
        self.elseStatement.parent = self


class DoWhileStatement(Node):
    def __init__(self, condition, statement):
        super().__init__()
        self.condition = condition
        self.statement = statement
        self.condition.parent = self
        self.statement.parent = self


class WhileStatement(Node):
    def __init__(self, condition, statement):
        super().__init__()
        self.condition = condition
        self.statement = statement
        self.condition.parent = self
        self.statement.parent = self


class ForStatement(Node):
    def __init__(self, init, condition, next, statement):
        super().__init__()
        self.init = init
        self.condition = condition
        self.next = next
        self.statement = statement
        self.init.parent = self.condition.parent = self.next.parent = self.statement.parent = self


class ForInStatement(Node):
    def __init__(self, each, enumerable, body):
        super().__init__()
        self.each = each
        self.enumerable = enumerable
        self.body = body
        each.parent = enumerable.parent = body.parent = self


class ContinueStatement(Node):
    def __init__(self, label):
        super().__init__()
        self.label = label
        if self.label != None: self.label.parent = self

class BreakStatement(Node):
    def __init__(self, label):
        super().__init__()
        self.label = label
        if self.label != None: self.label.parent = self

class ReturnStatement(Node):
    def __init__(self, result):
        super().__init__()
        self.result = result
        if self.result != None: self.result.parent = self


class WithStatement(Node):
    def __init__(self, expr, statement):
        super().__init__()
        self.expr = expr
        self.statement = statement
        self.expr.parent = self.statement.parent = self


#cases listed in same order as in source
#default case has no label
class SwitchStatement(Node):
    def __init__(self, expr, cases):
        super().__init__()
        self.expr = expr
        self.cases = cases
        self.expr.parent = self
        for c in self.cases: c.parent = self


class CaseCause(Node):
    def __init__(self, label, statements):
        super().__init__()
        self.label = label
        self.statements = statements
        if self.label != None : self.label.parent = self
        for s in self.statements: s.parent = self


class ThrowStatement(Node):
    def __init__(self, exception):
        super().__init__()
        self.exception = exception
        self.exception.parent = self


class TryStatement(Node):
    def __init__(self, block, catchClause, finClause):
        super().__init__()
        self.block = block
        self.catchClause = catchClause
        self.finClause = finClause

        if self.catchClause!= None: self.catchClause.parent = self
        if self.finClause!= None: self.finClause.parent = self
        self.block.parent = self


class CatchClause(Node):
    def __init__(self, id, block):
        super().__init__()
        self.id = id
        self.block = block

        self.id.parent = self.block.parent = self

class FinallyClause(Node):
    def __init__(self, block):
        super().__init__()
        self.block = block
        self.block.parent = self


class DebuggerStatement(Node):
    def __init__(self):
        super().__init__()
