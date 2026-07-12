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
    
    def parser(self):
        stack = []
        for token in self.token_code:
            # print(stack)
            token_type, data = token
            if token_type == "TOKEN_NUMBER":
                number = ASTNode(data)
                if len(stack) != 0:
                    stack[-1].right = number
                    if len(stack) == 2:
                        stack[0].right = stack.pop()
            if token_type in ["TOKEN_PLUS", "TOKEN_MINUS", "TOKEN_DIV", "TOKEN_MUL"]:
                mask = ASTNode(data, left=number)
                if len(stack) != 0:
                    if token_type in ["TOKEN_PLUS", "TOKEN_MINUS"]:
                        mask.right = number
                    if token_type in ["TOKEN_DIV", "TOKEN_MUL"] and stack[0].data in ["+", "-"]:
                        mask.left = stack[0].right
                    else:
                        mask.left = stack.pop()
                elif mask == "TOKEN_MINUS":
                    
                    pass
                
                stack.append(mask)
        self.aststack.append(stack.pop())
        return f"code ast stack: {self.aststack}\n temp_stack: {stack}\n stack.lenght: {len(stack)}"

if __name__ == "__main__":
    code = '''
    -3 + 4 + 5;
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
