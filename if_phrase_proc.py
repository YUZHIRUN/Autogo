import re
import regular_expression
import common

regular = regular_expression.RegularClass()


def if_condition_pro(input_str: str):
    process_str = input_str.replace('\n', '\n@')
    content_list = process_str.split('@')
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


def if_process(if_phrases: str):
    if_rep = if_phrases.replace('if', 'IF ')
    if_rep = if_rep.replace('else', 'ELSE')
    then_rep = if_rep.replace('{', '\nTHEN')
    sign_rep = then_rep.replace('&&', '\nAND ')
    sign_rep = sign_rep.replace('||', '\nOR ')
    equal_rep = sign_rep.replace('==', ' equal to ')
    not_equal_rep = equal_rep.replace('!=', ' not equal to ')
    if_phrase_1 = common.func_useless_del(not_equal_rep)
    if if_phrase_1.count('(') != 0 and if_phrase_1.count(')') != 0:
        f_bracket_del = common.str_index_rep(if_phrase_1, '(', mode='f')
        l_bracket_del = common.str_index_rep(f_bracket_del, ')', mode='l')
        res = l_bracket_del
    else:
        res = if_phrase_1
    res = if_condition_pro(res)
    res = common.del_line_sign(res)
    res = res.replace('ELSE\nTHEN', 'ELSE THEN')
    return res


def if_phrase(input_phrase: str):
    if_list = list()
    phrase = re.search(regular.get_if_info, input_phrase)
    if phrase is not None:
        if_list = re.findall(regular.get_if_info, input_phrase)
        if_phrase_num = len(if_list)
        for idx in range(if_phrase_num):
            if_list[idx] = if_process(if_list[idx])
    return if_list
