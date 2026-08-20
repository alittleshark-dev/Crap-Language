# -*- coding: utf-8 -*-
# Copyright (c) 2026, alittleshark-dev
class ASTNode:
    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left:ASTNode = left
        self.right:ASTNode = right

    def __repr__(self):
        if self.left is None or self.right is None:
            return f"Leaf({self.data!r})"
        else:
            return f"BinOp({self.data!r} left={self.left!r} right={self.right!r})"

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
                       ")": "TOKEN_R_BRACKETS"}
        self.aststack = []

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
        if token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "+", "-"]: return 1
        elif token_type in ["TOKEN_MUL", "TOKEN_DIV", "*", "/"]: return 2
        else: return 0

    def parser(self):
        stack = []
        temp_numbers = []
        temp_masks = []

        for token in self.token_code:
            token_type, data = token
            if token_type == "TOKEN_NUMBER":
                temp_numbers.append(ASTNode(data))

            elif token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "TOKEN_MUL", "TOKEN_DIV"]:                    
                while len(temp_masks) != 0 and\
                        self.get_priority(temp_masks[-1].data) >= self.get_priority(token_type):

                    op_node = temp_masks.pop()

                    right = temp_numbers.pop()
                    left = temp_numbers.pop()

                    op_node.left = left
                    op_node.right = right
                    temp_numbers.append(op_node)

                temp_masks.append(ASTNode(data))
            elif token_type == "TOKEN_END":
                # 处理表达式
                if len(temp_masks) != 0:
                   while len(temp_masks) != 0:
                       num = temp_numbers.pop()
                       op_node = temp_masks.pop()
                       op_node.left = temp_numbers.pop()
                       op_node.right = num
                       temp_numbers.append(op_node)

        return f"Debug: \n numbers: {temp_numbers}\n temp_masks: {temp_masks} \n stack: {stack}"

if __name__ == "__main__":
    code = '''
    1 + 2 + 3;
    '''
    my_compiler = Compiler(code)
    print("INPUT_CODE: ")
    print(code)
    tokens = my_compiler.lexer()
    print("Tokens: \n")
    for token in tokens:
        print(f"\t{token}")
    ast = my_compiler.parser()
    print()
    print("AST: ")
    print(ast)
