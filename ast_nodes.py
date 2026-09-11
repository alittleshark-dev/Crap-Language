#              -*- coding: utf-8 -*-

# ==================================================
#                File: ./ast_nodes.py
#        Copyright © alittleshark-dev 2026
#               Licensed under the 
#                   MIT License
#             See for details /LICENSE
# ==================================================
class ASTNode:
    def __init__(self, data):
        self.data = data
        self.packaged = False


"""
数据类型/ Data types
"""
class Number(ASTNode):
    def __init__(self, value):
        super().__init__(data=value)

    def __repr__(self):
        return f"Number({self.data!r})"

class UnaryOp(ASTNode):
    def __init__(self, operator, operand=None):
        """ Represents a unary operation node in the AST. """
        super().__init__(data=operator)
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.data!r} operand={self.operand!r})"

class String(ASTNode):
    def __init__(self, value):
        super().__init__(data=value)

    def __repr__(self):
        return f"String({self.data!r})"

class List(ASTNode):
    def __init__(self, elements):
        super().__init__(data=elements)

    def __repr__(self):
        return f"List({self.data!r})"

"""
运算符/ Operators
"""
class BinOp(ASTNode):
    def __init__(self, operator, left=None, right=None):
        super().__init__(data=operator)
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.data!r} left={self.left!r} right={self.right!r})"

"""
变量/ Variables
"""
class Identifier(ASTNode):
    def __init__(self, name, var=None):
        super().__init__(data=name)
        self.var = var

    def __repr__(self):
        return f"Identifier({self.data!r}, var={self.var!r})"

"""
控制流/ Control Flow
"""
class Condition(ASTNode):
    """ Represents a condition node in the AST. """
    def __init__(self, condition, left=None, right=None):
        super().__init__(data=condition)
        self.left = left
        self.right = right
        
    def __repr__(self):
        return f"Condition(condition={self.data!r} left={self.left!r} right={self.right!r})"

"""
输入输出/ Input and Output
"""
class OUTPUT(ASTNode):
    def __init__(self, arg=None):
        super().__init__(data=arg)


    def __repr__(self):
        return f"OUTPUT(arg={self.data!r})"

class INPUT(ASTNode):
    def __init__(self, arg=None, var=None):
        super().__init__(data=arg)
        self.var = var

    def __repr__(self):
        return f"INPUT(arg={self.data!r} var={self.var!r})"
