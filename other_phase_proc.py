import re
import regular_expression

regular = regular_expression.RegularClass()


def set_value_phase_proc(input_phase: str):
    if re.search(regular.get_set_value_info, input_phase) is not None:
        variable_name = re.search(regular.get_set_value_info, input_phase).group(1)
        value = re.search(regular.get_set_value_info, input_phase).group(3)
        sign = re.search(regular.get_set_value_info, input_phase).group(2)
        if re.search(regular.special_sign, sign) is not None:
            first_sign = re.search(regular.special_sign, sign).group(1)
            res = 'Set ' + str(variable_name) + ' to ' + str(variable_name) + ' ' + str(first_sign) + ' ' + str(value)
        else:
            res = 'Set ' + str(variable_name) + ' to ' + str(value)
    elif re.search(regular.get_set_special_value_info, input_phase) is not None:
        variable_name = re.search(regular.get_set_special_value_info, input_phase).group(1)
        sign = re.search(regular.get_set_special_value_info, input_phase).group(2)
        res = 'Set ' + str(variable_name) + ' = ' + str(variable_name) + ' ' + str(sign) + ' 1'
    else:
        res = ''
    return res


def break_phase_proc():
    return 'BREAK'


def return_phase_proc(input_phase: str):
    return_phase = re.search(regular.get_return_info, input_phase)
    if return_phase is not None:
        return_content = return_phase.group(1)
        res = 'RETURN ' + str(return_content)
    else:
        res = ''
    return res


def switch_phase_proc(input_phase: str):
    switch_phase = re.search(regular.switch, input_phase)
    case_phase = re.search(regular.case, input_phase)
    default_phase = re.search(regular.default, input_phase)
    if switch_phase is not None:
        switch_name = switch_phase.group(1)
        res = 'SWITCH: ' + switch_name
    elif case_phase is not None:
        case_name = case_phase.group(1)
        res = 'CASE: ' + case_name
    elif default_phase is not None:
        res = 'DEFAULT: '
    else:
        res = ''
    return res
