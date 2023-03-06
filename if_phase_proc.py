import re
import common


def if_condition_pro(input_str: str):
    process_str = input_str.replace('\n', '\n&')
    content_list = process_str.split('&')
    line_num = len(content_list)
    line_idx = 0
    while line_idx < line_num:
        diff_num = content_list[line_idx].count('(') - content_list[line_idx].count(')')
        if diff_num != 0:
            rep = content_list[line_idx].replace('\n', ' ')
            content_list[line_idx] = rep
            line_idx = line_idx + 1
        else:
            line_idx = line_idx + 1
    res = ''.join(content_list)
    res = res.replace('THEN', '\nTHEN')
    return res


def if_process(if_phases: str):
    if_rep = if_phases.replace('if', 'IF ')
    if_rep = if_rep.replace('else', 'ELSE')
    then_rep = if_rep.replace('{', '\nTHEN')
    sign_rep = then_rep.replace('&&', '\nAND ')
    sign_rep = sign_rep.replace('||', '\nOR ')
    equal_rep = sign_rep.replace('==', 'equal to')
    not_equal_rep = equal_rep.replace('!=', 'not equal to')
    if_phase_1 = common.del_line_plus(not_equal_rep)
    if if_phase_1.count('(') != 0 and if_phase_1.count(')') != 0:
        f_bracket_del = common.str_index_rep(if_phase_1, '(', mode='f')
        l_bracket_del = common.str_index_rep(f_bracket_del, ')', mode='l')
        res = l_bracket_del
    else:
        res = if_phase_1
    res = if_condition_pro(res)
    res = common.del_line_sign(res)
    res = res.replace('ELSE\nTHEN', 'ELSE THEN')
    return res


def if_phase(input_phase: str):
    if_list = list()
    if_regular = r'[else]* *if *\(.+\) *\n* *\{|[else]* *if *\([^\{]+\n +[^\{]+\{|else *\n* *\{'
    phase = re.search(if_regular, input_phase)
    if phase is not None:
        if_list = re.findall(if_regular, input_phase)
        if_phase_num = len(if_list)
        for idx in range(if_phase_num):
            if_list[idx] = if_process(if_list[idx])
    return if_list
