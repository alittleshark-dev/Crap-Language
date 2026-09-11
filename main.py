#              -*- coding: utf-8 -*-

# ==================================================
#                File: ./main.py
#        Copyright © alittleshark-dev 2026
#               Licensed under the 
#                   MIT License
#             See for details /LICENSE
# ==================================================

import lexer
import parser

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
str "hello";
> a;
-1 * 2 + 3;
a 24;
a < str;
< "Hello!";
a < "请输入";
a;
< "hello";
"""

text_code = code

lex = lexer.Lexer(text_code)
for token in lex.tokenizer():
    print(token)

par = parser.Parser(lex.token_code)
par.parser()
for node in par.aststack:
    print(node)