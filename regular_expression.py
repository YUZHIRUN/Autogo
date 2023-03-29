class RegularClass:
    def __init__(self):
        # function regular
        self.global_func = r'FUNC *\(.+\n *\{ *\n(?: +.*\n)+ *\}|FUNC *\(.+\n *\{ *\n *\}'
        self.local_func = r'[\w\*]+ *\** +[\*\w]+ *\([^{};\#]+\n\{ *\n(?: .*\n)+\}'
        self.struct = r'typedef +struct *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.enum = r'typedef +enum *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.union = r'typedef +union *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.macro = r'#define +(?:.+?) +(?:\S+)'
        self.global_var = r'(?:\w+) +(?:g_\S+) *= *(?:.+?);'

        # comment regular
        self.comment_1 = r'//.*'
        self.comment_2 = r'/\*.*\*/'
        self.comment_3 = r'/\*.+\n.*?\*/'
        self.comment_4 = r' */\*.*\n(.+\n)+?.*\*/'

        # get names regular
        self.global_func_name = r'FUNC *\(.+\) *(\S+?)\('
        self.local_func_name = r'\w+\** +\** *(\w+) *\('
        self.macro_name = r'#define +(.+?) +(?:\S+)'
        self.global_var_name = r'(?:\w+) +(g_\S+) *= *(?:.+?);'

        # phase check regular
        self.if_re = r'if *\(.+?\)|else.*'
        self.for_re = r'for *\(.+\)'
        self.do_re = r'do *\{|\} *while *\((.+?\));'
        self.switch_re = r'switch *\(([\w\(\)]+)\)|case +([\w\(\)]+):|default *:'
        self.while_re = r'while *\(.+?\)'
        self.set_value_re = r'(?:[^\n,;|&]+) *[|=&\+-]*= *(?:[\S| ]+?);|(\S+) *[+-]{2} *;'
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
        self.condition_func = r'(\w+?)\(.+\)(?!\n)'
        self.point_func = r'(?:\(void\))* *\( *\*( *\w+)\)\([^\n=]*\)'

        # other regular
        self.tab_scale = r'[;\{\)]\n {2}[^ ]'
        self.compile_macro = r'\#ifn?(?:def)?.*\n(?:.+\n)+? *\#endif|\#ifn?def.*\n\#endif.+'
        self.special_sign = r'([+-^&|])='
        self.new_line = r'\n+'

        # variable definition regular
        # self.variable1 = r'\w+\** +\**(?:[\w\[\]]+)(?: *= *[\w\{\}]+)* *;(?![^ \n])'
        self.variable = r'\w+\** +\**(?:[\w\[\]]+)(?: *= *[\w\{\}]+)* *[;,\)](?![^ \n])'
        # self.variable2 = r'\w+\** +(?:[\*\w\[\]]+,)+[^\n\(\),]+;(?![^ \n])'
        self.params = r'\w+\** +\**(?:[\w]+) *[,\)](?![^ \n])'

        self.get_variable = r'(\w+)\** +\**([\w\[\]]+)(?: *= *[\w\{\}]+)* *[;,\)](?![^ \n])'
        # self.get_variable2 = r'(\w+)\** +(?:[\*\w\[\]]+,)+[^\n\(\),]+;(?![^ \n])'
        self.get_params = r'(\w+)\** +\**([\w]+) *[,\)](?![^ \n])'

    def any_find(self, input_str: str):
        re1 = r'(?<!\w)'
        re2 = r'(?!\w)'
        res = re1 + input_str + re2
        return res


class variables_class:
    def __init__(self):
        self.uint8 = 'u8'
        self.sint8 = 'i8'
        self.uint16 = 'u16'
        self.sint16 = 'i16'
        self.uint32 = 'u32'
        self.uint64 = 'u64'
        self.sint64 = 'i64'
        self.float32 = 'f32'
        self.float = 'f32'
        self.double = 'd64'
        self.float64 = 'd64'
        self.pointer = 'p'
        self.boolean = 'bool'
        self.arr = 'a'
        self.struct = 'st'
        self.enum = 'e'
        self.union = 'un'
        self.def_struct = 'ST'
        self.def_enum = 'E'
        self.def_union = 'UN'
        self.link = '_'

    def is_ptr(self, input_str: str):
        if input_str.count('*') == 0:
            return False
        else:
            return True

    def is_array(self, input_str: str):
        if input_str.count('[') != 0 and input_str.count(']') != 0:
            return True
        else:
            return False

    def has_add_pre(self, compare_pre, obj: str):
        if obj.count(compare_pre) != 0:
            return True
        else:
            return False
