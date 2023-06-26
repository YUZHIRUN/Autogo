class RegularClass:
    def __init__(self):
        # function regular
        self.point_func_declare = r'(?:static) *\w+(?:\( *\*\w+\)) *\(.+?\).+?&(?:\w+);'
        self.global_func = r'FUNC *\(.+\n *\{ *\n(?: +.*\n)+ *\}|FUNC *\(.+\n *\{ *\n *\}'
        self.local_func = r'[\w\*]+ +[\*\w]+ *\([^{};\#]+\n\{ *\n(?: .*\n)+\}'
        self.enum = r'typedef +enum *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.union = r'typedef +union *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.macro = r'# *define +(?:.+?) +(?:.+)'
        # self.global_var = r'(?:static)* *(?:[\w\*]+) +(?:g_[\w\[\]\*]+).*[;{]'
        self.global_var = r'(?:static)* *(?:[\w\* ]+) +(?:g_[\w\[\]]+) *;|(?:static)* *(?:[\w\* ]+) +(?:g_[\w\[\]]+) *= *[^;]+;'
        # struct
        self.struct = r'typedef +struct *\w* *\n* *\{ *\n(?: .*?\n)+?\} *\S+'
        self.struct_head = r'(?:.|\n)+?\{ *\n'
        self.struct_tail = r'\n *\}.+\n*'

        # comment regular
        self.comment_1 = r'//[^:\n]+|// *(?=\n)'
        self.comment_2 = r'/\*.*\*/'
        self.comment_3 = r'/\*.+\n.*?\*/'
        self.comment_4 = r' */\*.*\n(.+\n)+?.*\*/'
        # self.st_item = r'([\w\*]+) +([\w\[\]\*]+);'
        self.st_item = r'((?:struct|const|volatile| )*(?:[\w\*]+)) +([\w\[\]\*]+);'
        self.en_item = r'(\w+) *,?( *= *(\w+))*'

        # get names regular
        self.global_func_name = r'FUNC *\(.+\) *(\S+?)\('
        self.local_func_name = r'[\w\*]+ +([\w\*]+) *\('
        self.global_var_type_name = r'(?:static)* *([\w\* ]+) +(g_[\w]+).*'
        self.include_file = r'# *include +(?:.+?(?:"|>))'

        # phase check regular
        self.if_re = r'if *\(.+?\)|else.*'
        self.for_re = r'for *\(.+\)'
        self.do_re = r'do *\{|\} *while *\((.+?\));'
        self.switch_re = r'switch *\(([^\n\{}]+)\)|case +([^\n\{}]+):|default *:'
        self.while_re = r'while *\(.+?\)'
        self.set_value_re = r' *(?:[^\n,;|&=+]+?) *(?:[\^=|&+-]?=) *(?:.+?);|(\S+) *[+-]{2} *;'
        self.define_var_re = r'(?:volatile|const)* *(?:[\w\*]+) +(?:[\w, \[\]\*]+) *;'
        self.define_var_init = r'(?:(?:volatile|const|\*)* *[\w\*]+) +(?:[\w\*\-<>\[\]]+) *= *(?:.+);'
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
        self.get_set_value_info = r' *([^\n,;|&=+]+?) *([\^=|&+-]?=) *(.+?);'
        self.get_set_special_value_info = r'(\S+) *([+-]){2} *;'
        self.get_return_info = r'return +(.+?);'
        self.get_return_type = r'([\w\*]+) +(\*?@).+;'
        self.get_head_info = r'\((.+)\)'
        self.get_define_var = r'(?:volatile|const)* *(?:[\w\*]+) +([\w, \[\]\*]+) *;'
        self.get_define_type = r'((?:volatile|const)* *[\w\*]+) +(?:[\w, \[\]\*]+) *;'
        self.get_define_init_info = r'((?:volatile|const|\*)* *[\w\*]+) +([\w\*-<>\[\]]+) *= *(.+);'
        self.get_include_file = r'# *include +(.+?(?:"|>))'
        self.get_macro_name = r'# *define +(.+?) +(?:.+)'
        self.get_global_func_info = r'FUNC\( *(\w+) *, *\w+ *\) *(\w+)\((.+)\)'
        self.global_func_params = r'[\w\*]+ [\w\*]+|P\d[A-Z]+\((?:[\w\*]+),.+?\) *(?:[\w\*]+)|void'
        self.global_func_params_0 = r'void'
        self.global_func_params_1 = r'P\d[A-Z]+\(([\w\*]+),.+?\) *([\w\*]+)'
        self.global_func_params_2 = r'([\w\*]+ +[\w\*]+)'
        self.macro_value = r'# *define +(?:.+?) +(.+)'
        self.get_param_info = r'((?:const|volatile)* *[\w\*]+) +([\w\*]+)'
        self.get_point_func_info = r'(?:static) *\w+(\( *\*\w+\)) *\(.+?\).+?&(\w+);'

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
        self.last_func = r'[\w\*]+\(.+\)'
        self.get_last_func_name = r'([\w\*]+)\(.+\)'
        self.point_func = r'(?:\(void\))* *\( *\*( *\w+)\)\([^\n=]*\)'
        self.point_func_head = r'(?:\(void\))* *(\( *\*(?: *\w+)\))(\([^\n=]*\))'

        # other regular
        # self.tab_scale = r'[;\{\)]\n {2}[^ ]'
        self.compile_macro = r'\#ifn?(?:def)?.*\n(?:.+\n)+? *\#endif|\#ifn?def.*\n\#endif.+'
        self.special_sign = r'([+-^&|])='
        self.new_line = r'\n+'
        self.pointer_space = r' +\* +'
        self.new_line_space = r'\n+ *\n+'
        self.var_class = r'\(.int\d{1,}[\w\*]*?\)|\(boolean\)|\(float\d{2}\)|\(int\)'
        self.li_coor = r'li\[(\d+)\]'
        self.proto_del_bracket = r'\(.+\)'

class Xpath:
    def __init__(self):
        self.user_id = r'//*[@id="user"]'
        self.password = r'//*[@id="password"]'
        self.register = r'//*[@id="loginForm"]/div/div[2]/input'

        self.base_item = r'/html/body/div[3]/div/form/div[2]/div[2]/div[2]/ul/li/ul'
        self.items = r'/html/body/div[3]/div/form/div[2]/div[2]/div[2]'
        self.origin_folder = r'/html/body/div[3]/div/form/div[2]/div[2]/div[2]/ul/li/i'
        self.origin_item = r'/html/body/div[3]/div/form/div[2]/div[2]/div[2]/ul/li/a'

        self.object_type = r'//*[@class="propertyTable inlineEditEnabled"]/tbody[1]//td[contains(text(), "ObjectType")]/../td[2]'
        self.req_category = r'//td[contains(text(), "Req. Category:")]/../td[2]'
        self.special_verification = r'//td[contains(text(), "Special Verification Criteria:")]/../td[2]'
        self.verification_approach = r'//td[contains(text(), "Verification Approach:")]/../td[2]'

        # self.verification_approach_select = r'//*[@class="Verification Approach:"]/tbody[1]//td[contains(text(), "Req. Category:")]/../td[2]'
        self.special_verification_input = r'//td[contains(text(), "Special Verification Criteria:")]/../td[2]/div/div/div/div'
        self.req_category_input = r'//td[contains(text(), "Req. Category:")]/../td[2]/table/tbody/tr/td/div/ul/li/input'
        self.object_type_select = r'//select[@class="pixelResizeEditBox"]'

        self.copy = r'/html/body/ul/li[20]/a'
        self.insert_new_child = r'//*[contains(text(), "Insert a new Child Item (Ctrl + Insert)")]'
        self.new_item_after = r'//*[contains(text(), "Insert a new Item after this (Ctrl + Enter)")]'
        self.delete_item = r'//*[@class="vakata-context jstree-contextmenu jstree-default-contextmenu"]//a[text()="Delete…"]'
        self.input_content = r'//*[@class="editable new-item description-container editor-wrapper wysiwyg"]/div[2]/div/div'
        self.input_title = r'//*[@class="editable new-item description-container editor-wrapper wysiwyg"]/div/div/input'
        self.draft = '//*[text()="Draft"]'
        self.paint_button = '//*[@id="toolbarContainer"]/div/button[4]/i'
        # table
        self.insert_table = r'//span[text()="Insert Table"]/../i[1]'
        self.table_init_div = r'//*[@class="fr-select-table-size"]/span[1]/span[1]'
        self.tab_xpath = r'//*[@class="fr-select-table-size"]/span[$]/span[1]'
        self.tab_content = r'//*[@class="editable new-item description-container editor-wrapper wysiwyg"]/div[2]/div/div/table[1]/tbody[1]/tr[$0]/td[$1]'
        self.add_row_bt = r'//span[text()="Remove Table"]/../../button[2]'
        self.add_row_select = r'//a[text()="Insert row below"]'
        self.add_col_bt = r'//span[text()="Remove Table"]/../../button[3]'
        self.add_col_select = r'//a[text()="Insert column after"]'
        self.merge_bt = r'//span[text()="Remove Table"]/../../button[4]'
        self.select_merge = r'//a[text()="Merge cells"]'

        self.set_color_bt = r'//span[text()="Remove Table"]/../../button[5]'
        self.color_gray = r'//span[contains(text(), "Color #CCCCCC")]/..'
        # review
        self.review_name = r'/html/body/div[3]/div/div[1]/table/tbody/tr/td[2]/span'
        self.review_info = r'//*[@class="viewsMenu"]/a[3]'
        self.review_start_time = r'//*[@class="propertyTable"]/tbody/tr/td[2]/div/span'
        self.review_end_time = r'//*[@class="propertyTable"]/tbody/tr[4]/td[2]/span'
        self.review_new_item = r'//a[@title="Create a new item of this type."]/img'
        self.chose_moderator = r'//span[@title="Choose Review Moderator"]/a'
        self.search_moderator = r'//*[@id="ITEMFILTER"]'
        self.search_frame_name = r'inlinedPopupIframe'
        self.search_bt = r'//*[@id="searchButton"]'
        self.chose_bt = r'//*[@id="selectedUserIds1"]'
        self.search_confirm_bt = r'//*[@id="selectAssignedUsersForm"]/div[3]/input[1]'
        self.review_obj_type = r'//select[@id="dynamicChoice_references_1001"]'
        self.review_link_select = r'//*[@class="urlFieldQuery"]/div/table/tbody/tr/td[2]/span/a'
        self.review_link_label = r'//*[@id="customWikiLinkTabPane-tab"]'
        self.review_link_input = r'//*[@id="wikiLink"]'
        self.insert_link_bt = r'/html/body/div[1]/div[2]/input[1]'
        self.review_select_area = r'//*[@id="dynamicChoice_references_14"]'
        self.review_start_data = r'//*[text()="Review Start Date:"]/../../td[2]/input'
        self.review_end_data = r'//*[text()="Review Start Date:"]/../../td[4]/input'
        self.review_summary_input = r'//*[@id="summary"]'
        # review close
        self.close_get_link = r'//*[@class="propertyTable inlineEditEnabled"]/tbody/tr[5]/td[2]/span/a'
        self.close_feed_back = r'//a[@data-actionmenukey="feedback"]'
        self.feed_back_options = r'//*[@id="commentFilter"]'
        self.close_edit = r'//a[@title="Edit (Alt + E)"]/img'
        self.close_question = r'//*[text()="Num_RF_Question:"]/../../td[2]/input'
        self.close_problem = r'//*[text()="Num_RF_Problem:"]/../../td[2]/input'
        self.close_propose = r'//*[text()="Num_RF_Proposed Change:"]/../../td[2]/input'
        self.close_save = r'//input[@title="Save (Ctrl + S)"]'
        self.submit_close = r'//div[@id="item-transitions"]/a'

        self.user_check_err = r'//li[text()="Invalid user credentials!"]'
        self.user_check_ok = r'//a[text()="Reports"]'
        self.have_been_saved = r'//div[text()="Your changes have been successfully saved!"]'




