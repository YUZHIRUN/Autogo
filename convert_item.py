import draw_graph
import error_code
import if_phrase_proc
import common
import function_phrase_proc

err = error_code.err_class()


def __code_proc(input_code: str):
    info_list = list()
    if_phrase_list = if_phrase_proc.if_phrase(input_code)
    if_phrase_num = len(if_phrase_list)
    if_idx = 0
    task_list = common.pack_func_info(input_code)  # Package valid information in a function
    for task in task_list:
        info = common.property_map(task)
        if info != 'if':
            info_list.append(info)
        else:
            if_info = common.if_prop_map(if_phrase_list[if_idx], task)
            info_list.append(if_info)
            if_idx = if_idx + 1
            if if_idx > if_phrase_num:
                return err.file_err
    func_code = function_phrase_proc.last_func_callback_proc(info_list)
    return func_code

def convert_code_to_pseudo(code: str):
    try:
        res_code = __code_proc(code)
    except Exception:
        res_code = err.convert_code_error
    return res_code

def convert_graph_to_xml(pseudo_code):
    try:
        xml_info = draw_graph.get_graph_xml(pseudo_code)
    except Exception:
        xml_info = err.draw_error
    return xml_info


if __name__ == '__main__':
    with open('_test/test.txt', 'r') as obj:
        content = obj.read()
    res = convert_graph_to_xml(content)
    print(res)
