class RegularClass:
    def __init__(self):
        # function regular
        self.global_func = r'FUNC *\(.+\n *\{ *\n(?: +.*\n)+ *\}|FUNC *\(.+\n *\{ *\n *\}'
        self.local_func = r'[\w\*]+ *\** +[\*\w]+ *\([^{};\#]+\n\{ *\n(?: .*\n)+\}'
        self.struct = r'typedef +struct *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.enum = r'typedef +enum *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.union = r'typedef +union *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.macro = r'# *define +(?:.+?) +(?:\S+)'
        self.global_var = r'(?:\w+) +(?:g_\S+) *= *(?:.+?);'

        # comment regular
        self.comment_1 = r'//.*'
        self.comment_2 = r'/\*.*\*/'
        self.comment_3 = r'/\*.+\n.*?\*/'
        self.comment_4 = r' */\*.*\n(.+\n)+?.*\*/'

        # get names regular
        self.global_func_name = r'FUNC *\(.+\) *(\S+?)\('
        self.local_func_name = r'\w+\** +\** *(\w+) *\('
        self.macro_name = r'# *define +(.+?) +(?:\S+)'
        self.global_var_name = r'(?:\w+) +(g_\S+) *= *(?:.+?);'

        # phase check regular
        # phase check regular
        self.if_re = r'if *\(.+?\)|else.*'
        self.for_re = r'for *\(.+\)'
        self.do_re = r'do *\{|\} *while *\((.+?\));'
        self.switch_re = r'switch *\(([\w\(\)]+)\)|case +([\w\(\)]+):|default *:'
        self.while_re = r'while *\(.+?\)'
        self.set_value_re = r'(?:[^\n,;|&]+) *[|=&\+-]*= *(?:[\S| ]+?);|(\S+) *[+-]{2} *;'
        self.define_var_re = r'\w+ +(?:[\w, \[\]]+) *;'
        self.func_re = r'[\(void\) ]*(?:[\w]+?)\(.*?\);|(?:\(void\))* *\( *\* *\w+\)\(.*\);'
        self.return_re = r'return +.+?;'
        self.break_re = r'break *;'
        self.continue_re = r'continue *;'

        # get information regular
        self.get_for_info = r'for *\((.+?);(.+?);(.+?)\)'
        self.get_for_condition = r'([\w|\.|-|>|\[|\]|\*]+?) *[><=!]{1,2} *([\S| ]+?);'
        self.get_while_info = r'while *\((.+?)\)'
        self.get_do_info = r'do *\{*'
        self.get_while_of_do_info = r'\} *while *\((.+?)\);'
        self.get_if_info = r'[else]* *if *\(.+\) *\n* *\{|[else]* *if *\([^\{]+\n +[^\{]+\{|else[^\{\(\)\}]*\{'
        self.get_set_value_info = r'([^\n,;|&=+ ]+?) *([\^=|&+-]?=) *([\S| ]+?);'
        self.get_set_special_value_info = r'(\S+) *([+-]){2} *;'
        self.get_return_info = r'return +(.+?);'
        self.get_define_var = r'\w+ +([\w, \[\]]+) *;'

        # function class regular
        self.memcpy = r'memcpy *\((?:\([^\n,;]+\))* *&*(\S+?), *\n* *(?:\([^\n,;]+\))* *&*(\S+?),\n*.+\);'
        self.memset = r'memset *\((?:\([^\n,;]+\))* *&*(\S+?), *\n* *(?:\([^\n,;]+\))* *&*(\S+?),\n*.+\);'
        self.func_get_value = r'(?:\(void\))* *(\w[^\n\(\)]+?)\( *&([^\,\n;]+)\);'
        self.func_trans_value = r'(?:\(void\))* *(\w[^\n\(\)]+?)\(([^\n,;\(\)]+)\);'
        self.common_func = r'(?:\(void\))* *([\w]+?)\(.*?\);'

        # switch phase class regular
        self.switch = r'switch *\(([\w\(\)]+)\)'
        self.case = r'case +([\w\(\)]+):'
        self.default = r'default *:'

        # last function callback regular
        self.last_func = r'(?:\w+?)\(.*\)(?!\n)'
        self.get_last_func = r'(\w+?)\(.*\)(?!\n)'
        self.point_func = r'(?:\(void\))* *\( *\*( *\w+)\)\([^\n=]*\)'

        # other regular
        # self.tab_scale = r'[;\{\)]\n {2}[^ ]'
        self.compile_macro = r'\#ifn?(?:def)?.*\n(?:.+\n)+? *\#endif|\#ifn?def.*\n\#endif.+'
        self.special_sign = r'([+-^&|])='
        self.new_line = r'\n+'
        self.var_class = r'\(.int\d+\)|\(boolean\)'
