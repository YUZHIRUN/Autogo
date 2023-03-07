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
    elif re.search(regular.get_set_plus_plus_info, input_phase) is not None:
        variable_name = re.search(regular.get_set_plus_plus_info, input_phase).group(1)
        res = str(variable_name) + ' = ' + str(variable_name) + ' + 1'
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
