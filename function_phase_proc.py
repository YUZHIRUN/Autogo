import re
import regular_expression

regular = regular_expression.RegularClass()


def memcpy_func(input_str: str):
    obj_name = re.search(regular.memcpy, input_str).group(1)
    origin_name = re.search(regular.memcpy, input_str).group(2)
    res = 'Call the function memcpy for copy the values from ' + str(origin_name) + ' to ' + str(obj_name)
    # res = 'Call the function ' + input_str + 'for copy the values from ' + str(origin_name) + ' to ' + str(obj_name)
    return res


def memset_func(input_str: str):
    obj_name = re.search(regular.memset, input_str).group(1)
    res = 'Call the function memset for init the variable ' + str(obj_name)
    # res = 'Call the function ' + input_str + ' for init the variable ' + str(obj_name)
    return res


def get_value_func(input_str: str):
    func_name = re.search(regular.func_get_value, input_str).group(1)
    obj_name = re.search(regular.func_get_value, input_str).group(2)
    res = 'Call the function ' + str(func_name) + ' for get the value of ' + str(obj_name)
    # res = 'Call the function ' + input_str + ' for get the value of ' + str(obj_name)
    return res


def trans_value_func(input_str: str):
    func_name = re.search(regular.func_trans_value, input_str).group(1)
    obj_name = re.search(regular.func_trans_value, input_str).group(2)
    res = 'Call the function ' + str(func_name) + ' and transmit ' + str(obj_name) + ' to it'
    # res = 'Call the function ' + input_str + ' and transmit the ' + str(obj_name) + ' to it'
    return res


def common_func(input_str: str):
    func_name = re.search(regular.common_func, input_str).group(1)
    # res = 'Call the function ' + str(func_name)
    func = input_str.replace(';', '')
    res = 'Call the function ' + func
    return res


def common_point_func(input_str: str):
    func_name = re.search(regular.point_func, input_str).group(1)
    res = 'Call the function ' + str(func_name)
    return res


def func_process(func_phase: str):
    while True:
        try:
            if re.search(regular.memcpy, func_phase) is not None:
                res = memcpy_func(func_phase)
                break
            if re.search(regular.memset, func_phase) is not None:
                res = memset_func(func_phase)
                break
            if re.match(regular.func_get_value, func_phase) is not None:
                res = get_value_func(func_phase)
                break
            if re.match(regular.func_trans_value, func_phase) is not None:
                res = trans_value_func(func_phase)
                break
            if re.match(regular.common_func, func_phase) is not None:
                res = common_func(func_phase)
                break
            if re.match(regular.point_func, func_phase) is not None:
                res = common_point_func(func_phase)
            else:
                res = ''
        except Exception:
            res = ''
        break
    return res


def point_func_proc(func_line: list):
    for line_idx in func_line:
        point_func = re.search(regular.point_func, line_idx)
        if point_func is not None:
            point = point_func.group(1)
            info = ' the value obtained by the function ' + str(point)
            new_info = re.sub(regular.point_func, info, line_idx)
            index = func_line.index(line_idx)
            func_line[index] = new_info
    return func_line


def last_func_callback_proc(func_line_list: list):
    func_list = point_func_proc(func_line_list)
    for func_line_idx in func_list:
        condition_func = re.search(regular.last_func, func_line_idx)
        condition_funcs = re.findall(regular.last_func, func_line_idx)
        if condition_func is not None and (func_line_idx.startswith('IF') is True or func_line_idx.startswith('Set') is True):
            condition_name: str = re.search(regular.get_last_func, func_line_idx).group(1)
            if condition_name.count('IF') == 0 and condition_name.count('sizeof') == 0 and condition_name.count(
                    'OR') == 0 and condition_name.count('AND') == 0:
                info = 'the result of the function ' + condition_funcs[0]
                new_info = re.sub(regular.last_func, info, func_line_idx)
                index = func_list.index(func_line_idx)
                func_list[index] = new_info
    res = '\n'.join(func_list)
    res = res.replace('(void)', '')
    res = re.sub(regular.var_class, '', res)
    res = res + '\nEND'
    return res
