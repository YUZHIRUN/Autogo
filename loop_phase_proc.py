import re


def for_phase_proc(input_str):
    for_regular = r'for *\((.+?);(.+?);(.+?)\)'
    condition_regular = r'([\w|\.|-|>|\[|\]|\*]+?) *[>|<|=]{1,2} *([\S| ]+?);'
    if re.search(for_regular, input_str) is not None:
        start_condition = re.search(for_regular, input_str).group(1) + ';'
        end_condition = re.search(for_regular, input_str).group(2) + ';'
        # loop_condition = re.search(for_regular, input_str).group(3)
        try:
            variable_name = re.search(condition_regular, start_condition).group(1)
            start_value = re.search(condition_regular, start_condition).group(2)
            end_value = re.search(condition_regular, end_condition).group(2)
            res = 'FOR ' + str(variable_name) + ' from ' + str(start_value) + ' to ' + str(end_value)
        except Exception:
            res = ''
    else:
        res = ''
    return res


def while_phase_proc(input_phase: str):
    while_regular = r'while *\((.+?)\)'
    phase = re.search(while_regular, input_phase)
    if phase is not None:
        condition = phase.group(1)
        res = 'WHILE ' + str(condition) + ' THEN continue ELSE break'
    else:
        res = ''
    return res


def do_phase_proc(input_phase: str):
    do_regular = r'do *\{*'
    while_regular = r'\} *while *\((.+?)\);'
    do_phase = re.search(do_regular, input_phase)
    while_regular = re.search(while_regular, input_phase)
    if do_phase is not None:
        res = 'DO'
    elif while_regular is not None:
        do_condition = while_regular.group(1)
        res = 'IF ' + str(do_condition) + ' THEN continue ELSE break'
    else:
        res = ''
    return res
