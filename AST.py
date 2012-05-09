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


class Number(Node):
    def __init__(self, value):
        #TODO: parse numbers correctly
        super().__init__()
        self.value = value


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
