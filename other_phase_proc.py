import re


def set_value_phase_proc(input_phase: str):
    set_value_regular = r'([\w\.->\[\]\*]+?) *([=|&+-]{1,2}) *([\S| ]+?);'
    plus_regular = r'(\S+) *\+\+;'
    sign_regular = r'([+-])='
    if re.search(set_value_regular, input_phase) is not None:
        variable_name = re.search(set_value_regular, input_phase).group(1)
        value = re.search(set_value_regular, input_phase).group(3)
        sign = re.search(set_value_regular, input_phase).group(2)
        if re.search(sign_regular, sign) is not None:
            first_sign = re.search(sign_regular, sign).group(1)
            res = 'Set ' + str(variable_name) + ' to ' + str(variable_name) + ' ' + str(first_sign) + ' ' + str(value)
        else:
            res = 'Set ' + str(variable_name) + ' to ' + str(value)
    elif re.search(plus_regular, input_phase) is not None:
        variable_name = re.search(plus_regular, input_phase).group(1)
        res = str(variable_name) + ' = ' + str(variable_name) + ' + 1'
    else:
        res = ''
    return res


def break_phase_proc():
    return 'BREAK'


def return_phase_proc(input_phase: str):
    return_regular = r'return +(.+?);'
    return_phase = re.search(return_regular, input_phase)
    if return_phase is not None:
        return_content = return_phase.group(1)
        res = 'RETURN ' + str(return_content)
    else:
        res = ''
    return res
