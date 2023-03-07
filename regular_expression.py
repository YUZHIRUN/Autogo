class RegularClass:
    def __init__(self):
        self.global_func = r'FUNC *\(.+\n\{\n(?:[\t| +|/].*\n)+\}'
        self.local_func = r'(?:static )*[\w]+.+\)\n\{ *\n(?:[ /]+.*\n)+\}'
        self.struct = r'typedef struct *\n* *\{ *\n(?: +.*?\n)+?\} *\S+?;'
        self.enum = r'typedef enum *\n* *\{ *\n(?: +.*?,*?\n)+?\} *\S+?;'
        self.macro = r'#define +(?:.+?) +(?:\S+)'
        self.global_var = r'(?:\w+) +(?:g_\S+) *= *(?:.+?);'

        self.new_line = r'\n+'

        self.comment_1 = r'//.*'
        self.comment_2 = r'/\*.*\*/'
        self.comment_3 = r'/\*.+\n.*?\*/'
        self.comment_4 = r' */\*.*\n(.+\n)+?.*\*/'

        self.global_func_name = r'FUNC *\(.+\) *(\S+)\('
        self.local_func_name = r'\w+\** +\** *(\w+) *\('
        self.macro_name = r'#define +(.+?) +(?:\S+)'
        self.global_var_name = r'(?:\w+) +(g_\S+) *= *(?:.+?);'

        self.if_re = r'if *\(.+?\)|else.*'
        self.for_re = r'for *\(.+?;.+?;.+?\)'
        self.do_re = r'do *\{|\} *while *\((.+?\));'
        self.switch_re = r'switch *\(.+?\)\n* *\{'
        self.while_re = r'while *\(.+?\)'
        self.set_value_re = r'([\w\.->\[\]\*]+?) *[=|&+-]{1,2} *([\S ]+?);|(\S+) *\+\+;'
        self.func_re = r'[\(void\)]*(?:[\w]+?)\(.*?\);|\( *\* *\w+\)\(&*.+\);'
        self.return_re = r'return +.+?;'
        self.break_re = r'break *;'




