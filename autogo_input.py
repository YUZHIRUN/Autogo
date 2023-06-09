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
                line_type = re.search(regular.st_item, st_line).group(1)
            except Exception:
                line_type = 'None'
            try:
                line_var = re.search(regular.st_item, st_line).group(2)
            except Exception:
                line_var = 'None'
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
    global_var_types = list()
    for var in generate_code.g_global_var_list:
        try:
            var_type = re.search(regular.global_var_type, var).group(1)
        except Exception:
            var_type = 'None'
        global_var_types.append(var_type)
    g_global_var.append(var_names)
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


def clear_information():
    g_include_item.clear()
    g_local_func.clear()
    g_global_func.clear()
    g_struct.clear()
    g_enum.clear()
    g_union.clear()
    g_macro.clear()
    g_global_var.clear()


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
