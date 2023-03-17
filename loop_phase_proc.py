import re
import regular_expression

regular = regular_expression.RegularClass()


# def for_phase_proc(input_str):
#     if re.search(regular.get_for_info, input_str) is not None:
#         start_condition = str(re.search(regular.get_for_info, input_str).group(1)) + ';'
#         end_condition = str(re.search(regular.get_for_info, input_str).group(2)) + ';'
#         try:
#             variable_name = re.search(regular.get_for_condition, start_condition).group(1)
#             start_value = re.search(regular.get_for_condition, start_condition).group(2)
#             end_value = re.search(regular.get_for_condition, end_condition).group(2)
#             res = 'FOR ' + str(variable_name) + ' from ' + str(start_value) + ' to ' + str(end_value)
#         except Exception:
#             res = ''
#     else:
#         res = ''
#     return res

def for_phase_proc(input_str: str):
    res = input_str.replace('for', 'FOR ')
    res = res.replace('{', '')
    return res


def while_phase_proc(input_phase: str):
    phase = re.search(regular.get_while_info, input_phase)
    if phase is not None:
        condition = phase.group(1)
        res = 'WHILE ' + str(condition) + ' : '
    else:
        res = ''
    return res


def do_phase_proc(input_phase: str):
    do_phase = re.search(regular.get_do_info, input_phase)
    while_regular = re.search(regular.get_while_of_do_info, input_phase)
    if do_phase is not None:
        res = 'DO'
    elif while_regular is not None:
        do_condition = while_regular.group(1)
        res = 'WHILE IF ' + str(do_condition) + ' THEN continue ELSE break'
    else:
        res = ''
    return res
