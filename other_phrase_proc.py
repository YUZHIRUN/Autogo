import re
import regular_expression

regular = regular_expression.RegularClass()


def set_value_phrase_proc(input_phrase: str):
    if re.search(regular.get_set_value_info, input_phrase) is not None:
        variable_name = re.search(regular.get_set_value_info, input_phrase).group(1)
        value = re.search(regular.get_set_value_info, input_phrase).group(3)
        sign = re.search(regular.get_set_value_info, input_phrase).group(2)
        if re.search(regular.special_sign, sign) is not None:
            first_sign = re.search(regular.special_sign, sign).group(1)
            res = 'Set ' + str(variable_name) + ' to ' + str(variable_name) + ' ' + str(first_sign) + ' ' + str(value)
        else:
            res = 'Set ' + str(variable_name) + ' to ' + str(value)
    elif re.search(regular.get_set_special_value_info, input_phrase) is not None:
        variable_name = re.search(regular.get_set_special_value_info, input_phrase).group(1)
        sign = re.search(regular.get_set_special_value_info, input_phrase).group(2)
        res = 'Set ' + str(variable_name) + ' = ' + str(variable_name) + ' ' + str(sign) + ' 1'
    else:
        # res = ''
        res = input_phrase
    return res

def define_var_phrase_proc(input_phrase: str):
    if re.search(regular.get_define_var, input_phrase) is not None:
        var_name = str(re.search(regular.get_define_var, input_phrase).group(1))
        var_type = str(re.search(regular.get_define_type, input_phrase).group(1))
        if str(var_name).count('*') != 0 or str(var_type).count('*') != 0:
            var_name = var_name.replace('*', '')
            var_type = var_type.replace('*', '')
            var_type = var_type + '*'
        res = 'Define variable ' + str(var_name) + ', which type is ' + var_type
    else:
        res = ''
    return res

def define_var_init_proc(input_phrase: str):
    if re.search(regular.get_define_init_info, input_phrase) is not None:
        var_type = str(re.search(regular.get_define_init_info, input_phrase).group(1))
        var_name = str(re.search(regular.get_define_init_info, input_phrase).group(2))
        var_init_val = str(re.search(regular.get_define_init_info, input_phrase).group(3))
        if var_type.count('*') != 0 or var_name.count('*') != 0:
            var_name = var_name.replace('*', '')
            var_type = var_type.replace('*', '')
            var_type = var_type + '*'
        res = 'Define variable @var_name, which type is @var_type, and initialize it to @var_init_val'
        res = res.replace('@var_name', var_name)
        res = res.replace('@var_type', var_type)
        res = res.replace('@var_init_val', var_init_val)
    else:
        res = ''
    return res

def break_phrase_proc():
    return 'BREAK'


def continue_phrase_proc():
    return 'CONTINUE'


def return_phrase_proc(input_phrase: str):
    res = input_phrase.replace('return', 'RETURN')
    res = res.replace(';', '')
    return res

def switch_phrase_proc(input_phrase: str):
    switch_phrase = re.search(regular.switch, input_phrase)
    case_phrase = re.search(regular.case, input_phrase)
    default_phrase = re.search(regular.default, input_phrase)
    if switch_phrase is not None:
        switch_name = switch_phrase.group(1)
        res = 'SWITCH: ' + switch_name
    elif case_phrase is not None:
        case_name = case_phrase.group(1)
        res = 'CASE: ' + case_name
    elif default_phrase is not None:
        res = 'DEFAULT: '
    else:
        res = input_phrase
    return res

def macro_call_proc(input_phase: str):
    res = 'Call the macro ' + input_phase
    res = res.replace(';', '')
    return res
