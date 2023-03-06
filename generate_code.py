import re
import common
import error_code
import function_phase_proc
import if_phase_proc

g_global_func = list()
g_local_func = list()
g_struct_list = list()
g_enum_list = list()
g_macro_list = list()
g_global_var_list = list()

g_global_code_list = list()
g_local_code_list = list()

errcode = error_code.err_class()


def load_file(file_path):
    global_regular = r'FUNC *\(.+\n\{\n(?:[\t| +|/].*\n)+\}'
    local_func_regular = r'(?:static )*[a-z]+.+\)\n\{\n(?:[\t| +|/].*\n)+\}'
    struct_regular = r'typedef struct *\n* *\{ *\n(?: +.+?;\n)+?\} *\S+?;'
    enum_regular = r'typedef enum *\n* *\{ *\n(?: +.+?,*?\n)+?\} *\S+?;'
    macro_regular = r'#define +(?:.+?) +(?:\S+)'
    global_var_regular = r'(?:\w+) +(?:g_\S+) *= *(?:.+?);'
    ret = errcode.ok
    while True:
        with open(file_path, mode='r', encoding='UTF-8') as file_obj:
            file_content = file_obj.read()
            file_content = common.del_line_sign(file_content)  # delete the \n
            global_func = re.search(global_regular, file_content)
            local_func = re.search(local_func_regular, file_content)
            structs = re.search(struct_regular, file_content)
            enums = re.search(enum_regular, file_content)
            macros = re.search(macro_regular, file_content)
            global_var = re.search(global_var_regular, file_content)
            if global_func is not None:
                func_list = re.findall(global_regular, file_content)
                func_list = common.tab_to_space(func_list)
                g_global_func.extend(func_list)
            if local_func is not None:
                func_list = re.findall(local_func_regular, file_content)
                func_list = common.tab_to_space(func_list)
                g_local_func.extend(func_list)
            if structs is not None:
                struct_list = re.findall(struct_regular, file_content)
                struct_list = common.tab_to_space(struct_list)
                g_struct_list.extend(struct_list)
            if enums is not None:
                enums_list = re.findall(enum_regular, file_content)
                enums_list = common.tab_to_space(enums_list)
                g_enum_list.extend(enums_list)
            if macros is not None:
                macros_list = re.findall(macro_regular, file_content)
                macros_list = common.tab_to_space(macros_list)
                g_macro_list.extend(macros_list)
            if global_var is not None:
                global_var_list = re.findall(global_var_regular, file_content)
                global_var_list = common.tab_to_space(global_var_list)
                g_global_var_list.extend(global_var_list)
        break
    return ret


def local_func_proc(input_func_list, output_info_list: list):
    ret = errcode.ok
    while True:
        if len(input_func_list) == 0:
            break
        for fun_idx in input_func_list:
            info_list = list()
            if_phase_list = if_phase_proc.if_phase(fun_idx)
            if_phase_num = len(if_phase_list)
            if_idx = 0
            task_list = common.pack_func_info(fun_idx)
            for task in task_list:
                info = common.property_map(task)
                if info != 'if':
                    info_list.append(info)
                else:
                    try:
                        if_info = common.if_prop_map(if_phase_list[if_idx], task)
                        info_list.append(if_info)
                        if_idx = if_idx + 1
                        if if_idx > if_phase_num:
                            ret = errcode.file_err
                            break
                    except IndexError:
                        ret = errcode.if_err
                        break
            if ret != errcode.ok:
                break
            func_code = common.func_format_proc(info_list)
            output_info_list.append(func_code)
        break
    return ret


def global_func_proc(input_func_list, output_info_list):
    ret = local_func_proc(input_func_list, output_info_list)
    return ret


def fill_function_info():
    while True:
        ret = global_func_proc(g_global_func, g_global_code_list)
        if ret != errcode.ok:
            break
        ret = local_func_proc(g_local_func, g_local_code_list)
        break
    return ret


def get_code_info(file_path, mode='load'):
    ret_name_list = list()
    ret_list = list()
    ret_num_list = list()
    while True:
        if mode == 'load':
            ret = load_file(file_path)
            if ret != errcode.ok:
                break
        # num-----------------------------------------------------
        global_func_num = len(g_global_func)
        local_func_num = len(g_local_func)
        struct_num = len(g_struct_list)
        enum_num = len(g_enum_list)
        macro_num = len(g_macro_list)
        global_var_num = len(g_global_var_list)
        # name-----------------------------------------------------
        global_func_names = common.get_global_func_names(g_global_func)
        local_func_names = common.get_local_func_names(g_local_func)
        struct_names = common.get_struct_names(g_struct_list)
        enum_names = common.get_enum_names(g_enum_list)
        macro_names = common.get_macro_names(g_macro_list)
        global_var_names = common.get_global_var_names(g_global_var_list)
        # function process---------------------------------------------
        ret = fill_function_info()
        if ret != errcode.ok:
            break
        ret_list.append(g_global_code_list)
        ret_list.append(g_local_code_list)
        ret_list.append(g_struct_list)
        ret_list.append(g_enum_list)
        ret_list.append(g_macro_list)
        ret_list.append(g_global_var_list)

        ret_name_list.append(global_func_names)
        ret_name_list.append(local_func_names)
        ret_name_list.append(struct_names)
        ret_name_list.append(enum_names)
        ret_name_list.append(macro_names)
        ret_name_list.append(global_var_names)

        ret_num_list.append(global_func_num)
        ret_num_list.append(local_func_num)
        ret_num_list.append(struct_num)
        ret_num_list.append(enum_num)
        ret_num_list.append(macro_num)
        ret_num_list.append(global_var_num)
        break
    return ret, ret_name_list, ret_list, ret_num_list


def clear_info():
    g_global_code_list.clear()
    g_local_code_list.clear()
    g_global_func.clear()
    g_local_func.clear()
    g_struct_list.clear()
    g_enum_list.clear()
    g_macro_list.clear()
    g_global_var_list.clear()
