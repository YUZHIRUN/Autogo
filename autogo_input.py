import generate_code
import common
import re
import regular_expression

regular = regular_expression.RegularClass()

g_include_item = list()  # (include)
g_local_func = list()  # (name)
g_global_func = list()  # (name)
g_struct = list()  # (name, type, var)
g_enum = list()  # (name, item, value)
g_union = list()  # (name, type, var)
g_global_var = list()  # (global_var, type)
g_macro = list()  # (name, value)

g_local_func_prototype = list()
g_global_func_prototype = list()


def del_duplicate_element(input_list: list):
    res_list = list()
    res_list.extend(input_list)
    for e in res_list:
        if res_list.count(e) > 1:
            res_list.remove(e)
    for e in res_list:
        if res_list.count(e) > 1:
            res_list.remove(e)
    return res_list


def get_names():
    res_dict = dict()
    global_func_names = common.get_global_func_names(generate_code.g_global_func)
    local_func_names = common.get_local_func_names(generate_code.g_local_func)
    struct_names = common.get_struct_names(generate_code.g_struct_list)
    enum_names = common.get_enum_names(generate_code.g_enum_list)
    macro_names = common.get_macro_names(generate_code.g_macro_list)
    global_var_names = common.get_global_var_names(generate_code.g_global_var_list)
    union_names = common.get_union_names(generate_code.g_union_list)
    res_dict['global_func_names'] = global_func_names
    res_dict['local_func_names'] = local_func_names
    res_dict['struct_names'] = struct_names
    res_dict['enum_names'] = enum_names
    res_dict['macro_names'] = macro_names
    res_dict['global_var_names'] = global_var_names
    res_dict['union_names'] = union_names
    return res_dict


def detail_pro(func_type='local', func_idx=0):
    g_locals = generate_code.g_local_code_list
    g_globals = generate_code.g_global_code_list
    if func_type == 'local':
        res_content = g_locals[func_idx]
    else:
        res_content = g_globals[func_idx]
    return res_content


def include_pro():
    global g_include_item
    for include_item in generate_code.g_include_list:
        include_obj = re.search(regular.get_include_file, include_item)
        if include_obj is not None:
            include_file = include_obj.group(1)
        else:
            include_file = ''
        include_file = include_file.replace(r'"', '')
        include_file = include_file.replace(r'<', '')
        include_file = include_file.replace('>', '')
        g_include_item.append(include_file)
        g_include_item = del_duplicate_element(g_include_item)


def local_func_pro(local_func_names: list):
    global g_local_func
    g_local_func.extend(local_func_names)


def global_func_pro(global_func_names: list):
    global g_global_func
    g_global_func.extend(global_func_names)


def struct_proc(struct_names: list):
    struct_list: list = generate_code.g_struct_list
    struct_types = list()
    struct_vars = list()
    for struct in struct_list:
        struct_item = re.sub(regular.struct_head, '', struct)
        struct_item = re.sub(regular.struct_tail, '', struct_item)
        struct_item = struct_item.split('\n')
        types = list()
        variables = list()
        for st_line in struct_item:
            st_line = st_line.strip()
            try:
                line_type = str(re.search(regular.st_item, st_line).group(1))
                line_type = line_type.strip()
            except Exception:
                line_type = 'None'
            try:
                line_var = str(re.search(regular.st_item, st_line).group(2))
                line_var = line_var.strip()
            except Exception:
                line_var = 'None'
            if line_type.count('*') != 0 or line_var.count('*') != 0:
                line_var = line_var.replace('*', '')
                line_type = line_type.replace('*', '')
                line_type = line_type + '*'
            types.append(line_type)
            variables.append(line_var)
        struct_types.append(types)
        struct_vars.append(variables)
    g_struct.append(struct_names)
    g_struct.append(struct_types)
    g_struct.append(struct_vars)


def enum_proc(enum_names: list):
    enum_list: list = generate_code.g_enum_list
    enum_items = list()
    enum_vals = list()
    for enum in enum_list:
        enum = re.sub(regular.struct_head, '', enum)
        enum = re.sub(regular.struct_tail, '', enum)
        enum_lines = enum.split('\n')
        single_en_items = list()
        single_en_vals = list()
        item_val = '0'
        for enum_line in enum_lines:
            enum_line = enum_line.strip()
            try:
                line_item = re.search(regular.en_item, enum_line).group(1)
                if line_item is None:
                    line_item = 'None'
            except IndexError:
                line_item = 'None'
            get_item_val = re.search(regular.en_item, enum_line).group(3)
            if get_item_val is not None:
                get_item_val = common.clear_number_sign(str(get_item_val))
                if str(get_item_val).count('x') != 0 or str(get_item_val).count('X') != 0:
                    item_val = str(int(get_item_val, 16))
                else:
                    item_val = str(get_item_val)
            else:
                item_val = int(item_val)
            single_en_items.append(line_item)
            single_en_vals.append(item_val)
            item_val = str(int(item_val) + 1)
        enum_items.append(single_en_items)
        enum_vals.append(single_en_vals)
    g_enum.append(enum_names)
    g_enum.append(enum_items)
    g_enum.append(enum_vals)


def union_proc(union_names: list):
    union_list: list = generate_code.g_union_list
    union_types = list()
    union_vars = list()
    for union in union_list:
        union_item = re.sub(regular.struct_head, '', union)
        union_item = re.sub(regular.struct_tail, '', union_item)
        union_item = union_item.split('\n')
        types = list()
        variables = list()
        for st_line in union_item:
            st_line = st_line.strip()
            try:
                line_type = re.search(regular.st_item, st_line).group(1)
            except Exception:
                line_type = 'None'
            try:
                line_var = re.search(regular.st_item, st_line).group(2)
            except Exception:
                line_var = 'None'
            types.append(line_type)
            variables.append(line_var)
        union_types.append(types)
        union_vars.append(variables)
    g_union.append(union_names)
    g_union.append(union_types)
    g_union.append(union_vars)


def global_var_proc(var_names):
    global_var_types = common.get_global_var_types(generate_code.g_global_var_list)
    global_var_names = var_names
    var_len = len(global_var_names)
    for var_idx in range(var_len):
        if global_var_names[var_idx].count('*') != 0 or global_var_types[var_idx].count('*') != 0:
            global_var_names[var_idx] = global_var_names[var_idx].replace('*', '')
            global_var_types[var_idx] = global_var_types[var_idx].replace('*', '')
            global_var_types[var_idx] = global_var_types[var_idx] + '*'
    g_global_var.append(global_var_names)
    g_global_var.append(global_var_types)


def macro_proc(macro_names):
    macro_var_list = list()
    for macro in generate_code.g_macro_list:
        try:
            macro_var = re.search(regular.macro_value, macro).group(1)
        except Exception:
            macro_var = 'None'
        macro_var_list.append(macro_var)
    g_macro.append(macro_names)
    g_macro.append(macro_var_list)


def get_func_param(func_name, func_type='local'):
    res_list = list()
    params_mode = list()
    param_types = list()
    param_members = list()
    if func_type == 'local':
        local_functions = generate_code.g_local_func
        local_function_names = common.get_local_func_names(local_functions)
        try:
            func_idx = local_function_names.index(func_name)
        except Exception:
            func_idx = 0
        func_prototype = g_local_func_prototype[func_idx]
        func_param_info = str(re.search(regular.get_head_info, func_prototype).group(1))
        def_vars = func_param_info.split(',')
    else:
        global_functions = generate_code.g_global_func
        global_function_names = common.get_global_func_names(global_functions)
        try:
            func_idx = global_function_names.index(func_name)
        except Exception:
            func_idx = 0
        func_prototype = g_global_func_prototype[func_idx]
        func_param_info = str(re.search(regular.get_head_info, func_prototype).group(1))
        def_vars = func_param_info.split(',')
    for param in def_vars:
        if re.search(regular.global_func_params_0, param) is not None:
            params_mode.append('None')
            param_types.append('None')
            param_members.append('None')
            break
        elif re.search(regular.get_param_info, param) is not None:
            param_type = str(re.search(regular.get_param_info, param).group(1))
            param_var = str(re.search(regular.get_param_info, param).group(2))
            if str(param_type).count('*') == 0 and str(param_var).count('*') == 0:
                params_mode.append('input')
            else:
                params_mode.append('output')
                param_var = param_var.replace('*', '')
                param_type = param_type.replace('*', '')
                param_type = param_type + '*'
            param_types.append(param_type)
            param_members.append(param_var)
        else:
            params_mode.append('output')
            param_types.append('None')
            param_members.append('None')
            break
    res_list.append(params_mode)
    res_list.append(param_types)
    res_list.append(param_members)
    return res_list


def return_info_process(func_name: str, func_type='local'):
    """
    Get return type
    :param func_name:
    :param func_type:
    :return: 'None' or 'type@var'
    """
    if func_type == 'local':
        functions = generate_code.g_local_func
        function_names = generate_code.g_local_func_names
        try:
            func_idx = function_names.index(func_name)
        except Exception:
            func_idx = 0
        prototype = g_local_func_prototype[func_idx]
    else:
        functions = generate_code.g_global_func
        function_names = generate_code.g_global_func_names
        try:
            func_idx = function_names.index(func_name)
        except Exception:
            func_idx = 0
        prototype = g_global_func_prototype[func_idx]
    function_content = functions[func_idx]
    return_info = re.search(regular.get_return_info, function_content)
    if return_info is not None:
        return_var = return_info.group(1)
        return_var = str(return_var).strip()
        return_type = str(prototype).split(' ')[0]
        if return_type.count('*') != 0 or func_name.count('*') != 0:
            return_var = return_var.replace('*', '')
            return_type = return_type.replace('*', '')
            return_type = return_type + '*'
        return_info = str(return_type) + '@' + str(return_var)
    else:
        return_info = 'None'
    return return_info


def get_local_func_prototype():
    local_funcs = generate_code.g_local_func
    for local_func in local_funcs:
        prototype = local_func.split('\n')[0]
        g_local_func_prototype.append(prototype)


def get_global_func_prototype():
    funcs = generate_code.g_global_func
    for g_func in funcs:
        head_line = g_func.split('\n')[0]
        return_type = re.search(regular.get_global_func_info, head_line).group(1)
        func_name = re.search(regular.get_global_func_info, head_line).group(2)
        params_info = re.search(regular.get_global_func_info, head_line).group(3)
        params_list_check = re.search(regular.global_func_params, params_info)
        if params_list_check is not None:
            params = list()
            params_list = re.findall(regular.global_func_params, params_info)
            for param in params_list:
                if re.search(regular.global_func_params_0, param) is not None:
                    params.append('void')
                    break
                elif re.search(regular.global_func_params_1, param) is not None:
                    param_type = re.search(regular.global_func_params_1, param).group(1)
                    param_var = re.search(regular.global_func_params_1, param).group(2)
                    res = str(param_type) + ' ' + str(param_var)
                    params.append(res)
                elif re.search(regular.global_func_params_2, param) is not None:
                    res = re.search(regular.global_func_params_2, param).group(1)
                    params.append(res)
            param_res = '(' + ', '.join(params) + ')'
            prototype = str(return_type) + ' ' + func_name + param_res
        else:
            prototype = str(return_type) + ' ' + func_name + '(None)'
        g_global_func_prototype.append(prototype)


def get_func_prototype(func_name, func_type='local'):
    if func_type == 'local':
        func_names = generate_code.g_local_func_names
        try:
            func_idx = func_names.index(func_name)
        except Exception:
            func_idx = 0
        prototype = g_local_func_prototype[func_idx]
    else:
        func_names = generate_code.g_global_func_names
        try:
            func_idx = func_names.index(func_name)
        except Exception:
            func_idx = 0
        prototype = g_global_func_prototype[func_idx]
    return prototype


def get_unit_var(func_name, func_type='local'):
    """

    :param func_name:
    :param func_type:
    :return: (type@name)
    """
    global_vars = g_global_var[0]
    global_types = g_global_var[1]
    unit_names = list()
    unit_types = list()
    if func_type == 'local':
        functions = generate_code.g_local_func
        func_names = generate_code.g_local_func_names
    else:
        functions = generate_code.g_global_func
        func_names = generate_code.g_global_func_names
    try:
        func_idx = func_names.index(func_name)
    except Exception:
        func_idx = 0
    function = functions[func_idx]
    for e in global_vars:
        if function.count(e) != 0:
            var_idx = global_vars.index(e)
            var_type = global_types[var_idx]
            var_name = e
            unit_names.append(var_name)
            unit_types.append(var_type)
    return unit_types, unit_names


# def dynamic_call_get(func_name, func_type='local'):


def clear_information():
    g_include_item.clear()
    g_local_func.clear()
    g_global_func.clear()
    g_struct.clear()
    g_enum.clear()
    g_union.clear()
    g_macro.clear()
    g_global_var.clear()

    g_local_func_prototype.clear()
    g_global_func_prototype.clear()


def get_information():
    name_dict = get_names()
    clear_information()
    include_pro()
    global_func_pro(name_dict['global_func_names'])
    local_func_pro(name_dict['local_func_names'])
    struct_proc((name_dict['struct_names']))
    enum_proc(name_dict['enum_names'])
    macro_proc(name_dict['macro_names'])
    global_var_proc(name_dict['global_var_names'])
    union_proc(name_dict['union_names'])
    get_local_func_prototype()
    get_global_func_prototype()
