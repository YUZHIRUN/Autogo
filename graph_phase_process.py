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
    depth = int(count / 2) + 1
    return depth

def get_max_depth(input_content: str):
    max_depth = 0
    phase_line = input_content.split('\n')
    for line in phase_line:
        line_depth = get_phase_depth(line)
        if line_depth > max_depth:
            max_depth = line_depth
    return max_depth

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


def set_start(input_content: str):
    return 'Start\n' + input_content


def if_phase_proc(input_code: str):
    # code_list = input_code.split('\n')
    if_code_list = re.findall(regular.graph_if_condition, input_code)
    res_content = input_code
    if_idx = 0
    for code in if_code_list:
        depth = int(get_phase_depth(code))
        condition = str(re.search(regular.graph_get_if_condition, if_code_list[if_idx]).group(1))
        condition = re.sub(regular.not_equal_to, ' != ', condition)
        condition = re.sub(regular.equal_to, ' == ', condition)
        condition = condition.replace('AND', '&&')
        condition = condition.replace('OR', '||')
        condition = condition.replace('\n', ' ')
        res = 'IF ' + condition
        res = common.depth_set(res, depth)
        res_content = res_content.replace(if_code_list[if_idx], res)
        if_idx += 1
    return res_content


def point_add(point: str):
    if point.count('.') != 0:
        point_list = point.split('.')
        point_list[-1] = str(int(point_list[-1]) + 1)
        point_res = '.'.join(point_list)
    else:
        point_res = str(int(point) + 1)
    return point_res


def point_insert(point: str):
    point_res = point + '.1'
    return point_res


def content_pack(input_content: str):
    max_depth = get_max_depth(input_content)
    line_list = input_content.split('\n')
    serial_line = list()
    content_list = list()
    for depth in range(1, max_depth+1):
        current_point = point_add(str(depth))
        for line in line_list:
            current_depth = get_phase_depth(line)
            if (line.count('IF') != 0 or line.count('FOR') != 0 or line.count('ELSE') != 0) or current_depth < depth:
                serial_line.append(line)
        content = '\n'.join(serial_line)
        serial_line.clear()




def phase_process(input_code):
    code_content = var_declare_proc(input_code)
    code_content = if_phase_proc(code_content)
    code_content = set_start(code_content)
    # content_pack(code_content)
    return code_content


#

if __name__ == '__main__':
    with open('_test/test_1.txt', 'r') as obj:
        content = obj.read()
        code = phase_process(content)
        max_depth = get_max_depth(code)
        print(max_depth)
        print(code)
