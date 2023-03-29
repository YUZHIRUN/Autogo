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
g_new_content = ''


def clean_data(input_str: str):
    variable = input_str.replace(',', '')
    variable = variable.replace(';', '')
    variable = variable.replace(')', '')
    variable = variable.strip()
    variable = variable + ';'
    return variable


def upper_name(input_str: str):
    if input_str.count('_') != 0:
        obj_list = input_str.split('_')
        op_obj: str = obj_list[1]
        op_obj_head = op_obj[0]
        op_obj_body = op_obj[1:]
        op_obj_head = op_obj_head.upper()
        op_obj = op_obj_head + op_obj_body
        obj_list[1] = op_obj
        res = '_'.join(obj_list)
    else:
        res = input_str
    return res


def comb_value(type_pre: str, obj_value, def_phase):
    global g_new_content
    if name_re.has_add_pre(type_pre + name_re.link, obj_value) is False:
        if name_re.is_array(obj_value) is True and name_re.is_ptr(def_phase) is True:
            name_pre = name_re.pointer + name_re.arr + type_pre + name_re.link
            new_name = name_pre + obj_value
        elif name_re.is_array(obj_value) is False and name_re.is_ptr(def_phase) is True:
            name_pre = name_re.pointer + type_pre + name_re.link
            new_name = name_pre + obj_value
        elif name_re.is_array(obj_value) is True and name_re.is_ptr(def_phase) is False:
            name_pre = name_re.arr + type_pre + name_re.link
            new_name = name_pre + obj_value
        else:
            name_pre = type_pre + name_re.link
            new_name = name_pre + obj_value
        new_name = upper_name(new_name)
    else:
        new_name = upper_name(obj_value)
    rep_reg = regular.any_find(obj_value)
    g_new_content = re.sub(rep_reg, new_name, g_new_content)


def get_type(input_type: str, value: str, pos='inner'):
    type_list = list(g_variable_type.keys())
    if type_list.count(input_type) != 0:
        ret = g_variable_type[input_type]
    else:
        if pos == 'inner':
            test1_str = value + '.'
            test2_str = value + '['
            if g_new_content.count(test1_str) != 0 or g_new_content.count(test2_str) != 0:
                ret = name_re.struct
            else:
                ret = ''
        else:
            ret = name_re.struct
    return ret


def variable_proc(variable_list: list, pos='inner'):
    global g_new_content
    for def_phase in variable_list:
        def_phase = clean_data(def_phase)
        if def_phase.count('return') != 0:
            continue
        else:
            obj_type: str = re.search(regular.get_variable, def_phase).group(1)
            obj_value: str = re.search(regular.get_variable, def_phase).group(2)
            type_pre = get_type(obj_type, obj_value, pos=pos)
            comb_value(type_pre, obj_value, def_phase)


def struct_proc(struct_list: list):
    global g_new_content
    struct_names = common.get_struct_names(struct_list)
    for struct_name in struct_names:
        pre_name = name_re.def_struct + name_re.link
        if struct_name.count(pre_name) == 0:
            new_name = pre_name + struct_name
            rep_reg = regular.any_find(struct_name)
            g_new_content = re.sub(rep_reg, new_name, g_new_content)


def enum_proc(enum_list: list):
    global g_new_content
    enum_names = common.get_enum_names(enum_list)
    for enum_name in enum_names:
        pre_name = name_re.def_enum + name_re.link
        if enum_name.count(pre_name) == 0:
            new_name = pre_name + enum_name
            rep_reg = regular.any_find(enum_name)
            g_new_content = re.sub(rep_reg, new_name, g_new_content)


def union_proc(union_list: list):
    global g_new_content
    union_names = common.get_union_names(union_list)
    for union_name in union_names:
        pre_name = name_re.def_union + name_re.link
        if union_name.count(pre_name) == 0:
            new_name = pre_name + union_name
            rep_reg = regular.any_find(union_name)
            g_new_content = re.sub(rep_reg, new_name, g_new_content)


def st_e_un_proc(file_content: str):
    if re.search(regular.struct, file_content) is not None:
        structs = re.findall(regular.struct, file_content)
        struct_proc(structs)

    if re.search(regular.enum, file_content) is not None:
        enums = re.findall(regular.enum, file_content)
        enum_proc(enums)

    if re.search(regular.union, file_content) is not None:
        unions = re.findall(regular.enum, file_content)
        union_proc(unions)


def rename_proc(file_path):
    ret = err.ok
    global g_new_content
    g_new_content = generate_code.g_file_content
    file_content = g_new_content
    file_type = generate_code.g_file_type
    common.get_tab_scale(file_content)
    file_content = common.file_useless_info_del(file_content, mode=file_type)
    if re.search(regular.variable, file_content) is not None:
        variables = re.findall(regular.variable, file_content)
        variable_proc(variables)

    st_e_un_proc(file_content)

    with open(file_path, mode='w', encoding='UTF-8') as file_obj_w:
        new_content = g_new_content
        file_obj_w.write(new_content)

    return ret
