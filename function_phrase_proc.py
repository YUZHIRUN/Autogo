import re

import generate_code
import regular_expression

regular = regular_expression.RegularClass()


def memcpy_func(input_str: str):
    obj_name = re.search(regular.memcpy, input_str).group(1)
    origin_name = re.search(regular.memcpy, input_str).group(2)
    res = 'Call the memcpy function for copy the values from ' + str(origin_name) + ' to ' + str(obj_name)
    # res = 'Call the function ' + input_str + 'for copy the values from ' + str(origin_name) + ' to ' + str(obj_name)
    return res


def memset_func(input_str: str):
    obj_name = re.search(regular.memset, input_str).group(1)
    res = 'Call the memset function for init the variable ' + str(obj_name)
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
    func_res = func_name
    point_funcs_declare = generate_code.g_point_func_list
    for func in point_funcs_declare:
        if func.count(func_name) != 0:
            try:
                proto = re.search(regular.get_point_func_info, func).group(2)
                point_head = re.search(regular.point_func_head, input_str).group(1)
                func_res = input_str.replace(point_head, proto)
            except Exception:
                func_res = func_name
        else:
            func_res = func_name
    res = 'Call the function ' + str(input_str)
    return res


def func_process(func_phrase: str):
    while True:
        try:
            if re.search(regular.memcpy, func_phrase) is not None:
                res = memcpy_func(func_phrase)
                break
            if re.search(regular.memset, func_phrase) is not None:
                res = memset_func(func_phrase)
                break
            if re.match(regular.func_get_value, func_phrase) is not None:
                res = get_value_func(func_phrase)
                break
            if re.match(regular.func_trans_value, func_phrase) is not None:
                res = trans_value_func(func_phrase)
                break
            if re.match(regular.common_func, func_phrase) is not None:
                res = common_func(func_phrase)
                break
            if re.match(regular.point_func, func_phrase) is not None:
                res = common_point_func(func_phrase)
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
            point_name = point_func.group(1)
            func_res = point_name
            for e in generate_code.g_point_func_list:
                if e.count(point_name) != 0:
                    try:
                        # point_head = re.search(regular.point_func_head, line_idx).group(1)
                        point_params = re.search(regular.point_func_head, line_idx).group(2)
                        proto = re.search(regular.get_point_func_info, e).group(2)
                        func_res = proto + point_params
                    except Exception:
                        func_res = point_name
            if line_idx.count('Call the function') != 0:
                info = ' ' + str(func_res)
            else:
                info = ' the result of call the function ' + str(func_res)
            new_info = re.sub(regular.point_func, info, line_idx)
            index = func_line.index(line_idx)
            func_line[index] = new_info
    return func_line


def last_func_call_result(func_line: str):
    res_line = func_line
    obj_line = res_line.strip('_')
    call_func_phrase = re.search(regular.last_func, func_line)
    if call_func_phrase is not None and (
            obj_line.startswith('IF') is True or obj_line.startswith('Set') is True) and obj_line.count(
            'the result of') == 0:
        func_name = str(re.search(regular.get_last_func_name, obj_line).group(1))
        if func_name.count('IF') == 0 and func_name.count('size') == 0 and func_name.count(
                'OR') == 0 and func_name.count('AND') == 0:
            func_proto = re.findall(regular.last_func, obj_line)[0]
            info = 'the result of call function ' + func_proto
            res_line = res_line.replace(func_proto, info)
    return res_line


def last_func_callback_proc(func_line_list: list):
    func_list = point_func_proc(func_line_list)
    func_list_len = len(func_list)
    for func_line_idx in range(func_list_len):
        new_line = last_func_call_result(func_list[func_line_idx])
        func_list[func_line_idx] = new_line
    res = '\n'.join(func_list)
    res = res.replace('(void)', '')
    res = re.sub(regular.var_class, '', res)
    res = re.sub(regular.del_space, ' ', res)
    res = res + '\nEND'
    return res
