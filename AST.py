__author__ = 'Robur'


class Node:
    def __init(self):
        self.parent = None


class ProgramNode(Node):
    def __init__(self):
        self.sourceElements = []


class FunctionDeclaration(Node):
    def __init__(self,name,arguments,sourceElements):
        self.name = name
        self.arguments = arguments
        self.sourceElements = sourceElements

class Block(Node):
    def __init__(self,statements):
        self.statements = statements