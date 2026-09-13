#              -*- coding: utf-8 -*-

# ==================================================
#                File: ./ast_nodes.py
#        Copyright © alittleshark-dev 2026
#               Licensed under the 
#                   MIT License
#             See for details /LICENSE
# ==================================================
class ASTNode:
    """
    所有AST节点的基类
    """
    def __init__(self, data):
        """ data: str  存放Token """
        self.data = data
        self.packaged = False


"""
数据类型/ Data types
"""
class Number(ASTNode):
    """
    数字类型
    """
    def __init__(self, value):
        """ value: 存放的数字 """
        super().__init__(data=value)

    def __repr__(self):
        return f"Number({self.data!r})"

class UnaryOp(ASTNode):
    """
    一元运算符（如负号）
    """
    def __init__(self, operator, operand=None):
        """
        operator: 操作符（如 "-"）
        operand: 操作数
        """
        super().__init__(data=operator)
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.data!r} operand={self.operand!r})"

class String(ASTNode):
    """
    字符串
    """
    def __init__(self, value):
        """
        value: 字符串内容
        """
        super().__init__(data=value)

    def __repr__(self):
        return f"String({self.data!r})"

class ListNode(ASTNode):
    """
    列表
    """
    def __init__(self, elements):
        """
        elements: 元素列表
        """
        super().__init__(data=elements)

    def __repr__(self):
        return f"ListNode({self.data!r})"

"""
运算符/ Operators
"""
class BinOp(ASTNode):
    """
    二元运算符
    """
    def __init__(self, operator, left=None, right=None):
        """
        operator: 操作符
        left(default=None): 左子节点
        right(default=None): 右子节点
        """
        super().__init__(data=operator)
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.data!r} left={self.left!r} right={self.right!r})"

"""
变量/ Variables
"""
class Identifier(ASTNode):
    """
    变量
    """
    def __init__(self, name, var=None):
        """
        name: 变量名
        var(default=None): 值
        """
        super().__init__(data=name)
        self.var = var

    def __repr__(self):
        return f"Identifier({self.data!r}, var={self.var!r})"

"""
控制流/ Control Flow
"""
class Condition(ASTNode):
    """
    条件判断
    """
    def __init__(self, condition, left=None, right=None):
        """
        condition: 条件
        left(default=None): 左子节点
        right(default=None): 右子节点
        """
        super().__init__(data=condition)
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Condition(condition={self.data!r} left={self.left!r} right={self.right!r})"

"""
输入输出/ Input and Output
"""
class Output(ASTNode):
    """
    输出
    """
    def __init__(self, arg=None):
        """
        arg: 输出的内容
        """
        super().__init__(data=arg)

    def __repr__(self):
        return f"Output(arg={self.data!r})"

class Input(ASTNode):
    """
    输入
    """
    def __init__(self, arg=None, var=None):
        """
        arg: 提示内容
        var: 传入的值
        """
        super().__init__(data=arg)
        self.var = var

    def __repr__(self):
        return f"Input(arg={self.data!r} var={self.var!r})"