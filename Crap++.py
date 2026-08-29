# -*- coding: utf-8 -*-
# Copyright (c) 2026, alittleshark-dev
class ASTNode:
    def __init__(self, data, left=None, right=None, condition=None):
        self.data = data
        self.left:ASTNode = left
        self.right:ASTNode = right
        self.condition:ASTNode = condition

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
                       ")": "TOKEN_R_BRACKETS"}
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

        for token in self.token_code:
            token_type, data = token
            if token_type == "TOKEN_NUMBER":
                if type(self.aststack[-1]) is Identifier:
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
                if type(self.aststack[-1]) is Identifier and self.aststack[-1].left == None:
                    self.aststack.append(ASTNode(data, left=self.aststack.pop()))
                else:
                    self.aststack.append(ASTNode(data))

            elif token_type == "TOKEN_STRING":
                if type(self.aststack[-1]) is Identifier:
                    self.aststack[-1].left = ASTNode(data)

                elif self.aststack[-1].data in (">", "<") and self.aststack[-1].right is None:
                    self.aststack[-1].right = ASTNode(data)
                
                elif self.aststack[-1].data in (">", "<") and self.aststack[-1].left is None:
                    self.aststack[-1].left = ASTNode(data)

                else:
                    self.aststack[-1].right = ASTNode(data)


            elif token_type == "TOKEN_IDENTIFIER":
                if (self.aststack[-1].data == ">" or self.aststack[-1].data == "<") and self.aststack[-1].left == None:
                    self.aststack[-1].left = Identifier(data)
                else:
                    self.aststack.append(Identifier(data))

            elif token_type == "TOKEN_END":
                self.line += 1

                if len(temp_masks) != 0:
                    while len(temp_masks) != 0:
                        print(len(temp_masks), len(temp_numbers), "\n", temp_masks, temp_numbers, self.aststack)
                        if len(temp_numbers) == 1 and len(temp_masks) != 0:
                            missing_op = temp_masks[-1].data
                            print(f"Syntax error [{self.line} line]: Missing right operand for '{missing_op}'")
                            temp_masks.clear()
                            temp_numbers.clear()
                            break
                        
                        num = temp_numbers.pop()
                        op_node = temp_masks.pop()
                        op_node.left = temp_numbers.pop()
                        op_node.right = num
                        temp_numbers.append(op_node)
                    
                    if len(self.aststack) != 0 and self.aststack[-1].data in (">", "<") and self.aststack[-1].left == None:
                        self.aststack[-1].left = temp_numbers.pop()
                    else:
                        self.aststack.append(temp_numbers.pop())
                
                if len(list_number) != 0 and type(self.aststack[-1]) is Identifier and self.aststack[-1].left == None:
                    self.aststack[-1].left = list_number

                if len(temp_numbers) == 1:
                    self.aststack.append(temp_numbers.pop())

                if len(temp_numbers) > 1:
                    print(f"Syntax error [{self.line} line]: Missing operator between numbers")
                    temp_numbers.clear()
                    temp_masks.clear()

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
    < "Hello!";
    a < "请输入";
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
    # print(ast)
    line = 0
    for node in my_compiler.aststack:
        line += 1
        print(f"\t[ln {line}]: {node}")
