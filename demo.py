import re


# def set_value_phase(input_phase: str):
#     res = None
#     # set_value_regular = r'([\w]+) ([\w]+) *= *(.+);'
#     set_value_regular = r'[\w\ **]+ ([\ ** \w\[*\w *\] *]+) = ([\S]+);'
#     phase = re.search(set_value_regular, input_phase)
#     if phase is not None:
#         res = 'Set ' + str(phase.group(1)) + ' to ' + str(phase.group(2))
#     return res


def get_condition(input_phase: str):
    res = None
    regular = r'\(([\w|.|-|>]+ [=|>|<]+ [\w|.|-|>]+)\)'
    phase = re.search(regular, input_phase)
    if phase is not None:
        res = re.findall(regular, input_phase)
    return res


test = 'if ((sigRecState.ALM_ICL_aktiv == TRUE) && (sigRecState.ALM_ICL_Navigation_aktiv == TRUE) && (ALM_ICL_01_status == FALSE)) {'

condition = get_condition(test)

print(condition)
