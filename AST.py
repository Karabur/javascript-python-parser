__author__ = 'Robur'


class Node:
    def __init__(self):
        self.parent = None


class ProgramNode(Node):
    def __init__(self, sourceElements):
        super().__init__()
        self.sourceElements = sourceElements
        for s in self.sourceElements: s.parent = self

class FunctionDeclaration(Node):
    def __init__(self,name,arguments,sourceElements):
        super().__init__()
        self.name = name
        self.arguments = arguments
        self.sourceElements = sourceElements
        for s in self.sourceElements: s.parent = self

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
    def __init__(self, id, initializer):
        super().__init__()
        self.id = id
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
    def __init__(self, callee, args):
        super().__init__()
        self.callee = callee
        self.args = args
        self.callee.parent = self
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
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right


class Literal(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value