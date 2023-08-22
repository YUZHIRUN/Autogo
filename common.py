import re
import regular_expression
import function_phrase_proc
import loop_phrase_proc
import other_phrase_proc

regular = regular_expression.RegularClass()
g_tab_scale = 4


# def get_tab_scale(file_content: str):
#     global g_tab_scale
#     if re.search(regular.tab_scale, file_content) is not None:
#         g_tab_scale = 2
#     else:
#         g_tab_scale = 4


def while_phrase_line_proc(content: str):
    res = content
    while_list = re.findall(regular.while_common, content)
    while_num = len(while_list)
    while True:
        if while_num == 0:
            break
        for idx in range(while_num):
            while_phrase: str = while_list[idx]
            if while_phrase.count('\n') == 0:
                continue
            while_new_phrase = while_phrase.replace('\n', ' ')
            while_new_phrase = re.sub(regular.del_space, ' ', while_new_phrase)
            res = res.replace(while_phrase, while_new_phrase)
        break
    return res

def file_info_clean(content_str: str, mode='.c'):
    res = del_line_sign(content_str)
    res = res.expandtabs(tabsize=g_tab_scale)
    res = re.sub(regular.special_comment_sign, '//:', res)
    if re.search(regular.comment_1, res) is not None:
        res = re.sub(regular.comment_1, '', res)
    if re.search(regular.comment_2, res) is not None:
        res = re.sub(regular.comment_2, '', res)
    if re.search(regular.comment_3, res) is not None:
        res = re.sub(regular.comment_3, '', res)
    if re.search(regular.comment_4, res) is not None:
        res = re.sub(regular.comment_4, '', res)
    res = pointer_space_proc(res)
    res = del_line_sign(res)
    res = while_phrase_line_proc(res)
    if mode == '.c':
        if re.search(regular.compile_macro, res) is not None:
            res = re.sub(regular.compile_macro, '', res)
        res = del_line_sign(res)
    return res


def pointer_space_proc(content_str: str):
    res = re.sub(regular.pointer_space, '* ', content_str)
    return res


def str_index_rep(input_str: str, obj_s, mode='f'):
    res = None
    while True:
        f_index = input_str.find(obj_s)
        l_index = input_str.rfind(obj_s)
        if f_index == len(input_str) - 1 or l_index == len(input_str) - 1:
            break
        if f_index == -1 or l_index == -1:
            break
        else:
            if mode == 'f':
                res = input_str[:f_index] + '' + input_str[f_index + 1:]
            if mode == 'l':
                res = input_str[:l_index] + '' + input_str[l_index + 1:]
        break
    return res


def del_line_sign(obj_str: str):
    """
    delete \n
    :param obj_str:
    :return:
    """
    res = re.sub(regular.new_line, '\n', obj_str)
    return res

def del_if_line_proc(obj_str: str):
    res = obj_str
    obj = re.search(regular.del_if_line, obj_str)
    if obj is not None:
        if_flag = str(re.search(regular.del_if_line, obj_str).group(1))
        res = re.sub(regular.del_if_line, (if_flag + ' '), obj_str)
    return res

def clear_number_sign(input_str: str):
    res = input_str.strip()
    res = res.replace('UL', '')
    res = res.replace('ul', '')
    res = res.replace('Ul', '')
    res = res.replace('uL', '')
    res = res.replace('U', '')
    res = res.replace('u', '')
    return res


def del_line_and_space(obj_str: str):
    """
    delete \n
    :param obj_str:
    :return:
    """
    res = re.sub(regular.new_line_space, '\n', obj_str)
    return res


def st_en_un_del_useless(obj_list):
    res_list = list()
    for e in obj_list:
        e = del_line_and_space(e)
        res_list.append(e)
    return res_list


def func_useless_del(obj_str: str):
    tab_proc = obj_str.expandtabs(tabsize=g_tab_scale)
    phrase_list = tab_proc.split('\n')
    phrase_num = len(phrase_list)
    for phrase_idx in range(phrase_num):
        del_space = phrase_list[phrase_idx].strip()
        phrase_list[phrase_idx] = del_space
    res = '\n'.join(phrase_list)
    res = del_line_sign(res)
    return res


def span_depth(input_str: str):
    space_num = 0
    idx = 0
    while input_str[idx] == ' ':
        space_num = space_num + 1
        idx = idx + 1
    depth = int(idx / g_tab_scale)
    return depth


def global_var_data_clear(var_list: list):
    res_list = list()
    for g_var in var_list:
        g_var = file_info_clean(g_var)
        res_list.append(g_var)
    return res_list


def get_local_func_name(func_str: str):
    first_line = func_str.split('\n')[0]
    func_head = first_line.strip()
    func_get = re.search(regular.local_func_name, func_head)
    if func_get is not None:
        func_name = func_get.group(1)
    else:
        func_name = ''
    func_name = func_name.replace('*', '')
    func_name = func_name.strip()
    return func_name


def get_global_func_name(func_str: str):
    first_line = func_str.split('\n')[0]
    func_head = first_line.strip()
    func_get = re.search(regular.global_func_name, func_head)
    if func_get is not None:
        func_name = func_get.group(1)
    else:
        func_name = ''
    func_name = func_name.replace('*', '')
    func_name = func_name.strip()
    return func_name


def get_global_func_names(global_func_list: list):
    name_list = list()
    for func_idx in global_func_list:
        func_name = get_global_func_name(func_idx)
        name_list.append(func_name)
    return name_list


def get_local_func_names(local_func_list: list):
    name_list = list()
    for func_idx in local_func_list:
        func_name = get_local_func_name(func_idx)
        name_list.append(func_name)
    return name_list


def get_struct_names(struct_list: list):
    name_list = list()
    for struct_idx in struct_list:
        struct: str = struct_idx.split('\n')[-1]
        struct = struct.replace('}', '')
        struct = struct.replace(';', '')
        struct_name = struct.strip(' ')
        name_list.append(struct_name)
    return name_list


def get_enum_names(enum_list: list):
    name_list = get_struct_names(enum_list)
    return name_list


def get_union_names(union_list: list):
    name_list = get_struct_names(union_list)
    return name_list


def get_macro_names(macro_list: list):
    name_list = list()
    for macro_idx in macro_list:
        macro = re.search(regular.get_macro_name, macro_idx)
        if macro is not None:
            name = macro.group(1)
            name_list.append(name)
    return name_list


def get_global_var_names(global_var_list: list):
    name_list = list()
    for var_idx in global_var_list:
        var = re.search(regular.global_var_type_name, var_idx)
        if var is not None:
            name = var.group(2)
        else:
            name = 'None'
        name_list.append(name)
    return name_list


def get_global_var_types(global_var_list: list):
    type_list = list()
    for var_idx in global_var_list:
        var = re.search(regular.global_var_type_name, var_idx)
        if var is not None:
            var_type = var.group(1)
        else:
            var_type = 'None'
        type_list.append(var_type)
    return type_list


def phrase_check(input_str: str):
    phrase_property = None
    wait_check_str = input_str.strip()
    while True:
        if wait_check_str.find('/') == 0:
            break
        if re.match(regular.break_re, wait_check_str) is not None:
            phrase_property = 'break'
            break
        if re.match(regular.continue_re, wait_check_str) is not None:
            phrase_property = 'continue'
            break
        if re.search(regular.if_re, wait_check_str) is not None:
            phrase_property = 'if'
            break
        if re.match(regular.for_re, wait_check_str) is not None:
            phrase_property = 'for'
            break
        if re.match(regular.while_re, wait_check_str) is not None and input_str.count('}') == 0:
            phrase_property = 'while'
            break
        if re.match(regular.do_re, wait_check_str) is not None or wait_check_str == 'do':
            phrase_property = 'do'
            break
        if re.match(regular.switch_re, wait_check_str) is not None:
            phrase_property = 'switch'
            break
        if re.match(regular.return_re, wait_check_str) is not None:
            phrase_property = 'return'
            break
        if re.match(regular.define_var_init, wait_check_str) is not None:
            phrase_property = 'define_var_init'
            break
        if re.match(regular.set_value_re, wait_check_str) is not None:
            phrase_property = 'set_value'
            break
        if re.match(regular.define_var_re, wait_check_str) is not None:
            phrase_property = 'define_var'
            break
        if re.match(regular.func_re, wait_check_str) is not None:
            phrase_property = 'function'
            break
        if re.match(regular.macro_call, wait_check_str) is not None:
            phrase_property = 'macro_call'
        break
    return phrase_property


def pack_func_info(func_input: str):
    task_list = list()
    func_list = func_input.split('\n')
    func_list = func_list[2:-1]
    for line in func_list:
        if phrase_check(line) is not None:
            depth = span_depth(line)
            line = line.strip()
            prop = phrase_check(line)
            content = line
            task = dict()
            task['depth'] = depth
            task['prop'] = prop
            task['content'] = content
            task_list.append(task)
    return task_list


def depth_set(input_str: str, depth):
    tab_line = ''
    if depth > 1:
        for i in range(depth - 1):
            tab_line = tab_line + '__'
    if input_str.count('\n') == 0:
        res = tab_line + input_str
    else:
        res = tab_line + input_str
        res = res.replace('\n', '\n' + tab_line)
    return res


def property_map(task: dict):
    res = ''
    if task['prop'] == 'break':
        res = other_phrase_proc.break_phrase_proc()
        res = depth_set(res, task['depth'])
    if task['prop'] == 'continue':
        res = other_phrase_proc.continue_phrase_proc()
        res = depth_set(res, task['depth'])
    if task['prop'] == 'if':
        res = 'if'
    if task['prop'] == 'for':
        res = loop_phrase_proc.for_phrase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'while':
        res = loop_phrase_proc.while_phrase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'do':
        res = loop_phrase_proc.do_phrase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'switch':
        res = other_phrase_proc.switch_phrase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'return':
        res = other_phrase_proc.return_phrase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'define_var_init':
        res = other_phrase_proc.define_var_init_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'set_value':
        res = other_phrase_proc.set_value_phrase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'define_var':
        res = other_phrase_proc.define_var_phrase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'function':
        res = function_phrase_proc.func_process(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'macro_call':
        res = other_phrase_proc.macro_call_proc(task['content'])
        res = depth_set(res, task['depth'])
    return res


def if_prop_map(if_phrase, task):
    res = depth_set(if_phrase, task['depth'])
    return res

def get_comment(obj_list):
    content_list = list()
    comment_list = list()
    for obj in obj_list:
        comment_obj = re.search(regular.special_comment, obj)
        if comment_obj is not None:
            comment = str(comment_obj.group(1))
            content = obj.replace(comment, '')
            content = content.strip()
            comment = re.sub(regular.clean_special_comment, '', comment)
            comment = comment.strip()
        else:
            comment = ''
            content = obj
        comment_list.append(comment)
        content_list.append(content)
    return content_list, comment_list

def st_en_un_get_comment(obj_list):
    content_list = list()
    comment_list = list()
    for obj in obj_list:
        item = re.sub(regular.struct_head, '', obj)
        item = re.sub(regular.struct_tail, '', item)
        items = item.split('\n')
        contents, comments = get_comment(items)
        comment_list.append(comments)
        item_content = re.sub(regular.special_comment, '', obj)
        content_list.append(item_content)
    return content_list, comment_list


def get_global_value(global_var_list):
    value_list = list()
    for var in global_var_list:
        try:
            val = re.search(regular.get_global_value, var).group(1)
        except Exception:
            val = ''
        if val is None:
            val = ''
        val = re.sub(regular.var_class, '', val)
        val = re.sub(regular.del_space, ' ', val)
        val = del_line_sign(val)
        val = val.strip('\n')
        val = val.strip()
        value_list.append(val)
    return value_list