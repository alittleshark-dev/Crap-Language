#              -*- coding: utf-8 -*-

# ==================================================
#                File: ./lexer.py
#        Copyright © alittleshark-dev 2026
#               Licensed under the 
#                   MIT License
#             See for details /LICENSE
# ==================================================

class Lexer:
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

    def tokenizer(self):
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
