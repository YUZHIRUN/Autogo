import re
import regular_expression
import error_code
import common

err = error_code.err_class()
name_re = regular_expression.variables_class()
regular = regular_expression.RegularClass()
g_file_content = ''
g_variable_type = {'uint8': name_re.uint8, 'sint8': name_re.sint8, 'uint16': name_re.uint16, 'sint16': name_re.sint16,
                   'uint32': name_re.uint32, 'uint64': name_re.uint64, 'float32': name_re.float32,
                   'float64': name_re.float64, 'boolean': name_re.boolean}


def get_type(input_type: str):
    type_list = list(g_variable_type.keys())
    if type_list.count(input_type) != 0:
        ret = g_variable_type[input_type]
    else:
        ret = 'ST_'
    return ret


def variable_proc(variable_list: list, mode='v1'):
    global g_file_content
    if mode == 'v1':
        for def_phase in variable_list:
            v_type: str = re.search(regular.get_variable1, def_phase).group(1)
            value: str = re.search(regular.get_variable1, def_phase).group(2)
            type_pr = get_type(v_type)
            if value.count('[') != 0:
                new_name = name_re.arr + type_pr + value
                # g_file_content.replace(value, new_name)
            elif def_phase.count('*') != 0:
                new_name = name_re.pointer + type_pr + value
            else:
                new_name = type_pr + value
            g_file_content = g_file_content.replace(value, new_name)


def struct_proc(struct_list: list):
    global g_file_content
    struct_names = common.get_struct_names(struct_list)
    for struct_name in struct_names:
        new_name = name_re.struct + struct_name
        g_file_content = g_file_content.replace(struct_name, new_name)


def enum_proc(enum_list: list):
    global g_file_content
    enum_names = common.get_enum_names(enum_list)
    for enum_name in enum_names:
        new_name = name_re.enum + enum_name
        g_file_content = g_file_content.replace(enum_name, new_name)


def rename_proc(file_path):
    ret = err.ok
    global g_file_content
    if file_path.endswith('.h') is True:
        file_mode = '.h'
    else:
        file_mode = '.c'
    with open(file_path, mode='r', encoding='UTF-8') as file_obj:
        g_file_content = file_obj.read()
        common.get_tab_scale(g_file_content)
        func_str = common.file_useless_info_del(g_file_content, mode=file_mode)
        if re.search(regular.variable1, func_str) is not None:
            variables = re.findall(regular.variable1, func_str)
            variable_proc(variables, mode='v1')

        if re.search(regular.variable2, func_str) is not None:
            variables = re.findall(regular.variable2, func_str)
            variable_proc(variables, mode='v2')

        if re.search(regular.struct, func_str) is not None:
            structs = re.findall(regular.struct, func_str)
            struct_proc(structs)

        if re.search(regular.enum, func_str) is not None:
            enums = re.findall(regular.enum, func_str)
            enum_proc(enums)

    with open(file_path, mode='w', encoding='UTF-8') as file_obj_w:
        new_content = g_file_content
        file_obj_w.write(new_content)
    return ret
