import re
import regular_expression
import function_phase_proc
import loop_phase_proc
import other_phase_proc

regular = regular_expression.RegularClass()
g_tab_scale = 4


def get_tab_scale(file_content: str):
    global g_tab_scale
    if re.search(regular.tab_scale, file_content) is not None:
        g_tab_scale = 2
    else:
        g_tab_scale = 4


def file_useless_info_del(content_str: str, mode='.c'):
    res = del_line_sign(content_str)
    res = res.expandtabs(tabsize=g_tab_scale)
    if re.search(regular.comment_1, res) is not None:
        res = re.sub(regular.comment_1, '', res)
    if re.search(regular.comment_2, res) is not None:
        res = re.sub(regular.comment_2, '', res)
    if re.search(regular.comment_3, res) is not None:
        res = re.sub(regular.comment_3, '', res)
    if re.search(regular.comment_4, res) is not None:
        res = re.sub(regular.comment_4, '', res)
    res = del_line_sign(res)
    if mode == '.c':
        if re.search(regular.compile_macro, res) is not None:
            res = re.sub(regular.compile_macro, '', res)
        res = del_line_sign(res)
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


def func_useless_del(obj_str: str):
    tab_proc = obj_str.expandtabs(tabsize=g_tab_scale)
    phase_list = tab_proc.split('\n')
    phase_num = len(phase_list)
    for phase_idx in range(phase_num):
        del_space = phase_list[phase_idx].strip()
        phase_list[phase_idx] = del_space
    res = '\n'.join(phase_list)
    res = del_line_sign(res)
    return res


# def tab_to_space(func_list: list, scale=g_tab_scale):
#     func_num = len(func_list)
#     for idx in range(func_num):
#         func_list[idx] = func_list[idx].expandtabs(tabsize=scale)
#     return func_list


def span_depth(input_str: str):
    space_num = 0
    idx = 0
    while input_str[idx] == ' ':
        space_num = space_num + 1
        idx = idx + 1
    depth = int(idx / g_tab_scale)
    return depth


def get_local_func_name(func_str: str):
    first_line = func_str.split('\n')[0]
    func_head = first_line.strip()
    func_get = re.search(regular.local_func_name, func_head)
    if func_get is not None:
        func_name = func_get.group(1)
    else:
        func_name = ''
    return func_name


def get_global_func_name(func_str: str):
    first_line = func_str.split('\n')[0]
    func_head = first_line.strip()
    func_get = re.search(regular.global_func_name, func_head)
    if func_get is not None:
        func_name = func_get.group(1)
    else:
        func_name = ''
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


def get_macro_names(macro_list: list):
    name_list = list()
    for macro_idx in macro_list:
        macro = re.search(regular.macro_name, macro_idx)
        if macro is not None:
            name = macro.group(1)
            name_list.append(name)
    return name_list


def get_global_var_names(global_var_list: list):
    name_list = list()
    for var_idx in global_var_list:
        var = re.search(regular.global_var_name, var_idx)
        if var is not None:
            name = var.group(1)
            name_list.append(name)
    return name_list


def phase_check(input_str: str):
    phase_property = None
    wait_check_str = input_str.strip()
    while True:
        if wait_check_str.find('/') == 0:
            break
        if re.match(regular.break_re, wait_check_str) is not None:
            phase_property = 'break'
            break
        if re.match(regular.continue_re, wait_check_str) is not None:
            phase_property = 'continue'
            break
        if re.match(regular.if_re, wait_check_str) is not None:
            phase_property = 'if'
            break
        if re.match(regular.for_re, wait_check_str) is not None:
            phase_property = 'for'
            break
        if re.match(regular.while_re, wait_check_str) is not None and input_str.count('}') == 0:
            phase_property = 'while'
            break
        if re.match(regular.do_re, wait_check_str) is not None or wait_check_str == 'do':
            phase_property = 'do'
            break
        if re.match(regular.switch_re, wait_check_str) is not None:
            phase_property = 'switch'
            break
        if re.match(regular.return_re, wait_check_str) is not None:
            phase_property = 'return'
            break
        if re.match(regular.set_value_re, wait_check_str) is not None:
            phase_property = 'set_value'
            break
        if re.match(regular.func_re, wait_check_str) is not None:
            phase_property = 'function'
            break
        break
    return phase_property


def pack_func_info(func_input: str):
    task_list = list()
    func_list = func_input.split('\n')
    func_list = func_list[2:-1]
    for line in func_list:
        if phase_check(line) is not None:
            depth = span_depth(line)
            line = line.strip()
            prop = phase_check(line)
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
        res = other_phase_proc.break_phase_proc()
        res = depth_set(res, task['depth'])
    if task['prop'] == 'continue':
        res = other_phase_proc.continue_phase_proc()
        res = depth_set(res, task['depth'])
    if task['prop'] == 'if':
        res = 'if'
    if task['prop'] == 'for':
        res = loop_phase_proc.for_phase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'while':
        res = loop_phase_proc.while_phase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'do':
        res = loop_phase_proc.do_phase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'switch':
        res = other_phase_proc.switch_phase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'return':
        res = other_phase_proc.return_phase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'set_value':
        res = other_phase_proc.set_value_phase_proc(task['content'])
        res = depth_set(res, task['depth'])
    if task['prop'] == 'function':
        res = function_phase_proc.func_process(task['content'])
        res = depth_set(res, task['depth'])
    return res


def if_prop_map(if_phase, task):
    res = depth_set(if_phase, task['depth'])
    return res
