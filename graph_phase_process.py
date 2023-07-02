import generate_code
import common
import regular_expression
import re

regular = regular_expression.graph_parse()

def get_phase_depth(input_phase: str):
    count = 0
    for i in input_phase:
        if i == '_':
            count += 1
        else:
            break
    return int(count / 2)

def var_declare_proc(input_code: str):
    define_var = re.search(regular.graph_define_var_del, input_code)
    if define_var is not None:
        define_phase = 'Define variables\n'
    else:
        define_phase = ''
    res_content = re.sub(regular.graph_define_var_del, '', input_code)
    res_content = define_phase + res_content
    res_content = common.del_line_sign(res_content)
    return res_content

def if_phase_proc(input_code: str):
    # code_list = input_code.split('\n')
    if_code_list = re.findall(regular.graph_if_condition, input_code)
    res_content = input_code
    if_idx = 0
    for code in if_code_list:
        depth = int(get_phase_depth(code))
        condition = str(re.search(regular.graph_get_if_condition, if_code_list[if_idx]).group(1))
        condition = re.sub(regular.not_equal_to, ' != ', condition)
        condition = re.sub(regular.equal_to, ' = ', condition)
        condition = condition.replace('AND', '&&')
        condition = condition.replace('OR', '||')
        condition = condition.replace('\n', ' ')
        res = 'IF ' + condition
        res = common.depth_set(res, depth)
        res_content = res_content.replace(if_code_list[if_idx], res)
        if_idx += 1
    return res_content



def phase_process(input_code):
    code_content = var_declare_proc(input_code)
    code_content = if_phase_proc(code_content)

    print(code_content)


if __name__ == '__main__':
    with open('_test/test.txt', 'r') as obj:
        content = obj.read()
        phase_process(content)


