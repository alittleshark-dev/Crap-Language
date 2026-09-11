#              -*- coding: utf-8 -*-

# ==================================================
#                File: ./parser.py
#        Copyright © alittleshark-dev 2026
#               Licensed under the 
#                   MIT License
#             See for details /LICENSE
# ==================================================

from ast_nodes import *
from datetime import datetime
import logging
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


class Parser:
    def __init__(self, token_code):
        self.aststack = []
        self.line = 0
        self.token_code = token_code

    def get_priority(self, token_type):
        """判断运算符的优先级"""
        if token_type == "(":
            return -1
        if token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "+", "-"]:
            return 1
        if token_type in ["TOKEN_MUL", "TOKEN_DIV", "*", "/"]:
            return 2
        return 0

    def _reduce(self, temp_numbers, temp_masks, start=0):
        """从 temp_masks[start:] 开始归约，结果压入 temp_numbers"""
        while len(temp_masks) > start:
            op_node = temp_masks.pop()
            if len(temp_numbers) < 2:
                print(f"Syntax error [line {self.line}]: Missing operand for '{op_node.data}'")
                return False
            right = temp_numbers.pop()
            left = temp_numbers.pop()
            op_node.left = left
            op_node.right = right
            temp_numbers.append(op_node)
        return True

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
                    list_number.append(Number(data))
                
                elif temp_minus == "-":
                    temp_numbers.append(UnaryOp("-", data))
                    temp_minus = None
                
                else:
                    temp_numbers.append(Number(data))
                
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
                    temp_masks.append(BinOp(data))

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
                self.aststack.append(OUTPUT())

            elif token_type == "TOKEN_INPUT":
                if len(self.aststack) != 0:
                    if type(self.aststack[-1]) is Identifier and self.aststack[-1].packaged == False:
                        self.aststack.append(INPUT(var=self.aststack.pop()))
                    else:
                        self.aststack.append(INPUT())
                else:
                    self.aststack.append(INPUT())


            elif token_type == "TOKEN_STRING":
                if (type(self.aststack[-1]) is Identifier
                    and not self.aststack[-1].packaged
                    and self.aststack[-1].var == None):
                    self.aststack[-1].var = String(data)

                elif (type(self.aststack[-1]) is INPUT
                      and self.aststack[-1].data == None
                      and not self.aststack[-1].packaged):
                    self.aststack[-1].data = String(data)

                elif (type(self.aststack[-1]) is OUTPUT
                      and self.aststack[-1].data == None
                      and not self.aststack[-1].packaged):
                    self.aststack[-1].data = String(data)

                else:
                    self.aststack.append(String(data))

            elif token_type == "TOKEN_IDENTIFIER":
                if len(self.aststack) == 0:
                    self.aststack.append(Identifier(data))
                    continue
            
                if len(temp_masks) == len(temp_numbers) and len(temp_numbers) != 0:
                    temp_numbers.append(Identifier(data))
            
                elif (type(self.aststack[-1]) is INPUT
                      and self.aststack[-1].data == None
                      and not self.aststack[-1].packaged):
                    self.aststack[-1].data = Identifier(data)
                
                elif (type(self.aststack[-1]) is OUTPUT
                      and self.aststack[-1].data == None
                      and not self.aststack[-1].packaged):
                    self.aststack[-1].data = Identifier(data)
                
                else:
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
                            and type(self.aststack[-1]) is INPUT
                            and self.aststack[-1].data == None
                            and not self.aststack[-1].packaged):
                            self.aststack[-1].data = temp_numbers.pop()
                            self.aststack[-1].packaged = True

                        elif (len(self.aststack) != 0
                            and type(self.aststack[-1]) is OUTPUT
                            and self.aststack[-1].data == None
                            and not self.aststack[-1].packaged):
                            self.aststack[-1].data = temp_numbers.pop()
                            self.aststack[-1].packaged = True

                        else:
                            self.aststack.append(temp_numbers.pop())

                if errorflag:
                    if (len(list_number) > 0
                        and type(self.aststack[-1]) is Identifier
                        and self.aststack[-1].var == None):
                        self.aststack[-1].var = List(list_number)
                        self.aststack[-1].packaged = True

                    if len(temp_numbers) == 1:
                        self.aststack.append(temp_numbers.pop())

                    if type(self.aststack[-1]) is Identifier:
                        self.aststack[-1].packaged = True

                    if not self.aststack[-1].packaged:
                        self.aststack[-1].packaged = True

                list_number = []

        return f" Debug: \n  numbers: {temp_numbers} \n  temp_masks: {temp_masks} \n aststack: {self.aststack}"
