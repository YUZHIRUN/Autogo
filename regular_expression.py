class RegularClass:
    def __init__(self):
        # function regular
        self.global_func = r'FUNC *\(.+\n *\{ *\n(?: +.*\n)+ *\}|FUNC *\(.+\n *\{ *\n *\}'
        self.local_func = r'[\w*]+ *\** +[*\w]+ *\([^\n{}]+\n(?: +[^{}]+\n)*?\{ *\n(?: +.*?\n)+\}'
        self.struct = r'typedef struct *\n* *\{ *\n(?: +.*?\n)+?\} *\S+?;'
        self.enum = r'typedef enum *\n* *\{ *\n(?: +.*?,*?\n)+?\} *\S+?;'
        self.macro = r'#define +(?:.+?) +(?:\S+)'
        self.global_var = r'(?:\w+) +(?:g_\S+) *= *(?:.+?);'

        # comment regular
        self.comment_1 = r'//.*'
        self.comment_2 = r'/\*.*\*/'
        self.comment_3 = r'/\*.+\n.*?\*/'
        self.comment_4 = r' */\*.*\n(.+\n)+?.*\*/'

        # get names regular
        self.global_func_name = r'FUNC *\(.+\) *(\S+)\('
        self.local_func_name = r'\w+\** +\** *(\w+) *\('
        self.macro_name = r'#define +(.+?) +(?:\S+)'
        self.global_var_name = r'(?:\w+) +(g_\S+) *= *(?:.+?);'

        # phase check regular
        self.if_re = r'if *\(.+?\)|else.*'
        self.for_re = r'for *\(.+?;.+?;.+?\)'
        self.do_re = r'do *\{|\} *while *\((.+?\));'
        self.switch_re = r'switch *\(.+?\)\n* *\{'
        self.while_re = r'while *\(.+?\)'
        self.set_value_re = r'(?:[^\n,;|&]+) *[|=&\+-]*= *(?:[\S| ]+?);|(\S+) *[+-]{2} *;'
        self.func_re = r'[\(void\) ]*(?:[\w]+?)\(.*?\);|\( *\* *\w+\)\(.*\);'
        self.return_re = r'return +.+?;'
        self.break_re = r'break *;'

        # get information regular
        self.get_for_info = r'for *\((.+?);(.+?);(.+?)\)'
        self.get_for_condition = r'([\w|\.|-|>|\[|\]|\*]+?) *[>|<|=]{1,2} *([\S| ]+?);'
        self.get_while_info = r'while *\((.+?)\)'
        self.get_do_info = r'do *\{*'
        self.get_while_of_do_info = r'\} *while *\((.+?)\);'
        self.get_if_info = r'[else]* *if *\(.+\) *\n* *\{|[else]* *if *\([^\{]+\n +[^\{]+\{|else *\n* *\{'
        self.get_set_value_info = r'([\w\.\->\[\]\*]+?) *([=|&+-]?=) *([\S| ]+?);'
        self.get_set_special_value_info = r'(\S+) *([+-]){2} *;'
        self.get_return_info = r'return +(.+?);'

        # function class regular
        self.memcpy = r'memcpy *\((?:\([^\n,;]+\))* *&*(\S+?), *\n* *(?:\([^\n,;]+\))* *&*(\S+?),\n*.+\);'
        self.memset = r'memset *\((?:\([^\n,;]+\))* *&*(\S+?), *\n* *(?:\([^\n,;]+\))* *&*(\S+?),\n*.+\);'
        self.func_get_value = r'[\(void\)]*(\w\S+?)\( *&([^\,\n;]+)\);'
        self.func_trans_value = r'[\(void\)]*(\w\S+?)\(([^\n,;]+)\);'
        self.common_func = r'[\(void\)]* *([\w]+?)\(.*?\);'
        self.point_func = r'\( *\*( *\w+)\)\([^\n=]*\)'

        # other regular
        self.special_sign = r'([+-])='
        self.new_line = r'\n+'
