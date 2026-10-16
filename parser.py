#              -*- coding: utf-8 -*-

# ==================================================
#                File: ./parser.py
#        Copyright © alittleshark-dev 2026
#              docs: ./docs/parser.md
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
        """
        判断运算符的优先级。
        括号返回 -1，保证栈内比较时不会被弹出；
        加减返回 1，乘除返回 2，其他返回 0。
        """
        if token_type == "(":
            return -1
        if token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "+", "-"]:
            return 1
        if token_type in ["TOKEN_MUL", "TOKEN_DIV", "*", "/"]:
            return 2
        return 0

    def parser(self):
        """
        bracket_stack: list        用来处理括号，记录每个左括号对应的运算符栈深度
        temp_number: list          表达式求值栈，数字、变量、BinOp 混装
        temp_masks: list           运算符栈，等待归约的 BinOp 节点
        vars_list: list            列表字面量缓冲，收集变量名后面的元素
        temp_minus: str            标记一元负号，None 或 "-"
        running: bool              是否继续解析，出错时置 False
        is_IF: bool                标记是否在 ? 之后，决定 > < = 是比较还是输入输出
        true_branch_list: list     用来存放真分支的语句
        false_branch_list: list    用来存放假分支的语句
        true_branch: bool          当前是否在真分支
        debug: bool                调试开关
        """

        bracket_stack = []      # 括号位置，记录 op_stacks 的深度
        temp_number = []        # 表达式求值栈
        temp_masks = []         # 运算符栈
        vars_list = []          # 列表字面量缓冲
        temp_minus = None       # 一元负号标记
        running = True          # 出错时置 False，提前结束
        is_IF = False           # 是否处于 ? 之后
        true_branch_list = []   # 真分支语句
        false_branch_list = []  # 假分支语句
        true_branch = True      # 当前是否在真分支
        debug = True            # 调试日志开关

        for token in self.token_code:

            # 打印进入本 token 处理前的状态快照
            if debug:
                logging.debug(
                    f"[Compiler] [sub] [Parser] [ln {self.line}] [unloop]\n"
                    f"now_token: {token}\n"
                    f"Packaged? {'Not Find' if len(self.aststack) == 0 else self.aststack[-1].packaged}\n"
                    f"bracket_stack: {bracket_stack}\n"
                    f"true_branch_list: {true_branch_list}\n"
                    f"false_branch_list: {false_branch_list}\n"
                    f"true_branch: {true_branch}\n"
                    f"temp_number: {temp_number}\n"
                    f"temp_masks: {temp_masks}\n"
                    f"vars_list: {vars_list}\n"
                    f"temp_minus: {temp_minus}\n"
                    f"gen_aststack: {self.aststack}\n"
                )

            token_type, data = token

            # 数字处理
            if token_type == "TOKEN_NUMBER":
                # 在 ? 之后，且栈顶是等待右操作数的比较节点，就把它填进去
                if (is_IF and type(self.aststack[-1]) in (Gt, Eq, Lt)
                          and self.aststack[-1].right == None):
                    self.aststack[-1].right = Number(data)
                    is_IF = False
                    continue

                # 栈顶是未打包的变量名，说明这是列表字面量的元素
                if (len(self.aststack) != 0
                    and type(self.aststack[-1]) is Identifier
                    and self.aststack[-1].packaged == False):
                    vars_list.append(Number(data))
                    continue

                # 前面有一元负号，包成 UnaryOp 再入栈
                if (len(self.aststack) != 0 and temp_minus == "-"):
                    temp_number.append(UnaryOp("-", data))
                    temp_minus = None

                # 普通数字，直接进表达式栈
                else:
                    temp_number.append(Number(data))

            # 字符串处理
            if token_type == "TOKEN_STRING":
                # 在 ? 之后，填进比较节点的右操作数
                if (is_IF and type(self.aststack[-1]) in (Gt, Eq, Lt)
                        and self.aststack[-1].right == None):
                    self.aststack[-1].right = String(data)
                    is_IF = False
                    continue

                # 栈顶是还没赋值的变量，字符串就是它的值
                if (type(self.aststack[-1]) is Identifier
                    and not self.aststack[-1].packaged
                    and self.aststack[-1].var == None):
                    self.aststack[-1].var = String(data)
                    continue

                # 栈顶是 input，字符串是它的提示内容
                if (type(self.aststack[-1]) is Input
                        and self.aststack[-1].data == None
                        and not self.aststack[-1].packaged
                        and not is_IF):
                    self.aststack[-1].data = String(data)
                    continue

                # 栈顶是 output，字符串是它的输出内容
                if (type(self.aststack[-1]) is Output
                        and self.aststack[-1].data == None
                        and not self.aststack[-1].packaged):
                    self.aststack[-1].data = String(data)

                # 其他情况，当独立字符串入栈
                else:
                    self.aststack.append(String(data))

            # 标识符处理
            if token_type == "TOKEN_IDENTIFIER":
                # 栈顶是未打包的变量名，这个标识符是列表字面量的元素
                if (len(self.aststack) != 0
                    and type(self.aststack[-1]) is Identifier
                    and self.aststack[-1].packaged  == False
                    and self.aststack[-1].var == None):
                    vars_list.append(Identifier(data))
                    continue

                # 在 ? 之后，填进比较节点的右操作数
                if (is_IF and type(self.aststack[-1]) in (Gt, Eq, Lt)
                          and self.aststack[-1].right == None):
                    self.aststack[-1].right = Identifier(data)
                    is_IF = False
                    continue

                # 全新的标识符，直接入栈
                if (len(self.aststack) == 0 and len(temp_number) == 0):
                    self.aststack.append(Identifier(data))
                    continue

                # 前面有运算符等着操作数，这个标识符进表达式栈
                if (len(temp_masks) == len(temp_number) and len(temp_number) != 0):
                    temp_number.append(Identifier(data))
                    continue

                # 栈顶是 input，标识符是它的目标变量
                if (type(self.aststack[-1]) is Input
                        and self.aststack[-1].data == None
                        and not self.aststack[-1].packaged):
                    self.aststack[-1].data = Identifier(data)
                    continue

                # 栈顶是 output，标识符是它的输出内容
                if (type(self.aststack[-1]) is Output
                        and self.aststack[-1].data == None
                        and not self.aststack[-1].packaged):
                    self.aststack[-1].data = Identifier(data)

                # 其他情况，当新标识符入栈
                else:
                    self.aststack.append(Identifier(data))

            # 四则运算符
            if token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "TOKEN_MUL", "TOKEN_DIV"]:
                # 栈顶运算符优先级不低于当前，就先归约掉
                while len(temp_masks) != 0 and\
                        self.get_priority(temp_masks[-1].data) >= self.get_priority(token_type):

                    op_node = temp_masks.pop()

                    right = temp_number.pop()
                    left = temp_number.pop()

                    op_node.left = left
                    op_node.right = right
                    temp_number.append(op_node)

                # 表达式栈为空时，减号是一元负号，不是减法
                if token_type == "TOKEN_MINUS" and len(temp_number) == 0:
                    temp_minus = data

                # 普通二元运算符，压入运算符栈
                else:
                    temp_masks.append(BinOp(data))

            # 左括号，记录当前运算符栈深度
            if token_type == "TOKEN_L_BRACKETS":
                bracket_stack.append(len(temp_masks))
                continue

            # 右括号，把括号内的运算符全部归约掉
            if token_type == "TOKEN_R_BRACKETS":

                start_masks = bracket_stack.pop()

                while len(temp_masks) > start_masks:

                    op_node = temp_masks.pop()

                    right = temp_number.pop()
                    left = temp_number.pop()

                    op_node.left = left
                    op_node.right = right

                    temp_number.append(op_node)
                continue

            # IF 触发符 ?
            if token_type == "TOKEN_IF":
                is_IF = True
                continue

            # 冒号，真分支结束，把条件节点和真分支组装成 Condition
            if (token_type == "TOKEN_COLON"
                and len(true_branch_list) >= 1
                and len(self.aststack) > 0
                and type(self.aststack[-1]) in (Eq, Gt, Lt)
                and self.aststack[-1].packaged == False):
                self.aststack.append(Condition(condition=self.aststack.pop(), left=true_branch_list.copy()))
                true_branch_list.clear()
                true_branch = False
                continue

            # OUTPUT
            if token_type == "TOKEN_OUTPUT":
                # 在 ? 之后，output 作为比较左值，构造 Gt 节点
                if is_IF:
                    if (len(vars_list) != 0
                        and type(vars_list[-1]) is Identifier):
                        last_node = vars_list.pop()

                    elif (len(temp_number) != 0
                        and type(temp_number[-1]) is Identifier):
                        last_node = temp_number.pop()

                    elif (len(vars_list) != 0
                        and type(vars_list[-1]) is Identifier):
                        last_node = vars_list.pop()

                    elif (len(self.aststack) != 0 and type(self.aststack[-1]) in (String, Identifier, Number)):
                        last_node = self.aststack.pop()

                    elif len(temp_number) == 1:
                        last_node = temp_number.pop()
                        if len(temp_number) != 0:
                            print(f"Syntax error [{self.line} line]: Unexpected number(s) before operator.")
                            running = False
                            break

                    else:
                        print(f"Syntax error [{self.line} line]: Missing left operand for comparison operator.")
                        running = False
                        break
                    self.aststack.append(Gt(left=last_node))
                    continue

                # 普通情况，直接压入 Output 节点
                else:
                    self.aststack.append(Output())

            # INPUT
            if token_type == "TOKEN_INPUT":
                if len(self.aststack) != 0 or len(temp_number) != 0:
                    # 在 ? 之后，input 作为比较左值，构造 Lt 节点
                    if is_IF:
                        if (len(vars_list) != 0
                            and type(vars_list[-1]) is Identifier):
                            last_node = vars_list.pop()

                        elif (len(temp_number) != 0
                            and type(temp_number[-1]) is Identifier):
                            last_node = temp_number.pop()

                        elif (len(vars_list) != 0
                            and type(vars_list[-1]) in (Identifier, Number)):
                            last_node = vars_list.pop()

                        elif (len(self.aststack) != 0 and type(self.aststack[-1]) in (String, Identifier, Number)):
                            last_node = self.aststack.pop()

                        elif len(temp_number) != 0:
                            last_node = temp_number.pop()
                            if len(temp_number) != 0:
                                print(f"Syntax error [{self.line} line]: Unexpected number(s) before operator.")
                                running = False
                                break

                        else:
                            print(f"Syntax error [{self.line} line]: Missing left operand for comparison operator.")
                            running = False
                            break
                        self.aststack.append(Lt(left=last_node))
                        continue

                    # 普通情况，栈顶是未打包变量就当 input 的目标变量
                    if type(self.aststack[-1]) is Identifier and self.aststack[-1].packaged == False:
                        self.aststack.append(Input(var=self.aststack.pop()))
                        continue

                    else:
                        self.aststack.append(Input())
                else:
                    self.aststack.append(Input())

            # 等于号，在 ? 之后构造 Eq 节点
            if token_type == "TOKEN_EQUAL":
                if len(self.aststack) != 0:
                    if is_IF:
                        if (len(self.aststack) != 0 and type(self.aststack[-1]) in (String, Identifier, Number)):
                            last_node = self.aststack.pop()

                        elif len(temp_number) != 0:
                            last_node = temp_number.pop()
                            if len(temp_number) != 0:
                                print(f"Syntax error [{self.line} line]: Unexpected number(s) before operator.")
                                running = False
                                break

                        else:
                            print(f"Syntax error [{self.line} line]: Missing left operand for comparison operator.")
                            running = False
                            break
                        self.aststack.append(Eq(left=last_node))
                        continue

            # 行结束，做各种归约和打包
            if token_type == "TOKEN_END":
                self.line += 1

                # 先把剩余的运算符全部归约掉
                if len(temp_masks) != 0:
                    while len(temp_masks) != 0:
                        # 表达式栈里剩多个数字但只剩一个运算符，说明缺运算符
                        if len(temp_number) > 2 and len(temp_masks) == 1:
                            print(f"Syntax error [{self.line} line]: Missing operator between numbers")
                            running = False
                            temp_masks.clear()
                            temp_number.clear()
                            self.aststack.clear()
                            break

                        # 运算符数量比操作数还多，说明缺右操作数
                        if len(temp_masks) == len(temp_number) and type(self.aststack[-1]) is not Identifier:
                            missing_op = temp_masks[-1].data
                            print(f"Syntax error [{self.line} line]: Missing right operand for '{missing_op}'")
                            running = False
                            temp_masks.clear()
                            temp_number.clear()
                            self.aststack.clear()
                            break

                        # 弹一个运算符和两个操作数，组装成 BinOp
                        num = temp_number.pop()
                        op_node = temp_masks.pop()
                        op_node.left = temp_number.pop()
                        op_node.right = num
                        temp_number.append(op_node)

                    if running:
                        # 表达式结果落到 input 或 output 的 data 上
                        if (len(self.aststack) != 0
                            and type(self.aststack[-1]) is Input
                            and self.aststack[-1].data == None
                            and not self.aststack[-1].packaged):
                            self.aststack[-1].data = temp_number.pop()
                            self.aststack[-1].packaged = True

                        elif (len(self.aststack) != 0
                            and type(self.aststack[-1]) is Output
                            and self.aststack[-1].data == None
                            and not self.aststack[-1].packaged):
                            self.aststack[-1].data = temp_number.pop()
                            self.aststack[-1].packaged = True

                        else:
                            self.aststack.append(temp_number.pop())

                if running:
                    # 列表字面量打包成 ListNode
                    if (len(vars_list) > 0
                        and type(self.aststack[-1]) is Identifier
                        and self.aststack[-1].var == None):
                        self.aststack[-1].var = ListNode(vars_list)
                        self.aststack[-1].packaged = True

                    # 表达式栈只剩一个，塞进 aststack
                    if len(temp_number) == 1:
                        self.aststack.append(temp_number.pop())

                    # 栈顶是 Identifier，标记为已打包
                    if type(self.aststack[-1]) is Identifier:
                        self.aststack[-1].packaged = True

                    # 变量名后面跟着比较节点，合并成赋值
                    if (len(self.aststack) >= 2
                        and type(self.aststack[-2]) is Identifier
                        and type(self.aststack[-1]) in (Gt, Eq, Lt)
                        and self.aststack[-1].right != None
                        and self.aststack[-1].left != None):
                        last_node = self.aststack.pop()
                        self.aststack[-1].var = last_node
                        self.aststack[-1].packaged = True

                    # 收集条件分支的语句
                    if (len(self.aststack) > 1
                       and type(self.aststack[-2]) in (Eq, Lt, Gt, Condition)
                       and self.aststack[-2].packaged == False):
                            if true_branch:
                                true_branch_list.append(self.aststack.pop())
                            else:
                                false_branch_list.append(self.aststack.pop())

                    # 把 else 分支挂到 Condition 的右子节点上
                    if (len(self.aststack) > 0
                        and type(self.aststack[-1]) is Condition
                        and self.aststack[-1].right == None
                        and len(false_branch_list) > 0):
                        self.aststack[-1].right = false_branch_list.copy()
                        false_branch_list.clear()
                        true_branch = True

                    # 比较节点或条件节点收尾打包
                    if (self.aststack[-1].packaged == False
                        and type(self.aststack[-1]) in (Eq, Lt, Gt, Condition)
                        and self.aststack[-1].right != None and self.aststack[-1].left != None
                        and len(true_branch_list) == 0 and len(false_branch_list) == 0):
                        self.aststack[-1].packaged = True

                # 行结束，清空行内缓冲
                vars_list = []
                temp_number = []

            # 打印本 token 处理完的状态快照
            if debug:
                logging.debug(
                    f"[Compiler] [sub] [Parser] [ln {self.line}] [looped]\n"
                    f"now_token: {token}\n"
                    f"Packaged? {'Not Find' if len(self.aststack) == 0 else self.aststack[-1].packaged}\n"
                    f"bracket_stack: {bracket_stack}\n"
                    f"true_branch_list: {true_branch_list}\n"
                    f"false_branch_list: {false_branch_list}\n"
                    f"true_branch: {true_branch}\n"
                    f"temp_number: {temp_number}\n"
                    f"temp_masks: {temp_masks}\n"
                    f"vars_list: {vars_list}\n"
                    f"temp_minus: {temp_minus}\n"
                    f"gen_aststack: {self.aststack}\n"
                )

        return f" Debug: \n  numbers: {temp_number} \n  temp_masks: {temp_masks} \n aststack: {self.aststack}"