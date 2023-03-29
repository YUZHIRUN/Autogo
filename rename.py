import re

import generate_code
import regular_expression
import error_code
import common

err = error_code.err_class()
name_re = regular_expression.variables_class()
regular = regular_expression.RegularClass()
g_variable_type = {'uint8': name_re.uint8, 'sint8': name_re.sint8, 'uint16': name_re.uint16, 'sint16': name_re.sint16,
                   'uint32': name_re.uint32, 'uint64': name_re.uint64, 'float32': name_re.float32,
                   'float64': name_re.float64, 'boolean': name_re.boolean}
g_functions = list()
g_new_content = ''


def get_type(input_type: str):
    type_list = list(g_variable_type.keys())
    if type_list.count(input_type) != 0:
        ret = g_variable_type[input_type]
    else:
        test_str = input_type + '.'
        if g_new_content.count(test_str) != 0:
            ret = name_re.struct
        else:
            ret = ''
    return ret


def variable_proc(variable_list: list, mode='v1'):
    global g_new_content
    if mode == 'v1':
        for def_phase in variable_list:
            if def_phase.count('return') == 0:
                v_type: str = re.search(regular.get_variable1, def_phase).group(1)
                value: str = re.search(regular.get_variable1, def_phase).group(2)
                type_pr = get_type(v_type)
                if name_re.has_add_pre(name_re.link, value) is False:
                    if name_re.is_array(value) is True and name_re.is_ptr(value) is True:
                        name_pre = name_re.pointer + name_re.arr + type_pr + name_re.link
                        new_name = name_pre + value
                        # g_file_content.replace(value, new_name)
                    elif name_re.is_array(value) is False and name_re.is_ptr(value) is True:
                        name_pre = name_re.pointer + type_pr + name_re.link
                        new_name = name_pre + value
                    elif name_re.is_array(value) is True and name_re.is_ptr(value) is False:
                        name_pre = name_re.arr + type_pr + name_re.link
                        new_name = name_pre + value
                    else:
                        name_pre = type_pr + name_re.link
                        new_name = name_pre + value
                    rep_reg = regular.any_find(value)
                    g_new_content = re.sub(rep_reg, new_name, g_new_content)


def struct_proc(struct_list: list):
    global g_new_content
    struct_names = common.get_struct_names(struct_list)
    for struct_name in struct_names:
        new_name = name_re.struct + struct_name
        rep_reg = regular.any_find(struct_name)
        g_new_content = re.sub(rep_reg, new_name, g_new_content)


def enum_proc(enum_list: list):
    global g_new_content
    enum_names = common.get_enum_names(enum_list)
    for enum_name in enum_names:
        new_name = name_re.enum + enum_name
        rep_reg = regular.any_find(enum_name)
        g_new_content = re.sub(rep_reg, new_name, g_new_content)


def union_proc(union_list: list):
    global g_new_content
    union_names = common.get_union_names(union_list)
    for union_name in union_names:
        new_name = name_re.union + union_name
        rep_reg = regular.any_find(union_name)
        g_new_content = re.sub(rep_reg, new_name, g_new_content)


def st_e_un_proc(file_content: str, file_type: str):
    common.get_tab_scale(file_content)
    func_str = common.file_useless_info_del(file_content, mode=file_type)

    if re.search(regular.struct, func_str) is not None:
        structs = re.findall(regular.struct, func_str)
        struct_proc(structs)

    if re.search(regular.enum, func_str) is not None:
        enums = re.findall(regular.enum, func_str)
        enum_proc(enums)

    if re.search(regular.union, func_str) is not None:
        unions = re.findall(regular.enum, func_str)
        union_proc(unions)


def rename_proc(file_path):
    ret = err.ok
    global g_new_content
    g_new_content = generate_code.g_file_content
    g_functions.extend(generate_code.g_global_func)
    g_functions.extend(generate_code.g_local_func)
    file_content = generate_code.g_file_content
    file_type = generate_code.g_file_type
    for funcs in g_functions:

        if re.search(regular.variable1, funcs) is not None:
            variables = re.findall(regular.variable1, funcs)
            variable_proc(variables, mode='v1')
        # if re.search(regular.variable2, func_str) is not None:
        #     variables = re.findall(regular.variable2, func_str)
        #     variable_proc(variables, mode='v2')
    st_e_un_proc(file_content, file_type)
    with open(file_path, mode='w', encoding='UTF-8') as file_obj_w:
        new_content = g_new_content
        file_obj_w.write(new_content)

    return ret
