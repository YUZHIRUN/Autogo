import re
import regular_expression
import error_code

name_re = regular_expression.variables_class()


def variable_proc(input_str: str):
    pass


def rename_proc(file_path):
    with open(file_path, mode='r+', encoding='UTF-8') as file_obj:
        file_content = file_obj.read()
