# -*- coding: utf-8 -*-
# Copyright (c) 2026, alittleshark-dev
from datetime import datetime
import logging
import random
import os

os.makedirs("log", exist_ok=True)

DEBUG = False

timestamp = datetime.now().strftime("%y-%m-%d %H-%M")
log_file = f"log/{timestamp}_astdebug.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | | %(message)s",
    force=True,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class ASTNode:
    def __init__(self, data, left=None, right=None, condition=None):
        self.data = data
        self.left:ASTNode = left
        self.right:ASTNode = right
        self.condition:ASTNode = condition
        self.packaged = False

    def __repr__(self):
        if self.right is None and self.left is not None and self.data in ("-",):
            return f"UnaryOp({self.data!r} operand={self.left!r})"


        if self.condition is not None:
            return f"Condition({self.data!r} condition={self.condition!r} left={self.left!r} right={self.right!r})"
        
        if self.left is None and self.right is None:
            return f"Leaf({self.data!r})"

        if self.data == ">":
            return f"OUTPUT({self.data!r} arg={self.left!r})"

        if self.data == "<":
            return f"INPUT({self.data!r} arg={self.right!r}) var={self.left!r}"
        return f"BinOp({self.data!r} left={self.left!r} right={self.right!r})"

class Identifier(ASTNode):
    def __init__(self, name):
        super().__init__(data=name)
        self.name = name

    def __repr__(self):
        return f"ValDecl({self.data!r} val={self.left!r})"

class UnaryOp(ASTNode):
    def __init__(self, operator, operand=None):
        super().__init__(data=operator, left=operand)
        self.operator = operator

class Compiler:
    def __init__(self, code):
        self.code = code
        self.token_code = []
        self.tokens = {">": "TOKEN_OUTPUT",
                       "<": "TOKEN_INPUT", 
                       "?": "TOKEN_IF",
                       "!": "TOKEN_BREAK",
                       ";": "TOKEN_END",
                       ":": "TOKEN_COLON",
                       "=": "TOKEN_EQUAL",
                       "+": "TOKEN_PLUS",
                       "-": "TOKEN_MINUS",
                       "/": "TOKEN_DIV",
                       "*": "TOKEN_MUL",
                       "(": "TOKEN_L_BRACKETS",
                       ")": "TOKEN_R_BRACKETS",
                       "[": "TOKEN_L_SQUARE",
                       "]": "TOKEN_R_SQUARE"}
        self.aststack = []
        self.line = 0

    def lexer(self):
        in_string = False
        temp = ""
        
        for ch in self.code:
            if in_string:
                if ch == '"':
                    self.token_code.append(("TOKEN_STRING", temp))
                    temp = ""
                    in_string = False
                else:
                    temp += ch
                continue
            if ch == "\n":continue
            if ch == '"':
                in_string = True
                
            elif ch == " ":
                if len(temp) != 0:
                    if temp.isdigit():
                        self.token_code.append(("TOKEN_NUMBER", temp))
                    else:
                        self.token_code.append(("TOKEN_IDENTIFIER", temp))
                    temp = ""
                    
            elif ch in self.tokens:
                if len(temp) != 0:
                    if temp.isdigit():
                        self.token_code.append(("TOKEN_NUMBER", temp))
                    else:
                        self.token_code.append(("TOKEN_IDENTIFIER", temp))
                    temp = ""
                self.token_code.append((self.tokens[ch], ch))
                
            else:
                temp += ch

        if len(temp) != 0:
            if temp.isdigit():
                self.token_code.append(("TOKEN_NUMBER", temp))
            else:
                self.token_code.append(("TOKEN_IDENTIFIER", temp))
        return self.token_code

    def get_priority(self, token_type):
        """
            判断运算符的优先级
        """
        if token_type == "(": return -1
        if token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "+", "-"]: return 1
        if token_type in ["TOKEN_MUL", "TOKEN_DIV", "*", "/"]: return 2
        return 0

    def parser(self):
        bracket_stack = []
        temp_numbers = []
        temp_masks = []
        list_number = []
        temp_minus = None
        errorflag = True

        for token in self.token_code:
            logging.debug(
                f"[Compiler] [sub] [Parser] [ln {self.line}]\n"
                f"now_token: {token}\n"
                f"bracket_stack: {bracket_stack}\n"
                f"temp_number: {temp_numbers}\n"
                f"temp_masks: {temp_masks}\n"
                f"list_number: {list_number}\n"
                f"temp_minus: {temp_minus}\n"
                f"gen_aststack: {self.aststack}\n"
            )
            token_type, data = token
            if token_type == "TOKEN_NUMBER":
                if type(self.aststack[-1]) is Identifier and self.aststack[-1].packaged == False:
                    list_number.append(ASTNode(data))
                
                elif temp_minus == "-":
                    temp_numbers.append(UnaryOp("-", data))
                    temp_minus = None
                
                else:
                    temp_numbers.append(ASTNode(data))
                
            elif token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "TOKEN_MUL", "TOKEN_DIV"]:
                # 优先级
                while len(temp_masks) != 0 and\
                        self.get_priority(temp_masks[-1].data) >= self.get_priority(token_type):

                    op_node = temp_masks.pop()

                    right = temp_numbers.pop()
                    left = temp_numbers.pop()

                    op_node.left = left
                    op_node.right = right
                    temp_numbers.append(op_node)
                if token_type == "TOKEN_MINUS" and len(temp_numbers) == 0:
                    temp_minus = data
                
                else:
                    temp_masks.append(ASTNode(data))

            elif token_type == "TOKEN_L_BRACKETS":
                bracket_stack.append(len(temp_masks))

            elif token_type == "TOKEN_R_BRACKETS":

                start_masks = bracket_stack.pop()

                while len(temp_masks) > start_masks:

                    op_node = temp_masks.pop()

                    right = temp_numbers.pop()
                    left = temp_numbers.pop()

                    op_node.left = left
                    op_node.right = right

                    temp_numbers.append(op_node)
            
            elif token_type == "TOKEN_OUTPUT":
                self.aststack.append(ASTNode(data))

            elif token_type == "TOKEN_INPUT":
                if len(self.aststack) != 0:
                    if type(self.aststack[-1]) is Identifier and self.aststack[-1].packaged == False:
                        self.aststack.append(ASTNode(data, left=self.aststack.pop()))
                else:
                    self.aststack.append(ASTNode(data))


            elif token_type == "TOKEN_STRING":
                if (type(self.aststack[-1]) is Identifier
                    and not self.aststack[-1].packaged):
                    self.aststack[-1].left = ASTNode(data)

                elif (self.aststack[-1].data == "<"
                      and self.aststack[-1].right == None
                      and not self.aststack[-1].packaged):
                    self.aststack[-1].right = ASTNode(data)

                elif (self.aststack[-1].data == ">"
                      and self.aststack[-1].left == None
                      and not self.aststack[-1].packaged):
                    self.aststack[-1].left = ASTNode(data)

                else:
                    self.aststack[-1].right = ASTNode(data)

            elif token_type == "TOKEN_IDENTIFIER":
                print(f"identifier! {data}")
            
                if len(self.aststack) == 0:
                    self.aststack.append(Identifier(data))
                    continue
            
                if len(temp_masks) == len(temp_numbers) and len(temp_numbers) != 0:
                    print("add to numbers")
                    temp_numbers.append(Identifier(data))
            
                elif (self.aststack[-1].data == "<"
                      and self.aststack[-1].right == None
                      and not self.aststack[-1].packaged):
                    print("add to input!")
                    self.aststack[-1].right = Identifier(data)
                
                elif (self.aststack[-1].data == ">"
                      and self.aststack[-1].left == None
                      and not self.aststack[-1].packaged):
                    print("add to output")
                    self.aststack[-1].left = Identifier(data)
                
                else:
                    print("add to aststack")
                    self.aststack.append(Identifier(data))


            elif token_type == "TOKEN_END":
                self.line += 1

                if len(temp_masks) != 0:
                    while len(temp_masks) != 0:
                        if len(temp_numbers) > 2 and len(temp_masks) == 1:
                            print(f"Syntax error [{self.line} line]: Missing operator between numbers")
                            errorflag = False
                            temp_masks.clear()
                            temp_numbers.clear()
                            self.aststack.clear()
                            break
                        if len(temp_masks) == len(temp_numbers) and type(self.aststack[-1]) is not Identifier:
                            missing_op = temp_masks[-1].data
                            print(f"Syntax error [{self.line} line]: Missing right operand for '{missing_op}'")
                            errorflag = False
                            temp_masks.clear()
                            temp_numbers.clear()
                            self.aststack.clear()
                            break
                        num = temp_numbers.pop()
                        op_node = temp_masks.pop()
                        op_node.left = temp_numbers.pop()
                        op_node.right = num
                        temp_numbers.append(op_node)
                    if errorflag:
                        if (len(self.aststack) != 0
                            # 是输入输出
                            and self.aststack[-1].data in (">", "<")
                            # 没有表达式
                            and self.aststack[-1].left == None
                            # 没被打包
                            and not self.aststack[-1].packaged):
                            self.aststack[-1].left = temp_numbers.pop()
                            self.aststack[-1].packaged = True

                        else:
                            self.aststack.append(temp_numbers.pop())
                
                    if type(self.aststack[-1]) is Identifier and self.aststack[-1].left == None:
                        self.aststack[-1].left = list_number
                        self.aststack[-1].packaged = True

                    if len(temp_numbers) == 1:
                        self.aststack.append(temp_numbers.pop())

                    if type(self.aststack[-1]) is Identifier:
                        self.aststack[-1].packaged = True

                    if not self.aststack[-1].packaged:
                        self.aststack[-1].packaged = True
                
                if DEBUG:
                    print(f"Compiler [{self.line} line]: 空行，跳过")

                else:
                    info_list = ["编译了一个分号, 什么都没有发生",
                                 "编译成功！输出了一个滚木！",
                                 "滚木！",
                                 "编译器什么都没有干, 并且很生气的说出了这句话",
                                 "解锁成就： 一行空气"]
                    print(f"Compiler [{self.line} line]: {random.choice(info_list)}")

                list_number = []

        return f" Debug: \n  numbers: {temp_numbers} \n  temp_masks: {temp_masks} \n aststack: {self.aststack}"

if __name__ == "__main__":
    code = '''
    > 1 + 2 * 3;
    > (1 + 2) * 3;
    a 24;
    b 2 4 3;
    str "hello";
    > a;
    -1 * 2 + 3;
    a 24;
    a < str;
    < "Hello!";
    a < "请输入";
    a;
    < "hello";
    1+2*i+1;
    '''
    error_code = """
    > 1 * 2 * 4*;
"""
    fib = """
    a 1 1;
    i 0; i ?> 10 !:;
        b a[i+1];
        a [i+2] [a[i] + b];
    :;
    > a;
"""
    debug_code = """
    < "Hello!";
    a < "请输入";
    a;
    < "hello";
    """

    text_code = code
    my_compiler = Compiler(text_code)
    print("INPUT_CODE: ")
    print(text_code)
    tokens = my_compiler.lexer()
    print("Tokens: \n")
    for token in tokens:
        print(f"\t{token}")
    ast = my_compiler.parser()
    print()
    print("AST: ")
    # print(ast)
    line = 0
    for node in my_compiler.aststack:
        line += 1
        print(f"\t[ln {line}]: {node}")
