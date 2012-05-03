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

