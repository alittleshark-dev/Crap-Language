# -*- coding: utf-8 -*-

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
数据类型 / Data types
"""
class Expression(ASTNode):
    """表达式基类：会产生一个值"""
    pass

class Number(Expression):
    """
    数字类型
    """
    def __init__(self, value):
        """数字类型
           value: 存放的数字 """
        super().__init__(data=value)

    def __repr__(self):
        return f"Number({self.data!r})"

class UnaryOp(Expression):
    """
    一元运算符（如负号）
    """
    def __init__(self, operator, operand=None):
        """一元运算符（如负号）
        operator: 操作符（如 "-"）
        operand: 操作数
        """
        super().__init__(data=operator)
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.data!r} operand={self.operand!r})"

class String(Expression):
    """
    字符串
    """
    def __init__(self, value):
        """字符串
        value: 字符串内容
        """
        super().__init__(data=value)

    def __repr__(self):
        return f"String({self.data!r})"

class ListNode(Expression):
    """
    列表
    """
    def __init__(self, elements):
        """列表
        elements: 元素列表
        """
        super().__init__(data=elements)

    def __repr__(self):
        return f"ListNode({self.data!r})"


"""
表达式 / Expression
"""
class BinOp(Expression):
    """
    二元运算符
    """
    def __init__(self, operator, left=None, right=None):
        """二元运算符
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
变量 / Variables
"""
class Identifier(Expression):
    """
    变量
    """
    def __init__(self, name, var=None):
        """变量
        name: 变量名
        var(default=None): 值
        """
        super().__init__(data=name)
        self.var = var

    def __repr__(self):
        return f"Identifier({self.data!r}, var={self.var!r})"


"""
比较表达式 / Compare
"""
class Compare(Expression):
    def __init__(self, left=None, operator=None, right=None):
        """比较表达式（如 a > b, x == y）
        left: 左操作数
        operator: 比较运算符（如 ">", "<", "=="）
        right: 右操作数
        """
        super().__init__(data=operator)
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Compare({self.left!r} {self.data!r} {self.right!r})"

class Gt(Compare):
    def __init__(self, left=None, right=None):
        """大于
        left: 左操作数
        operator: 大于运算符>
        right: 右操作数
        """
        super().__init__(left=left, operator=">", right=right)

    def __repr__(self):
        return f"Gt(Operator: {self.data} left: {self.left}) right: {self.right}"

class Lt(Compare):
    def __init__(self, left=None, right=None):
        """小于
        left: 左操作数
        operator: 小于运算符<
        right: 右操作数
        """
        super().__init__(left=left, operator="<", right=right)

    def __repr__(self):
        return f"Lt(Operator: {self.data} left: {self.left}) right: {self.right}"

class Eq(Compare):
    def __init__(self, left=None, right=None):
        """等于
        left: 左操作数
        operator: 等于运算符=
        right: 右操作数
        """
        super().__init__(left=left, operator="=", right=right)

    def __repr__(self):
        return f"Eq(Operator: {self.data} left: {self.left}) right: {self.right}"

"""
语句 / Statement
"""
class Statement(ASTNode):
    """语句基类：执行一个动作，不产生值"""
    pass


"""
控制流 / Control Flow
"""
class Condition(Statement):
    """
    条件判断
    """
    def __init__(self, condition, left=None, right=None):
        """条件判断
        condition: 条件
        left(default=None): 左子节点（if块）
        right(default=None): 右子节点（else块）
        """
        super().__init__(data=condition)
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Condition(condition={self.data!r} left={self.left!r} right={self.right!r})"


"""
输入输出 / Input and Output
"""
class Output(Statement):
    """
    输出
    """
    def __init__(self, arg=None):
        """输出
        arg: 输出的内容
        """
        super().__init__(data=arg)

    def __repr__(self):
        return f"Output(arg={self.data!r})"

class Input(Statement):
    """
    输入
    """
    def __init__(self, arg=None, var=None):
        """输入
        arg: 提示内容
        var: 传入的值
        """
        super().__init__(data=arg)
        self.var = var

    def __repr__(self):
        return f"Input(arg={self.data!r} var={self.var!r})"