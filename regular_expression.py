class RegularClass:
    def __init__(self):
        # function regular
        self.global_func = r'FUNC *\(.+\n *\{ *\n(?: +.*\n)+ *\}|FUNC *\(.+\n *\{ *\n *\}'
        self.local_func = r'[\w\*]+ *\** +[\*\w]+ *\([^{};\#]+\n\{ *\n(?: .*\n)+\}'
        self.enum = r'typedef +enum *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.union = r'typedef +union *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.macro = r'# *define +(?:.+?) +(?:.+)'
        self.global_var = r'(?:static)* *(?:\w+) +(?:g_[\w\[\]\*]+).+;'

        # struct
        self.struct = r'typedef +struct *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.struct_head = r'(?:.|\n)+?\{\n'
        self.struct_tail = r'\n *\}.+\n*'

        # comment regular
        self.comment_1 = r'//.*'
        self.comment_2 = r'/\*.*\*/'
        self.comment_3 = r'/\*.+\n.*?\*/'
        self.comment_4 = r' */\*.*\n(.+\n)+?.*\*/'
        self.st_item = r'([\w\*]+) +([\w\[\]\*]+);'
        self.en_item = r'(\w+) *,?( *= *(\w+))*'

        # get names regular
        self.global_func_name = r'FUNC *\(.+\) *(\S+?)\('
        self.local_func_name = r'\w+\** +\** *(\w+) *\('
        self.global_var_name = r'(?:static)* *(?:\w+) +(g_[\w\[\]\*]+).+;'
        self.global_var_type = r'(?:static)* *(\w+) +(?:g_[\w\[\]\*]+).+'
        self.include_file = r'# *include +(?:.+?(?:"|>))'

        # phase check regular
        self.if_re = r'if *\(.+?\)|else.*'
        self.for_re = r'for *\(.+\)'
        self.do_re = r'do *\{|\} *while *\((.+?\));'
        self.switch_re = r'switch *\(([^\n\{}]+)\)|case +([^\n\{}]+):|default *:'
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
        self.get_define_type = r'(\w+) +(?:[\w, \[\]]+) *;'
        self.get_include_file = r'# *include +(.+?(?:"|>))'
        self.get_macro_name = r'# *define +(.+?) +(?:.+)'
        self.macro_value = r'# *define +(?:.+?) +(.+)'

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
        self.li_coor = r'li\[(\d+)\]'

class Xpath:
    def __init__(self):
        self.base_item = r'/html/body/div[3]/div/form/div[2]/div[2]/div[2]/ul/li/ul'
        self.items = r'/html/body/div[3]/div/form/div[2]/div[2]/div[2]'
        self.origin_folder = r'/html/body/div[3]/div/form/div[2]/div[2]/div[2]/ul/li/i'
        self.origin_item = r'/html/body/div[3]/div/form/div[2]/div[2]/div[2]/ul/li/a'
        self.object_type = r'//*[@class="propertyTable inlineEditEnabled"]/tbody[1]//td[contains(text(), "ObjectType")]/../td[2]'
        self.req_category = r'/html/body/div[3]/div/form/div[2]/div[3]/div[2]/div/div[3]/div/div/div/div/div[1]/table/table/tbody/tr[6]/td[2]'
        self.object_type_select = r'//select[@class="pixelResizeEditBox"]'
        self.copy = r'/html/body/ul/li[20]/a'
        # self.insert_new_child = r'/html/body/ul/li[6]/a'
        self.insert_new_child = r'//*[contains(text(), "Insert a new Child Item (Ctrl + Insert)")]'
        self.new_item_after = r'//*[contains(text(), "Insert a new Item after this (Ctrl + Enter)")]'
        # self.new_item_before = r'/html/body/ul/li[7]/a'
        # self.paste_below = r'/html/body/ul/li[7]/a'
        # self.paste_above = r'/html/body/ul/li[6]/a'
        # self.paste_new_child = r'/html/body/ul/li[6]/a'
        self.input_content = r'//*[@class="editable new-item description-container editor-wrapper wysiwyg"]/div[2]/div/div'
        self.input_title = r'//*[@class="editable new-item description-container editor-wrapper wysiwyg"]/div/div/input'
        self.draft = '//*[text()="Draft"]'
        self.paint_button = '//*[@id="toolbarContainer"]/div/button[4]/i'
        # table
        self.insert_table = '//*[@class="fr-popup fr-desktop fr-ltr cb-custom-popup fr-active"]/div[1]/button[1]/i'
        self.table_init_div = r'//*[@class="fr-select-table-size"]/span[1]/span[1]'
        self.tab_xpath = r'//*[@class="fr-select-table-size"]/span[$]/span[1]'
        self.tab_content = r'//*[@class="editable new-item description-container editor-wrapper wysiwyg"]/div[2]/div/div/table[1]/tbody[1]/tr[$0]/td[$1]'
        self.add_row_bt = r'//span[text()="Remove Table"]/../../button[2]'
        self.add_row_select = r'//a[text()="Insert row below"]'
        self.add_col_bt = r'//span[text()="Remove Table"]/../../button[3]'
        self.add_col_select = r'//a[text()="Insert column after"]'

        self.set_color_bt = r'//span[text()="Remove Table"]/../../button[5]'
        self.color_gray = r'//span[contains(text(), "Color #CCCCCC")]/..'


