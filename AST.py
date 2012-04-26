__author__ = 'Robur'


class Node:
    def __init(self):
        self.parent = None


class ProgramNode(Node):
    sourceElements = []


class FunctionDeclaration(Node):
    name = ''
    arguments=[]
    def __init__(self,name):
        self.name = name

