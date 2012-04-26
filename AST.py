__author__ = 'Robur'


class Node:
    def __init(self):
        self.parent = None


class ProgramNode(Node):
    def __init__(self):
        self.sourceElements = []


class FunctionDeclaration(Node):
    def __init__(self,name,arguments):
        self.name = name
        self.arguments = arguments

