import re

memcpy_regular = r'[\(void\)]*memcpy *\(&*(\S+?),\n* *&*(\S+?),\n*.+\);'
memset_regular = r'[\(void\)]* *memset\(&*(\S+?),\n*.+?, *\n*.+?\);'
get_value_func_regular = r'[\(void\)]*(\S+?)\(&(\S+)\);'
trans_value_func_regular = r'[\(void\)]*(\S+?)\((\S+)\);'
common_function_regular = r'[\(void\)]* *([\w]+?)\(.*?\);'
point_function_regular = r'\( *\* *(\w+)\)\(&*.+\)'


def memcpy_func(input_str: str):
    obj_name = re.search(memcpy_regular, input_str).group(1)
    origin_name = re.search(memcpy_regular, input_str).group(2)
    res = 'Call the function memcpy for copy the values from ' + str(origin_name) + ' to ' + str(obj_name)
    return res


def memset_func(input_str: str):
    obj_name = re.search(memset_regular, input_str).group(1)
    res = 'Call the function memset for init the variable ' + str(obj_name)
    return res


def get_value_func(input_str: str):
    func_name = re.search(get_value_func_regular, input_str).group(1)
    obj_name = re.search(get_value_func_regular, input_str).group(2)
    res = 'Call the function ' + str(func_name) + ' for get the value of ' + str(obj_name)
    return res


def trans_value_func(input_str: str):
    func_name = re.search(trans_value_func_regular, input_str).group(1)
    obj_name = re.search(trans_value_func_regular, input_str).group(2)
    res = 'Call the function ' + str(func_name) + ' and transmit the ' + str(obj_name) + ' to it'
    return res


def common_func(input_str: str):
    func_name = re.search(common_function_regular, input_str).group(1)
    res = 'Call the function ' + str(func_name)
    return res


def func_process(func_phase: str):
    while True:
        try:
            if re.match(memcpy_regular, func_phase) is not None:
                res = memcpy_func(func_phase)
                break
            if re.match(memset_regular, func_phase) is not None:
                res = memset_func(func_phase)
                break
            if re.match(get_value_func_regular, func_phase) is not None:
                res = get_value_func(func_phase)
                break
            if re.match(common_function_regular, func_phase) is not None:
                res = common_func(func_phase)
                break
            else:
                res = ''
        except Exception:
            res = ''
        break
    return res


def point_func_proc(func_line: list):
    for line_idx in func_line:
        point_func = re.search(point_function_regular, line_idx)
        if point_func is not None:
            point = point_func.group(1)
            info = 'The value obtained by the function ' + str(point)
            new_info = re.sub(point_function_regular, info, line_idx)
            index = func_line.index(line_idx)
            func_line[index] = new_info
    res = '\n'.join(func_line)
    res = res + '\nEND'
    return res
