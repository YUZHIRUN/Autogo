import generate_code
import draw_graph
import common
import regular_expression
import re
import copy
from copy import deepcopy

CleanContent = ''
g_branch_package = dict()
g_content_package = dict()
regular = regular_expression.graph_parse()


def get_phrase_depth(input_phrase: str):
    count = 0
    for i in input_phrase:
        if i == '_':
            count += 1
        else:
            break
    depth = int(count / 2) + 1
    return depth


def get_max_depth(input_content: str):
    max_depth = 0
    phrase_line = input_content.split('\n')
    for line in phrase_line:
        line_depth = get_phrase_depth(line)
        if line_depth > max_depth:
            max_depth = line_depth
    return max_depth


def var_declare_proc(input_code: str):
    define_var = re.search(regular.graph_define_var_del, input_code)
    if define_var is not None:
        define_phrase = 'Define variables\n'
    else:
        define_phrase = ''
    res_content = re.sub(regular.graph_define_var_del, '', input_code)
    res_content = define_phrase + res_content
    res_content = common.del_line_sign(res_content)
    return res_content


def set_start(input_content: str):
    return 'Start\n' + input_content


def if_phrase_proc(input_code: str):
    # code_list = input_code.split('\n')
    if_code_list = re.findall(regular.graph_if_condition, input_code)
    res_content = input_code
    if_idx = 0
    for code in if_code_list:
        depth = int(get_phrase_depth(code))
        condition = str(re.search(regular.graph_get_if_condition, if_code_list[if_idx]).group(1))
        condition = re.sub(regular.not_equal_to, ' != ', condition)
        condition = re.sub(regular.equal_to, ' == ', condition)
        condition = condition.replace('AND', '&&')
        condition = condition.replace('OR', '||')
        condition = re.sub(regular.change_line_depth, ' ', condition)
        condition = re.sub(regular.del_space, ' ', condition)
        # condition = condition.replace('\n', ' ')
        res = 'IF ' + condition
        res = common.depth_set(res, depth)
        res_content = res_content.replace(if_code_list[if_idx], res)
        if_idx += 1
    return res_content


def point_add(point: str) -> str:
    if point.count('.') != 0:
        point_list = point.split('.')
        point_list[-1] = str(int(point_list[-1]) + 1)
        point_res = '.'.join(point_list)
    else:
        point_res = str(int(point) + 1)
    return point_res


def point_insert(point: str):
    point_res = point + '.1'
    return point_res


def package_line_up(input_phrase_dict: dict):
    code_package = list()
    keys = list(input_phrase_dict.keys())
    length = len(keys)
    for i in range(length - 1, -1, -1):
        key = keys[i]
        package = input_phrase_dict[key]
        code_package.append(package)
    return code_package


def del_depth_sign(input_str: str):
    depth = get_phrase_depth(input_str)
    sign = ''
    for i in range(depth - 1):
        sign = sign + '__'
    res = input_str.replace(sign, '')
    return res


def func_call_process(input_str: str):
    if input_str.count('call the function ') != 0 or input_str.count('Call the function ') != 0:
        res = re.sub(regular.del_func_para, '', input_str)
        res = re.sub(regular.del_func_for, '', res)
        res = re.sub(regular.del_func_transmit, '', res)
    else:
        res = input_str
    return res


def clean_func_call(input_content: str):
    content_list = input_content.split('\n')
    new_list = list()
    for content in content_list:
        content = func_call_process(content)
        new_list.append(content)
    new_content = '\n'.join(new_list)
    return new_content


def clean_code_depth(code: str):
    res = del_depth_sign(code)
    res = res.strip()
    return res

def switch_clean_line(code: str):
    res = del_depth_sign(code)
    res = res.replace('switch ', '')
    res = res.replace('(', '')
    res = res.replace(')', '')
    res = res.replace('SWITCH:', '')
    res = res.replace('CASE:', '')
    res = res.strip()
    return res


def content_clean_line(code: str):
    res = del_depth_sign(code)
    res = func_call_process(res)
    res = res.strip()
    return res


def if_clean_line(code: str):
    res = del_depth_sign(code)
    res = res.replace('ELSE IF ', '', 1)
    res = res.replace('IF', '', 1)
    res = res.strip()
    return res


def while_clean_line(code: str):
    res = del_depth_sign(code)
    res = res.replace('WHILE', '', 1)
    res = res.strip()
    return res


def do_while_clean_line(code: str):
    res = del_depth_sign(code)
    if res.count('DO WHILE LOOP to break') != 0:
        res = 'FALSE TO BREAK'
    else:
        try:
            condition = re.search(regular.do_while_condition, res).group(1)
        except Exception:
            condition = 'None'
        res = condition
        res = res.strip()
    return res

def check_branch(line: str):
    obj = del_depth_sign(line)
    if obj.startswith('IF') is True or obj.startswith('FOR') is True or obj.startswith(
            'WHILE') is True or obj.startswith(
        'DO') is True or obj.startswith('SWITCH') is True or obj.startswith('switch') is True:
        return True
    else:
        return False


def switch_case_check(line: str):
    obj = del_depth_sign(line)
    if obj.startswith('CASE') is True or obj.startswith('DEFAULT') is True:
        return True
    else:
        return False


def else_if_check(line: str):
    obj = del_depth_sign(line)
    if obj.startswith('ELSE IF') is True:
        return True
    else:
        return False


def else_check(line: str):
    obj = del_depth_sign(line)
    if obj.startswith('ELSE THEN') is True:
        return True
    else:
        return False


def get_phrase_type(key_index):
    content = get_content(key_index)
    content_first: str = content.split('\n')[0]
    content_first_obj = del_depth_sign(content_first)
    content_first_obj = content_first_obj.strip()
    if content_first_obj.startswith('IF') is True:
        res = 'IF'
    elif content_first_obj.startswith('FOR') is True:
        res = 'FOR'
    elif content_first_obj.startswith('WHILE') is True:
        res = 'WHILE'
    elif content_first_obj.startswith('DO') is True:
        res = 'DO_WHILE'
    elif content_first_obj.startswith('SWITCH') is True or content_first_obj.startswith('CASE') is True or content_first_obj.startswith('switch') is True:
        res = 'SWITCH'
    else:
        res = 'content'
    return res


def get_content(index_key: str):
    global CleanContent, g_content_package, g_branch_package
    branch_dict = g_branch_package
    content_dict = g_content_package
    key_type = index_key.split('_')[0]
    key_var = index_key.split('_')[1]
    if key_type == 'branch':
        res = branch_dict[key_var]
    else:
        res = content_dict[key_var]
    return res


def get_level(index_key: str):
    level_idx = index_key.replace('branch_', '')
    level_idx = level_idx.replace('content_', '')
    level = level_idx.split('.')[0]
    level = int(level)
    return level


def branch_pack(input_content: str):
    max_depth = get_max_depth(input_content)
    line_list = input_content.split('\n')
    serial_line = list()
    branch_dict = dict()
    if_flag = False
    for depth in range(1, max_depth + 1):
        current_point = point_insert(str(depth))
        for line in line_list:
            current_depth = get_phrase_depth(line)
            if ((check_branch(line) is True or else_if_check(line) is True or else_check(
                    line) is True or switch_case_check(line) is True) and (
                        depth == current_depth)) or current_depth > depth:
                if check_branch(line) is True and depth == current_depth and if_flag is False:
                    if_flag = True
                    serial_line.append(line)
                    continue
                if if_flag is True and check_branch(line) is True and depth == current_depth:
                    if_flag = False
                    if line.count('DO WHILE') != 0:
                        serial_line.append(line)
                    else:
                        if len(serial_line) != 0:
                            content = '\n'.join(serial_line)
                            branch_dict[current_point] = content
                            current_point = point_add(current_point)
                            serial_line.clear()
                            serial_line.append(line)
                            if_flag = True
                        continue
                else:
                    serial_line.append(line)
            else:
                if len(serial_line) != 0:
                    content = '\n'.join(serial_line)
                    branch_dict[current_point] = content
                    current_point = point_add(current_point)
                    serial_line.clear()
                    if_flag = False
    return branch_dict


def content_pack(input_content: str):
    max_depth = get_max_depth(input_content)
    line_list = input_content.split('\n')
    serial_line = list()
    content_dict = dict()
    for depth in range(1, max_depth + 1):
        current_point = point_insert(str(depth))
        for line in line_list:
            current_depth = get_phrase_depth(line)
            if (check_branch(line) is False and else_if_check(line) is False and else_check(
                    line) is False and switch_case_check(line) is False) and current_depth == depth:
                serial_line.append(line)
            else:
                if len(serial_line) != 0:
                    content = '\n'.join(serial_line)
                    content_dict[current_point] = content
                    current_point = point_add(current_point)
                    serial_line.clear()
        if len(serial_line) != 0:
            content = '\n'.join(serial_line)
            content_dict[current_point] = content
            serial_line.clear()
    return content_dict


def phrase_pack(input_content: str) -> list:
    global g_branch_package, g_content_package
    branch_package = branch_pack(input_content)
    content_package = content_pack(input_content)
    g_branch_package = copy.copy(branch_package)
    g_content_package = copy.copy(content_package)
    branch_keys = list(branch_package.keys())
    content_keys = list(content_package.keys())
    remain_list = list()
    branch_idx = 0
    content_idx = 0
    max_depth = get_max_depth(input_content)
    line_list = input_content.split('\n')
    content_flag = 0
    branch_flag = 0
    new_branch_flag = False
    serial_id = list()
    phrase_dict = dict()
    for depth in range(1, max_depth + 1):
        current_point = str(depth)
        for line in line_list:
            current_depth = get_phrase_depth(line)
            if (check_branch(line) is False and else_if_check(line) is False and else_check(
                    line) is False and switch_case_check(line) is False) and current_depth == depth:
                content_flag = content_flag + 1
            else:
                if content_flag != 0:
                    serial_id.append('content_' + content_keys[content_idx])
                    content_idx += 1
                    content_flag = 0
            if ((check_branch(line) is True or else_if_check(line) is True or else_check(
                    line) is True or switch_case_check(line) is True) and (
                        depth == current_depth)) or current_depth > depth:
                if check_branch(line) is True and depth == current_depth and new_branch_flag is False:
                    new_branch_flag = True
                    branch_flag = branch_flag + 1
                    continue
                if new_branch_flag is True and check_branch(line) is True and depth == current_depth:
                    new_branch_flag = False
                    if line.count('DO WHILE') != 0:
                        branch_flag = branch_flag + 1
                        continue
                    if branch_flag != 0:
                        serial_id.append('branch_' + branch_keys[branch_idx])
                        branch_idx += 1
                        branch_flag = 1
                        new_branch_flag = True
                        continue
                else:
                    branch_flag = branch_flag + 1
            else:
                if branch_flag != 0:
                    serial_id.append('branch_' + branch_keys[branch_idx])
                    branch_idx += 1
                    branch_flag = 0
                    new_branch_flag = False
        if content_flag != 0:
            serial_id.append('content_' + content_keys[content_idx])
            content_idx += 1
            content_flag = 0
        if len(serial_id) != 0:
            temp_list = deepcopy(serial_id)
            phrase_dict[current_point] = temp_list
            serial_id.clear()
    for e in branch_keys:
        if e.startswith(str(max_depth - 1)) is True:
            element = 'branch_' + e
            remain_list.append(element)
    # phrase_dict[str(max_depth - 1)] = remain_list
    code_package = package_line_up(phrase_dict)
    return code_package


def task_merge(task_list: list):
    content = CleanContent
    fifo = list()
    for task in task_list:
        key_list = list()
        code_pack = list()
        task_num = len(task)
        i = 0
        while i < task_num:
            task_key = task[i]
            task_content = get_content(task_key)
            code_pack.append(task_content)
            check_code = '\n'.join(code_pack)
            if content.count(check_code) != 0:
                key_list.append(task_key)
                if i == task_num - 1:
                    temp = deepcopy(key_list)
                    fifo.append(temp)
                    key_list.clear()
                    code_pack.clear()
                    break
                else:
                    i = i + 1
            else:
                temp = deepcopy(key_list)
                fifo.append(temp)
                key_list.clear()
                code_pack.clear()
    return fifo

def error_else_then_proc(input_code: str):
    code_list = input_code.split('\n')
    code_list_len = len(code_list)
    code_idx = 0
    while code_idx < code_list_len:
        else_then_check = re.search(regular.error_else_then, code_list[code_idx])
        if else_then_check is not None:
            current_depth = get_phrase_depth(code_list[code_idx])
            next_depth = get_phrase_depth(code_list[code_idx + 1])
            if next_depth <= current_depth:
                del code_list[code_idx]
                code_idx = 0
                code_list_len = len(code_list)
            else:
                code_idx += 1
        else:
            code_idx += 1
    res = '\n'.join(code_list)
    return res

def switch_depth_adjustment(input_code: str):
    code_list =input_code.split('\n')
    code_list_len = len(code_list)
    idx = 0
    switch_depth = 0
    switch_start_flag = False
    default_flag = True
    while idx < code_list_len:
        code_line = code_list[idx]
        if del_depth_sign(code_line).startswith('SWITCH') is True or del_depth_sign(code_line).startswith('switch') is True:
            switch_depth = get_phrase_depth(code_line)
            default_flag = False
            switch_start_flag = True
            idx += 1
            continue
        if del_depth_sign(code_line).startswith('CASE') is True and default_flag is False and switch_start_flag is True:
            case_depth = get_phrase_depth(code_line)
            case = del_depth_sign(code_line)
            case = common.depth_set(case, switch_depth)
            code_list[idx] = case
            idx += 1
        elif del_depth_sign(code_line).startswith('DEFAULT') is True and default_flag is False and switch_start_flag is True:
            default = del_depth_sign(code_line)
            default = common.depth_set(default, switch_depth)
            code_list[idx] = default
            default_flag = True
            idx += 1
        elif default_flag is True and switch_start_flag is True:
            current_depth = get_phrase_depth(code_line)
            if current_depth > switch_depth + 1:
                content = del_depth_sign(code_line)
                content = common.depth_set(content, current_depth - 1)
                code_list[idx] = content
                if del_depth_sign(code_line).startswith('BREAK') is True:
                    break
                else:
                    idx += 1
            else:
                idx += 1
        elif switch_start_flag is True:
            current_depth = get_phrase_depth(code_line)
            if current_depth > switch_depth + 1:
                content = del_depth_sign(code_line)
                content = common.depth_set(content, current_depth - 1)
                code_list[idx] = content
                idx += 1
            else:
                idx += 1
                continue
        else:
            idx += 1
            continue
    res = '\n'.join(code_list)
    return res

def wash_code(input_code: str):
    code_content = var_declare_proc(input_code)
    code_content = if_phrase_proc(code_content)
    code_content = set_start(code_content)
    code_content = clean_func_call(code_content)
    code_content = re.sub(regular.del_space, ' ', code_content)
    code_content = error_else_then_proc(code_content)
    code_content = switch_depth_adjustment(code_content)
    code_content = common.del_line_sign(code_content)
    return code_content


def phrase_process(input_code):
    global CleanContent
    code_content = wash_code(input_code)
    CleanContent = code_content
    phrase_task = phrase_pack(code_content)
    fifo = task_merge(phrase_task)
    return fifo

#
if __name__ == '__main__':
    with open('_test/test_1.txt', 'r') as obj:
        content = obj.read()
        xml_info = draw_graph.get_graph_xml(content)
        # fifo = phrase_process(content)
        print(xml_info)
        input()
