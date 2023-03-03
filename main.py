import re

g_global_regular = r'FUNC\(.+\n\{\n(?:[\t| +|/].*\n)+\}'
g_func_regular = r'(?:static )*[a-z]+.+\)\n\{\n(?:[\t| +|/].*\n)+\}'
g_global_func = list()
g_local_func = list()
circle = 0


def del_line_sign(obj_str: str):
    """
    delete \n
    :param obj_str:
    :return:
    """
    new_line_regular = r'\n+'
    res = re.sub(new_line_regular, '\n', obj_str)
    return res


def get_condition(input_phase: str):
    res = None
    regular = r'\(([\w|.|-|>]+ [=|>|<|!]+ [\w|.|-|>]+)\)'
    phase = re.search(regular, input_phase)
    if phase is not None:
        res = re.findall(regular, input_phase)
    return res


def set_value_phase(input_phase: str, mode):
    res = None
    if mode == 0:
        set_value_regular = r'[\w\ **]+ ([\ ** \w\[*\w *\] *]+) = ([\S]+);'
        phase = re.search(set_value_regular, input_phase)
        if phase is not None:
            res = 'Set ' + str(phase.group(1)) + ' to ' + str(phase.group(2))
    elif mode == 1:
        set_value_regular = r'([\S]+) = ([\S]+);'
        phase = re.search(set_value_regular, input_phase)
        if phase is not None:
            res = input_phase
    return res


def if_phase(input_phase: str):
    line_op = ''
    if input_phase[0] == '\t':
        line_op = input_phase.strip('\t')
    if input_phase[0] == ' ':
        line_op = input_phase.strip()
    conditions = get_condition(input_phase)
    condition_num = len(conditions)
    if_rep = line_op.replace('if', 'IF')
    sign_rep = if_rep.replace('&&', 'and')
    sign_rep = sign_rep.replace('||', 'or')



if __name__ == '__main__':
    with open('source/CtApSwcTriggerParse.c', mode='r', encoding='UTF-8') as obj:
        content = del_line_sign(obj.read())
        g_global_func = re.findall(g_global_regular, content)
        g_local_func = re.findall(g_func_regular, content)
        fun1: str = g_local_func[0]
        lines = fun1.split('\n')
        # print(lines)
        # for i in lines:
        #
