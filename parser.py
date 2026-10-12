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
        """
        Parser初始化
        self.aststack: list 这里是生成好的AST列表
        line: int           生成到的行数
        token_code: list    待转换AST 的 Token列表
        """
        self.aststack = []
        self.line = 1
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

    def parser(self):
        """
        bracker_stack: list 用来处理括号
        temp_numbers: list  临时放数字的栈
        temp_masks: list    临时存放符合的栈
        list_number: list   存放数字变量
        temp_minus: str     存放是不是负数
        errorflag: bool     报错标签防止报错依旧处理
        is_IF               用来判断是不是比较运算符
        """
        bracket_stack = []
        temp_numbers = []
        temp_masks = []
        list_number = []
        temp_minus = None
        errorflag = True
        is_IF = False
        true_branch_list = []
        false_branch_list = []
        true_branch = True

        for token in self.token_code:
            logging.debug(
                f"[Compiler] [sub] [Parser] [ln {self.line}] [unloop]\n"
                f"now_token: {token}\n"
                f"bracket_stack: {bracket_stack}\n"
                f"true_branch_list: {true_branch_list}\n"
                f"false_branch_list: {false_branch_list}\n"
                f"true_branch: {true_branch}\n"
                f"temp_number: {temp_numbers}\n"
                f"temp_masks: {temp_masks}\n"
                f"list_number: {list_number}\n"
                f"temp_minus: {temp_minus}\n"
                f"gen_aststack: {self.aststack}\n"
            )
            token_type, data = token
            if token_type == "TOKEN_NUMBER":
                if (is_IF and type(self.aststack[-1]) in (Gt, Eq, Lt)
                          and self.aststack[-1].right == None):
                    self.aststack[-1].right = Number(data)
                    is_IF=False
                    continue

                if (len(self.aststack) != 0 
                    and type(self.aststack[-1]) is Identifier
                    and self.aststack[-1].packaged == False):
                    list_number.append(Number(data))
                    continue
                
                if (len(self.aststack) != 0 and temp_minus == "-"):
                    temp_numbers.append(UnaryOp("-", data))
                    temp_minus = None

                else:
                    temp_numbers.append(Number(data))


            if token_type == "TOKEN_STRING":
                if (is_IF and type(self.aststack[-1]) in (Gt, Eq, Lt)
                        and self.aststack[-1].right == None):
                    self.aststack[-1].right = String(data)
                    is_IF=False
                    continue

                if (type(self.aststack[-1]) is Identifier
                    and not self.aststack[-1].packaged
                    and self.aststack[-1].var == None):
                    self.aststack[-1].var = String(data)
                    continue

                if (type(self.aststack[-1]) is Input
                        and self.aststack[-1].data == None
                        and not self.aststack[-1].packaged
                        and not is_IF):
                    self.aststack[-1].data = String(data)
                    continue

                if (type(self.aststack[-1]) is Output
                        and self.aststack[-1].data == None
                        and not self.aststack[-1].packaged):
                    self.aststack[-1].data = String(data)

                else:
                    self.aststack.append(String(data))

            if token_type == "TOKEN_IDENTIFIER":
                if (is_IF and type(self.aststack[-1]) in (Gt, Eq, Lt)
                          and self.aststack[-1].right == None):
                    self.aststack[-1].right = Identifier(data)
                    is_IF = False
                    continue

                if (len(self.aststack) == 0 and len(temp_numbers) == 0):
                    self.aststack.append(Identifier(data))
                    continue
            
                if (len(temp_masks) == len(temp_numbers) and len(temp_numbers) != 0):
                    temp_numbers.append(Identifier(data))
                    continue
            
                if (type(self.aststack[-1]) is Input
                        and self.aststack[-1].data == None
                        and not self.aststack[-1].packaged):
                    self.aststack[-1].data = Identifier(data)
                    continue
                
                if (type(self.aststack[-1]) is Output
                        and self.aststack[-1].data == None
                        and not self.aststack[-1].packaged):
                    self.aststack[-1].data = Identifier(data)
                
                else:
                    self.aststack.append(Identifier(data))
            
            if token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "TOKEN_MUL", "TOKEN_DIV"]:
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

            if token_type == "TOKEN_L_BRACKETS":
                bracket_stack.append(len(temp_masks))
                continue

            if token_type == "TOKEN_R_BRACKETS":

                start_masks = bracket_stack.pop()

                while len(temp_masks) > start_masks:

                    op_node = temp_masks.pop()

                    right = temp_numbers.pop()
                    left = temp_numbers.pop()

                    op_node.left = left
                    op_node.right = right

                    temp_numbers.append(op_node)
                continue

            if token_type == "TOKEN_IF":
                is_IF = True
                continue

            if (token_type == "TOKEN_COLON"
                and len(true_branch_list) >= 1
                and len(self.aststack) > 0
                and type(self.aststack[-1]) in (Eq, Gt, Lt)
                and self.aststack[-1].packaged == False):
                self.aststack.append(Condition(condition=self.aststack.pop(), left=true_branch_list.copy()))
                true_branch_list.clear()
                true_branch = False
                continue

            else:
                errorflag = True
                print("")
                
            
            if token_type == "TOKEN_OUTPUT":
                if is_IF:
                    if (len(self.aststack) != 0 and type(self.aststack[-1]) in (String, Identifier, Number)):
                        last_node = self.aststack.pop()

                    elif len(temp_numbers) == 1:
                        last_node = temp_numbers.pop()
                        if len(temp_numbers) != 0:
                            print(f"Syntax error [{self.line} line]: Unexpected number(s) before operator.")
                            errorflag = True
                            break

                    else:
                        print(f"Syntax error [{self.line} line]: Missing left operand for comparison operator.")
                        errorflag = True
                        break
                    self.aststack.append(Gt(left=last_node))
                    continue

                else:
                    self.aststack.append(Output())

            if token_type == "TOKEN_INPUT":
                if len(self.aststack) != 0:
                    if is_IF:
                        if (len(self.aststack) != 0 and type(self.aststack[-1]) in (String, Identifier, Number)):
                            last_node = self.aststack.pop()

                        elif len(temp_numbers) != 0:
                            last_node = temp_numbers.pop()
                            if len(temp_numbers) != 0:
                                print(f"Syntax error [{self.line} line]: Unexpected number(s) before operator.")
                                errorflag = True
                                break
                        
                        else:
                            print(f"Syntax error [{self.line} line]: Missing left operand for comparison operator.")
                            errorflag = True
                            break
                        self.aststack.append(Lt(left=last_node))
                        continue

                    if type(self.aststack[-1]) is Identifier and self.aststack[-1].packaged == False:
                        self.aststack.append(Input(var=self.aststack.pop()))
                        continue

                    else:
                        self.aststack.append(Input())
                else:
                    self.aststack.append(Input())

            if token_type == "TOKEN_EQUAL":
                if len(self.aststack) != 0:
                    if is_IF:
                        if (len(self.aststack) != 0 and type(self.aststack[-1]) in (String, Identifier, Number)):
                            last_node = self.aststack.pop()

                        elif len(temp_numbers) != 0:
                            last_node = temp_numbers.pop()
                            if len(temp_numbers) != 0:
                                print(f"Syntax error [{self.line} line]: Unexpected number(s) before operator.")
                                errorflag = True
                                break
                        
                        else:
                            print(f"Syntax error [{self.line} line]: Missing left operand for comparison operator.")
                            errorflag = True
                            break
                        self.aststack.append(Eq(left=last_node))
                        continue

            if token_type == "TOKEN_END":
                self.line += 1

                if len(temp_masks) != 0:
                    while len(temp_masks) != 0:
                        if len(temp_numbers) > 2 and len(temp_masks) == 1:
                            print(f"Syntax error [{self.line} line]: Missing operator between numbers")
                            errorflag = False('19')
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
                            and type(self.aststack[-1]) is Input
                            and self.aststack[-1].data == None
                            and not self.aststack[-1].packaged):
                            self.aststack[-1].data = temp_numbers.pop()
                            self.aststack[-1].packaged = True

                        elif (len(self.aststack) != 0
                            and type(self.aststack[-1]) is Output
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
                        self.aststack[-1].var = ListNode(list_number)
                        self.aststack[-1].packaged = True

                    if len(temp_numbers) == 1:
                        self.aststack.append(temp_numbers.pop())

                    if type(self.aststack[-1]) is Identifier:
                        self.aststack[-1].packaged = True

                    if (len(self.aststack) > 1
                       and type(self.aststack[-2]) in (Eq, Lt, Gt, Condition)
                       and self.aststack[-2].packaged == False):
                            if true_branch == True:
                                true_branch_list.append(self.aststack.pop())
                            else:
                                false_branch_list.append(self.aststack.pop())
                    
                    elif (len(self.aststack) > 1
                        and type(self.aststack[-1]) is Condition
                        and self.aststack[-1].right == None
                        and len(false_branch_list) > 0):
                        self.aststack[-1].right = false_branch_list.copy()
                        false_branch_list.clear()
                        true_branch = True

                    elif not self.aststack[-1].packaged:
                        self.aststack[-1].packaged = True

                list_number = []
                temp_numbers = []
            logging.debug(
                f"[Compiler] [sub] [Parser] [ln {self.line}] [looped]\n"
                f"now_token: {token}\n"
                f"Packaged? {'Not Find' if len(self.aststack) == 0 else self.aststack[-1].packaged}\n"
                f"bracket_stack: {bracket_stack}\n"
                f"true_branch_list: {true_branch_list}\n"
                f"false_branch_list: {false_branch_list}\n"
                f"true_branch: {true_branch}\n"
                f"temp_number: {temp_numbers}\n"
                f"temp_masks: {temp_masks}\n"
                f"list_number: {list_number}\n"
                f"temp_minus: {temp_minus}\n"
                f"gen_aststack: {self.aststack}\n"
            )

        return f" Debug: \n  numbers: {temp_numbers} \n  temp_masks: {temp_masks} \n aststack: {self.aststack}"
