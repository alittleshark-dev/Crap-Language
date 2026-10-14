# parser.py
path: ./parser.py

parser.py 是 Crap-Language 的语法分析器。

它接收 lexer.py 输出的 token 列表，组装成 AST（抽象语法树），输出到 self.aststack。


## 输入 / 输出

输入：token_code，lexer.tokenizer() 返回的 token 列表
输出：self.aststack，AST 节点列表

调用方式：

    par = parser.Parser(tokens)
    par.parser()
    ast = par.aststack


## 内部变量表

变量                类型            作用
------------------  --------------  ----------------------------------
self.aststack       list            最终 AST 节点栈
temp_vars           list            正在组装的表达式零件
temp_masks          list            待处理的运算符
list_number         list            列表元素
bracket_stack       list            括号层数标记
temp_minus          str / None      一元负号标记
is_IF               bool            是否在 ? 之后
true_branch_list    list            当前真分支的语句
false_branch_list   list            当前假分支的语句
true_branch         bool            当前在真分支还是假分支
running             bool            是否继续解析
line                int             当前行号
debug               bool            调试开关


## 各变量详解

self.aststack
    最终 AST 栈。所有解析完成的节点最终都进这里。
    - 遇到完整语句 → 压栈
    - 遇到 ; → 打包栈顶节点
    - 输出时按顺序打印

temp_vars
    正在组装的表达式零件。
    装的是：Number、String、Identifier、UnaryOp、BinOp。
    遇到运算符时，从这里弹出左右操作数组装。

temp_masks
    待处理的运算符。
    装的是：BinOp('+')、BinOp('-')、BinOp('*')、BinOp('/')。
    按优先级弹出，和 temp_vars 配对组装。

list_number
    列表元素。
    a 1 2 3; 里的 1 2 3 攒在这里，遇到 ; 时组装成 ListNode。

bracket_stack
    括号层数标记。
    - ( 时记录当前 len(temp_masks)
    - ) 时把 temp_masks 恢复到那一层

temp_minus
    一元负号标记。
    -1 里的 - 不是减号，是负号。
    遇到 - 且 temp_vars 为空时，设 temp_minus = "-"，
    下一个数字走 UnaryOp。

is_IF
    是否在 ? 之后。
    - ? 到来 → is_IF = True
    - > < = 在 is_IF 为真时 → 当比较运算符（Gt / Lt / Eq）
    - is_IF 为假时 → > 是输出前缀，< 是输入前缀

true_branch_list / false_branch_list
    当前真 / 假分支的语句。
    - ? ... ; 里的输出 → 进 true_branch_list
    - : ... ; 里的输出 → 进 false_branch_list
    - : 时把 true_branch_list 塞进 Condition.left
    - ; 时把 false_branch_list 塞进 Condition.right

true_branch
    当前在真分支还是假分支。
    - ? 后 → True
    - : 后 → False
    - 假分支合并后 → True

running
    是否继续解析。
    - 初始 True
    - 出错时设 False
    - 主循环开头 if not running: break

line
    当前行号。
    - 初始 1
    - 每次 ; 时 +1
    - 报错时打印

debug
    调试开关。
    - True：打印每步的 aststack、temp_vars、temp_masks 等
    - False：只输出结果


## 组装流程

token → temp_vars / temp_masks → 组装 → aststack
          ↑
       遇到 ; 时组装

例子：1 + 2 * 3;

步骤    token   temp_vars                               temp_masks
------  ------  --------------------------------------  --------------------------
1       1       [Number('1')]                           []
2       +       [Number('1')]                           [BinOp('+')]
3       2       [Number('1'), Number('2')]              [BinOp('+')]
4       *       [Number('1'), Number('2')]              [BinOp('+'), BinOp('*')]
5       3       [Number('1'), Number('2'), Number('3')] [BinOp('+'), BinOp('*')]
6       ;       [BinOp('+', 1, BinOp('*', 2, 3))]       []
7       输出    aststack = [BinOp('+', 1, BinOp('*', 2, 3))]


## 关键分支

TOKEN_END
    ; 是最复杂的分支，负责：
    1. 组装 temp_vars / temp_masks 里的表达式
    2. 把 temp_vars 里的值填进 Input / Output
    3. 处理 list_number → ListNode
    4. 打包 Identifier
    5. 处理分支：true_branch_list / false_branch_list
    6. 合并 Condition.right
    7. 打包 Condition

TOKEN_COLON
    : 负责：
    1. 检查 true_branch_list 非空
    2. 检查栈顶是 Eq / Gt / Lt 且未打包
    3. 创建 Condition(condition=栈顶, left=true_branch_list)
    4. true_branch = False

TOKEN_OUTPUT / TOKEN_INPUT / TOKEN_EQUAL
    这三个符号有双重语义：
    - is_IF 为真 → 比较运算符（Gt / Lt / Eq）
    - is_IF 为假 → 输出 / 输入前缀


## 已知问题

- a 12 ?< b; 里 12 被赋给 b，不是 a

## 调试

打开 debug = True，日志会输出到：

    ./log/YY-MM-DD_HH-MM_astdebug.log

每步打印：

- now_token：当前 token
- Packaged?：栈顶是否打包
- bracket_stack
- true_branch_list / false_branch_list
- true_branch
- temp_vars / temp_masks
- list_number
- temp_minus
- gen_aststack：当前 AST 栈
