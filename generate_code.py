import re
import common
import error_code
import function_phrase_proc
import if_phrase_proc
import regular_expression

regular = regular_expression.RegularClass()

g_file_name = ''
g_global_func = list()
g_local_func = list()
# global variable
g_global_var_list = list()
g_global_value_list = list()
g_global_var_comment_list = list()

g_point_func_list = list()
# macro
g_macro_list = list()
g_macro_comment_list = list()
# struct
g_struct_list = list()
g_struct_comment_list = list()
# enum
g_enum_list = list()
g_enum_comment_list = list()
# union
g_union_list = list()
g_union_comment_list = list()
# include
g_include_content_list = list()
g_include_comment_list = list()

g_another_global_vars = list()

# g_func_code_list = list()
g_global_code_list = list()
g_local_code_list = list()

g_local_func_names = list()
g_global_func_names = list()

errcode = error_code.err_class()


def load_file(file_path: str):
    """
    Identify function and other items.
    :param file_path:
    :return:
    """
    global g_file_name
    global_regular = regular.global_func
    local_func_regular = regular.local_func
    struct_regular = regular.struct
    enum_regular = regular.enum
    union_regular = regular.union
    macro_regular = regular.macro
    global_var_regular = regular.global_var
    include_regular = regular.include_file
    ret = errcode.ok
    if file_path.endswith('.c'):
        file_type = '.c'
    else:
        file_type = '.h'
    g_file_name = file_path.split('/')[-1]
    while True:
        with open(file_path, mode='r', encoding='utf-8') as file_obj:
            file_content = file_obj.read()
            # common.get_tab_scale(file_content)
            file_content = common.file_info_clean(file_content, mode=file_type)  # delete the \n
            global_func = re.search(global_regular, file_content)
            local_func = re.search(local_func_regular, file_content)
            structs = re.search(struct_regular, file_content)
            enums = re.search(enum_regular, file_content)
            macros = re.search(macro_regular, file_content)
            global_var = re.search(global_var_regular, file_content)
            unions = re.search(union_regular, file_content)
            include_file = re.search(include_regular, file_content)
            point_funcs = re.search(regular.point_func_declare, file_content)
            if global_func is not None:
                func_list = re.findall(global_regular, file_content)
                g_global_func.extend(func_list)
                file_content = re.sub(global_regular, '', file_content)
            if local_func is not None:
                func_list = re.findall(local_func_regular, file_content)
                for func_idx in func_list:
                    func_head = func_idx.split('\n')[0]
                    if func_head.startswith('FUNC') == 0:
                        g_local_func.append(func_idx)
                file_content = re.sub(local_func_regular, '', file_content)
            if point_funcs is not None:
                point_funcs_declare = re.findall(regular.point_func_declare, file_content)
                g_point_func_list.extend(point_funcs_declare)
                file_content = re.sub(regular.point_func_declare, '', file_content)
            if structs is not None:
                struct_obj_list = re.findall(struct_regular, file_content)
                struct_obj_list = common.st_en_un_del_useless(struct_obj_list)
                struct_list, comment_list = common.st_en_un_get_comment(struct_obj_list)
                g_struct_list.extend(struct_list)
                g_struct_comment_list.extend(comment_list)
                file_content = re.sub(struct_regular, '', file_content)
            if enums is not None:
                enums_obj_list = re.findall(enum_regular, file_content)
                enums_obj_list = common.st_en_un_del_useless(enums_obj_list)
                enums_list, comment_list = common.st_en_un_get_comment(enums_obj_list)
                g_enum_list.extend(enums_list)
                g_enum_comment_list.extend(comment_list)
                file_content = re.sub(enum_regular, '', file_content)
            if unions is not None:
                union_obj_list = re.findall(union_regular, file_content)
                union_obj_list = common.st_en_un_del_useless(union_obj_list)
                union_list, comment_list = common.st_en_un_get_comment(union_obj_list)
                g_union_list.extend(union_list)
                g_union_comment_list.extend(comment_list)
                file_content = re.sub(union_regular, '', file_content)
            if macros is not None:
                macros_obj_list = re.findall(macro_regular, file_content)
                macros_list, comment_list = common.get_comment(macros_obj_list)
                g_macro_list.extend(macros_list)
                g_macro_comment_list.extend(comment_list)
                file_content = re.sub(macro_regular, '', file_content)
            if global_var is not None:
                global_var_obj_list = re.findall(global_var_regular, file_content)
                global_var_list, comment_list = common.get_comment(global_var_obj_list)
                value_list = common.get_global_value(global_var_list)
                remain_content = re.sub(global_var_regular, '', file_content)
                if file_type == '.c':
                    another_vars = re.findall(regular.define_var_init, remain_content)
                    for e in another_vars:
                        var = e.strip()
                        g_another_global_vars.append(var)
                g_global_var_list.extend(global_var_list)
                g_global_value_list.extend(value_list)
                g_global_var_comment_list.extend(comment_list)
            else:
                if file_type == '.c':
                    remain_content = file_content
                    another_vars = re.findall(regular.define_var_init, remain_content)
                    another_vars_def = re.findall(regular.define_var_re, file_content)
                    for e in another_vars:
                        var = e.strip()
                        g_another_global_vars.append(var)
                    for e in another_vars_def:
                        var = e.strip()
                        g_another_global_vars.append(var)
            if file_type == '.c':
                if include_file is not None:
                    include_list = re.findall(include_regular, file_content)
                    content_list, comment_list = common.get_comment(include_list)
                    g_include_content_list.extend(content_list)
                    g_include_comment_list.extend(comment_list)
        break
    return ret


def local_func_proc(input_func_list, output_info_list: list, mode='local'):
    """
    Main function process the function.
    :param mode:
    :param input_func_list:
    :param output_info_list:
    :return:
    """
    if mode == 'local' or mode == 'global':
        ret = errcode.ok
    else:
        ret = errcode.file_err
    while True:
        if len(input_func_list) == 0:
            break
        for fun_idx in input_func_list:
            info_list = list()
            if_phrase_list = if_phrase_proc.if_phrase(fun_idx)
            if_phrase_num = len(if_phrase_list)
            if_idx = 0
            task_list = common.pack_func_info(fun_idx)  # Package valid information in a function
            for task in task_list:
                info = common.property_map(task)
                if info != 'if':
                    info_list.append(info)
                else:
                    try:
                        if_info = common.if_prop_map(if_phrase_list[if_idx], task)
                        info_list.append(if_info)
                        if_idx = if_idx + 1
                        if if_idx > if_phrase_num:
                            ret = errcode.file_err
                            break
                    except IndexError:
                        if mode == 'global':
                            func_name = common.get_global_func_name(fun_idx)
                        else:
                            func_name = common.get_local_func_name(fun_idx)
                        ret = errcode.if_err + ' error function: ' + func_name
                        break
            if ret != errcode.ok:
                break
            func_code = function_phrase_proc.last_func_callback_proc(info_list)
            output_info_list.append(func_code)
        break
    return ret


def global_func_proc(input_func_list, output_info_list):
    ret = local_func_proc(input_func_list, output_info_list, mode='global')
    return ret


def fill_function_info():
    g_global_code_list.clear()
    g_local_code_list.clear()
    # clear_info()
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
        func_num = len(g_global_func) + len(g_local_func)
        struct_num = len(g_struct_list)
        enum_num = len(g_enum_list)
        macro_num = len(g_macro_list)
        union_num = len(g_union_list)
        global_var_num = len(g_global_var_list)
        # name-----------------------------------------------------
        global_func_names = common.get_global_func_names(g_global_func)
        local_func_names = common.get_local_func_names(g_local_func)
        g_local_func_names.extend(local_func_names)
        g_global_func_names.extend(global_func_names)
        struct_names = common.get_struct_names(g_struct_list)
        enum_names = common.get_enum_names(g_enum_list)
        macro_names = common.get_macro_names(g_macro_list)
        global_var_names = common.get_global_var_names(g_global_var_list)
        union_names = common.get_union_names(g_union_list)
        # function process---------------------------------------------
        ret = fill_function_info()
        if ret != errcode.ok:
            break
        ret_name_list.append(global_func_names)
        ret_name_list.append(local_func_names)
        ret_name_list.append(global_var_names)
        ret_name_list.append(macro_names)
        ret_name_list.append(struct_names)
        ret_name_list.append(enum_names)
        ret_name_list.append(union_names)

        ret_list.append(g_global_code_list)
        ret_list.append(g_local_code_list)
        ret_list.append(g_global_var_list)
        ret_list.append(g_macro_list)
        ret_list.append(g_struct_list)
        ret_list.append(g_enum_list)
        ret_list.append(g_union_list)

        ret_num_list.append(func_num)
        ret_num_list.append(global_var_num)
        ret_num_list.append(macro_num)
        ret_num_list.append(struct_num)
        ret_num_list.append(enum_num)
        ret_num_list.append(union_num)
        break
    return ret, ret_name_list, ret_list, ret_num_list


def clear_info():
    g_global_code_list.clear()
    g_local_code_list.clear()
    g_global_func.clear()
    g_local_func.clear()
    g_struct_list.clear()
    g_struct_comment_list.clear()
    g_enum_list.clear()
    g_enum_comment_list.clear()
    g_macro_list.clear()
    g_macro_comment_list.clear()
    g_global_var_list.clear()
    g_global_var_comment_list.clear()
    g_union_list.clear()
    g_union_comment_list.clear()
    g_include_content_list.clear()
    g_include_comment_list.clear()
    g_local_func_names.clear()
    g_global_func_names.clear()
