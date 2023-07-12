import graph_phrase_process as cp
import mx_graph as mx
from copy import deepcopy

g_content = ''
g_path = r'_test/test.txt'
rectangle_round = 0
rectangle = 1
ellipse = 2
rhombus = 3
parallelogram = 4
group_progress_stack = list()

graph = mx.create_graph()
# ----------------------
down_position = 0
right_position = 1
left_position = 2
# ----------------------
Shape = 0
Group = 1
# --------------------------------
horizontal = 0
vertical = 1
# --------------------------------
group_shape = 0
group_group = 1
shape_group = 2
shape_shape = 3
# ----------------------------------
Yes = 'Yes'
No = 'No'


def init_operate():
    global g_content
    with open(g_path, mode='r') as obj:
        g_content = obj.read()


def get_shape_from_id(input_group, shape_id):
    res_shape = None
    for shape in input_group:
        current_id = mx.get_shape_id(shape)
        if current_id == shape_id:
            res_shape = shape
    return res_shape


def test_create_group(group):
    res = graph.create_graph(group)
    with open('_test/test.xml', 'w') as obj:
        obj.write(res)


def put_item_to_stack(group):
    global group_progress_stack
    group_progress_stack.append(group)


def upload_group_stack():
    global group_progress_stack
    del group_progress_stack[0]


def get_group_from_stack() -> list:
    global group_progress_stack
    group = deepcopy(group_progress_stack[0][0])
    return group


def get_input_shape_from_group(group):
    global group_progress_stack
    input_node = deepcopy(group_progress_stack[0][1])
    shape = get_shape_from_id(group, input_node)
    return shape


def get_output_shape_from_group(group):
    global group_progress_stack
    output_node = deepcopy(group_progress_stack[0][2])
    shape = get_shape_from_id(group, output_node)
    return shape


def get_obj_height(obj, obj_type=Group) -> int:
    obj_info = mx.get_object_info(obj, obj_type)
    obj_size = obj_info[1]
    obj_height = obj_size[1]
    return int(obj_height)


def get_obj_width(obj, obj_type=Group) -> int:
    obj_info = mx.get_object_info(obj, obj_type)
    obj_size = obj_info[1]
    obj_width = obj_size[0]
    return int(obj_width)


def get_obj_coor(obj, direction='down'):
    obj_type = mx.get_object_type(obj)
    if obj_type == Shape:
        obj_coor = mx.get_object_coor(obj, position=direction)
    else:
        obj_info = mx.get_object_info(obj, shape_type=Group)
        obj_x = int(obj_info[0][0])
        obj_y = int(obj_info[0][1])
        obj_width = int(obj_info[1][0])
        obj_height = int(obj_info[1][1])
        if direction == 'down':
            coor_x = obj_x + int(obj_width / 2)
            coor_y = obj_y + int(obj_height)
        elif direction == 'left':
            coor_x = obj_x
            coor_y = obj_y + int(obj_height / 2)
        elif direction == 'right':
            coor_x = obj_x + obj_width
            coor_y = obj_y + int(obj_height / 2)
        else:
            coor_x = obj_x + int(obj_width / 2)
            coor_y = obj_y
        obj_coor = (str(coor_x), str(coor_y))
    return obj_coor


def check_end_shape(shape):
    shape_value = mx.get_shape_text(shape)
    if shape_value == 'END':
        return True
    else:
        return False


def get_shape_down_y_value(shape_id, group):
    shape = get_shape_from_id(group, shape_id)
    obj_coor = mx.get_object_coor(shape)
    obj_coor_y = obj_coor[1]
    return int(obj_coor_y)


def get_min_y_shape_obj(shape_id_list, group):
    min_val = int('0xFFFF', 16)
    res_shape = None
    for shape_id in shape_id_list:
        y_val = get_shape_down_y_value(shape_id, group)
        if y_val < min_val:
            min_val = y_val
            res_shape = get_shape_from_id(group, shape_id)
    return res_shape


def get_y_offset(shape_id_list, group):
    y_list = list()
    for shape_id in shape_id_list:
        y_val = get_shape_down_y_value(shape_id, group)
        y_list.append(y_val)
    min_val = min(y_list)
    max_val = max(y_list)
    offset = abs(max_val - min_val) + 30
    return offset


# def case_content_check(line: str, line_list: list):
#     line_index = line_list

def content_process(content_key: str):
    content_progress = list()
    content_group = list()
    start_flag = True
    start_shape = None
    end_shape = None
    content_task = cp.get_content(content_key)
    content_line = content_task.split('\n')
    for e in content_line:
        code = cp.clean_code_depth(e)
        code = cp.content_clean_line(code)
        if code == 'Start':
            shape = graph.draw_rectangle_round(text='Start')
            content_progress.append(shape)
        else:
            if len(content_progress) == 0:
                shape = graph.draw_rectangle(text=code)
                content_progress.append(shape)
            else:
                shape = graph.draw_rectangle(text=code, rel_task=content_progress[0])
                link = graph.default_down_link(content_progress[0], shape)
                content_progress[0] = deepcopy(shape)
                content_group.append(link)
        content_group.append(shape)
        if start_flag is True:
            start_shape = deepcopy(shape)
            start_flag = False
        end_shape = deepcopy(shape)
    if check_end_shape(end_shape) is False:
        output_line = graph.default_down_line(end_shape)
    else:
        output_line = graph.default_down_line(end_shape, 0)
    content_group.append(output_line)
    input_node = mx.get_shape_id(start_shape)
    output_node = mx.get_shape_id(output_line)
    res_info = (content_group, input_node, output_node)
    return res_info


def switch_obj_joint(switch_obj, case_obj):
    return switch_obj + ' == ' + case_obj


def case_list_to_condition(case_list: list, switch):
    case_condition_list = list()
    for case in case_list:
        case_condition = switch + ' == ' + case
        case_condition_list.append(case_condition)
    conditions = ' || '.join(case_condition_list)
    return conditions


def switch_process(content_key: str):
    shape_group = list()
    input_node = None
    output_node = None
    case_conditions = None
    switch_obj = ''
    last_switch_shape = None
    last_case_group = None
    code_obj = cp.get_content(content_key)
    content_level = cp.get_level(content_key)
    case_group_height_list = list()
    case_group_output_list = list()
    code_line: list = code_obj.split('\n')
    case_list = list()
    for line in code_line:
        current_line_idx = code_line.index(line)
        next_line_depth = cp.get_phrase_depth(code_line[current_line_idx + 1])
        current_depth = cp.get_phrase_depth(line)
        line = cp.clean_code_depth(line)
        if (line.startswith('switch') is True or line.startswith('SWITCH') is True) and current_depth == content_level:
            switch_obj = cp.switch_clean_line(line)
            continue
        elif line.startswith('CASE') is True and current_depth == content_level and next_line_depth == current_depth:
            case_obj = cp.switch_clean_line(line)
            case_list.append(case_obj)
        elif line.startswith('CASE') is True and current_depth == content_level and len(
                case_list) != 0 and next_line_depth != current_depth:
            case_obj = cp.switch_clean_line(line)
            case_list.append(case_obj)
            case_conditions = case_list_to_condition(case_list, switch_obj)
            case_list.clear()
        elif line.startswith('CASE') is True and current_depth == content_level and len(
                case_list) == 0 and next_line_depth != current_depth:
            case_obj = cp.switch_clean_line(line)
            case_conditions = switch_obj_joint(switch_obj, case_obj)
        elif line.startswith('DEFAULT') is True and current_depth == content_level:
            default_shape = graph.draw_rhombus(text='DEFAULT')
            default_group = get_group_from_stack()
            graph.put_shape_group(default_shape, default_group, put_mode=shape_group)
            default_group_input_shape = get_input_shape_from_group(default_group)
            default_link = graph.default_down_link(default_shape, default_group_input_shape, text='YES')
            new_default_group = list()
            new_default_group.extend(default_group)
            new_default_group.append(default_shape)
            new_default_group.append(default_link)
            graph.put_shape_group(last_case_group, new_default_group, act=right_position, put_mode=group_group)
            default_group_output_shape = get_output_shape_from_group(default_group)
            default_group_output_coor = get_obj_coor(default_group_output_shape)
            default_case_link = graph.default_right_link(last_switch_shape, default_shape, text='NO')
            default_group_right_x = int(get_obj_coor(default_group, direction='right')[0])
            default_end_link = graph.default_right_down_left_link(default_shape, default_group_output_coor,
                                                                  rel_x=default_group_right_x, text='NO')
            shape_group.extend(new_default_group)
            shape_group.append(default_case_link)
            shape_group.append(default_end_link)
            default_group_height = get_obj_height(new_default_group)
            case_group_height_list.append(default_group_height)
            output_id = mx.get_shape_id(default_group_output_shape)
            case_group_output_list.append(output_id)
            upload_group_stack()
            test_create_group(shape_group)
            continue
        if case_conditions is not None:
            case_condition = case_conditions
            case_shape = graph.draw_rhombus(case_condition)
            case_group = get_group_from_stack()
            case_group_input_shape = get_input_shape_from_group(case_group)
            graph.put_shape_group(case_shape, case_group, put_mode=shape_group)
            case_link = graph.default_down_link(case_shape, case_group_input_shape, text='YES')
            new_case_group = list()
            new_case_group.extend(case_group)
            new_case_group.append(case_shape)
            new_case_group.append(case_link)
            if last_case_group is not None:
                graph.put_shape_group(last_case_group, new_case_group, act=right_position, put_mode=group_group)
                case_group_link = graph.default_right_link(last_switch_shape, case_shape, text='NO')
                shape_group.extend(new_case_group)
                shape_group.append(case_group_link)
            else:
                shape_group.extend(new_case_group)
                input_node = mx.get_shape_id(case_shape)
            last_switch_shape = deepcopy(case_shape)
            last_case_group = deepcopy(new_case_group)
            new_case_group_height = get_obj_height(new_case_group)
            case_group_height_list.append(new_case_group_height)
            case_group_output = get_output_shape_from_group(case_group)
            output_id = mx.get_shape_id(case_group_output)
            case_group_output_list.append(output_id)
            case_conditions = None
            test_create_group(shape_group)
            upload_group_stack()
    switch_min_height = min(case_group_height_list)
    max_height = max(case_group_height_list)
    height_offset = (max_height - switch_min_height) + 30
    min_height_index = case_group_height_list.index(switch_min_height)
    min_case_group_output_id = case_group_output_list[min_height_index]
    min_height_output_shape = get_shape_from_id(shape_group, min_case_group_output_id)
    output_line = graph.default_down_line(min_height_output_shape, line_length=height_offset)
    output_line_coor = get_obj_coor(output_line)
    output_node = mx.get_shape_id(output_line)
    shape_group.append(output_line)
    for e in case_group_output_list:
        if e != min_case_group_output_id:
            output_shapes = get_shape_from_id(shape_group, e)
            links = graph.default_down_left_or_right(output_shapes, output_line_coor, mode='None')
            shape_group.append(links)
    test_create_group(shape_group)
    res_info = (shape_group, input_node, output_node)
    return res_info


def do_while_process(content_key: str):
    shape_group = list()
    input_node = None
    output_node = None
    do_line = None
    do_while_group_output = None
    do_while_group = None
    code_obj = cp.get_content(content_key)
    content_level = cp.get_level(content_key)
    code_lines = code_obj.split('\n')
    for line in code_lines:
        current_depth = cp.get_phrase_depth(line)
        line = cp.clean_code_depth(line)
        if line.startswith(
                'DO WHILE') is True and content_level == current_depth:  # line.startswith('DO') is True and content_level == current_depth:
            line = cp.do_while_clean_line(line)
            do_while_shape = graph.draw_rhombus(line)
            graph.put_shape_group(do_while_group, do_while_shape, put_mode=group_shape)
            link = graph.default_down_link(do_while_group_output, do_while_shape)
            do_while_group_left_x = int(get_obj_coor(do_while_group, 'left')[0])
            do_while_right_x = int(get_obj_coor(do_while_shape, 'right')[0])
            do_while_yes_link, array1 = graph.default_down_left_up_right_link(do_while_shape, do_line,
                                                                              rel_x=do_while_group_left_x, text='YES')
            do_while_no_link, target_coor = graph.default_right_down_left_down_line(do_while_shape, array1,
                                                                                    rel_x=do_while_right_x,
                                                                                    text='NO')
            output_node = mx.get_shape_id(do_while_no_link)
            shape_group.append(do_while_shape)
            shape_group.append(link)
            shape_group.append(do_while_yes_link)
            shape_group.append(do_while_no_link)
            test_create_group(shape_group)
            continue
        elif line.startswith('DO') is True and content_level == current_depth:
            do_while_group = get_group_from_stack()
            do_while_input_shape = get_input_shape_from_group(do_while_group)
            do_line = graph.default_up_line(do_while_input_shape)
            do_line_coor = get_obj_coor(do_line)
            input_node = mx.get_shape_id(do_line)
            shape_group.extend(do_while_group)
            shape_group.append(do_line)
            do_while_group_output = deepcopy(get_output_shape_from_group(do_while_group))
            test_create_group(shape_group)
            upload_group_stack()
            continue
        else:
            continue
    res_info = (shape_group, input_node, output_node)
    return res_info


def for_process(content_key: str):
    shape_group = list()
    input_node = None
    output_node = None

    code_obj = cp.get_content(content_key)
    content_level = cp.get_level(content_key)
    code_lines = code_obj.split('\n')
    for line in code_lines:
        current_depth = cp.get_phrase_depth(line)
        line = cp.clean_code_depth(line)
        if line.startswith('FOR') is True and content_level == current_depth:
            # line =
            shape = graph.draw_rhombus(text=line)
            for_group = get_group_from_stack()
            graph.put_shape_group(shape, for_group, put_mode=shape_group)
            for_group_input_shape = get_input_shape_from_group(for_group)
            for_group_output_shape = get_output_shape_from_group(for_group)
            # for_group_width = get_obj_width(for_group)
            for_group_left_x = int(get_obj_coor(for_group, direction='left')[0])
            for_group_right_x = int(get_obj_coor(for_group, direction='right')[0])
            link = graph.default_down_link(shape, for_group_input_shape, text='YES')

            output_line = graph.default_down_line(for_group_output_shape, line_length=20)

            for_link = graph.default_left_up_right_link(output_line, shape, rel_x=for_group_left_x)
            output_coor = mx.get_object_coor(output_line)
            for_else_link, target_coor = graph.default_right_down_left_down_line(shape, output_coor,
                                                                                 rel_x=for_group_right_x, text='NO')
            shape_group.append(output_line)
            shape_group.extend(for_group)
            shape_group.append(shape)
            shape_group.append(link)
            shape_group.append(for_link)
            shape_group.append(for_else_link)
            output_node = mx.get_shape_id(for_else_link)
            input_node = mx.get_shape_id(shape)
            upload_group_stack()
            test_create_group(shape_group)
        else:
            continue
    res_info = (shape_group, input_node, output_node)
    return res_info


def while_process(content_key: str):
    shape_group = list()
    input_node = None
    output_node = None

    code_obj = cp.get_content(content_key)
    content_level = cp.get_level(content_key)
    code_lines = code_obj.split('\n')
    for line in code_lines:
        current_depth = cp.get_phrase_depth(line)
        line = cp.clean_code_depth(line)
        if line.startswith('WHILE') is True and content_level == current_depth:
            line = cp.while_clean_line(line)
            shape = graph.draw_rhombus(text=line)
            for_group = get_group_from_stack()
            graph.put_shape_group(shape, for_group, put_mode=shape_group)
            for_group_input_shape = get_input_shape_from_group(for_group)
            for_group_output_shape = get_output_shape_from_group(for_group)
            # for_group_width = get_obj_width(for_group)
            for_group_left_x = int(get_obj_coor(for_group, direction='left')[0])
            for_group_right_x = int(get_obj_coor(for_group, direction='right')[0])
            link = graph.default_down_link(shape, for_group_input_shape, text='YES')
            for_link = graph.default_left_up_right_link(for_group_output_shape, shape, rel_x=for_group_left_x)
            output_coor = mx.get_object_coor(for_group_output_shape)
            for_else_link, target_coor = graph.default_right_down_left_down_line(shape, output_coor,
                                                                                 rel_x=for_group_right_x, text='NO')
            # output_line = graph.default_down_line_from_coor(target_coor, line_length=10)
            shape_group.extend(for_group)
            shape_group.append(shape)
            shape_group.append(link)
            shape_group.append(for_link)
            shape_group.append(for_else_link)
            # shape_group.append(output_line)
            output_node = mx.get_shape_id(for_else_link)
            input_node = mx.get_shape_id(shape)
            upload_group_stack()
            test_create_group(shape_group)
        else:
            continue
    res_info = (shape_group, input_node, output_node)
    return res_info


def if_process(content_key: str):
    shape_group = list()
    input_node = None
    output_node = None
    branch_shape = None
    if_tree = None

    else_flag = False
    output_shape_id = list()

    code_obj = cp.get_content(content_key)
    content_level = cp.get_level(content_key)
    code_lines = code_obj.split('\n')
    for line in code_lines:
        current_depth = cp.get_phrase_depth(line)
        line = cp.clean_code_depth(line)
        if line.startswith('IF') is True and line.count('ELSE') == 0 and content_level == current_depth:
            line = cp.if_clean_line(line)
            shape = graph.draw_rhombus(text=line)
            if_group = get_group_from_stack()
            graph.put_shape_group(shape, if_group, put_mode=shape_group)
            if_tree = deepcopy(if_group)
            if_group_input_shape = get_input_shape_from_group(if_group)
            if_output_shape = deepcopy(get_output_shape_from_group(if_group))
            if_output_shape_id = mx.get_shape_id(if_output_shape)
            output_shape_id.append(if_output_shape_id)
            link = graph.default_down_link(shape, if_group_input_shape, text='YES')
            branch_shape = deepcopy(shape)
            shape_group.append(shape)
            shape_group.append(link)
            shape_group.extend(if_group)
            input_node = mx.get_shape_id(shape)
            upload_group_stack()
            test_create_group(shape_group)
        elif line.startswith('ELSE IF') is True and content_level == current_depth:
            line = cp.if_clean_line(line)
            shape = graph.draw_rhombus(text=line)
            else_if_group = get_group_from_stack()
            graph.put_shape_group(shape, else_if_group, act=down_position, put_mode=shape_group)
            else_if_input = get_input_shape_from_group(else_if_group)
            link = graph.default_down_link(shape, else_if_input, text='YES')
            else_if_branch = deepcopy(else_if_group)
            else_if_branch.append(shape)
            else_if_branch.append(link)
            graph.put_shape_group(if_tree, else_if_branch, act=right_position, put_mode=group_group)
            graph.put_shape_group(if_tree, else_if_group, act=right_position, put_mode=group_group)
            if_tree = deepcopy(else_if_group)
            else_if_group_output_shape = get_output_shape_from_group(else_if_group)
            else_if_group_output_shape_id = mx.get_shape_id(else_if_group_output_shape)
            output_shape_id.append(else_if_group_output_shape_id)
            else_if_link = graph.default_right_down_link(branch_shape, shape, text='NO')
            branch_shape = deepcopy(shape)
            shape_group.extend(else_if_branch)
            shape_group.append(else_if_link)
            upload_group_stack()
            test_create_group(shape_group)
        elif line.count('ELSE') != 0 and content_level == current_depth:
            line = cp.if_clean_line(line)
            else_flag = True
            else_group = get_group_from_stack()
            graph.put_shape_group(if_tree, else_group, put_mode=group_group, act=right_position)
            else_input_shape = get_input_shape_from_group(else_group)
            else_output_shape = get_output_shape_from_group(else_group)
            else_output_shape_id = mx.get_shape_id(else_output_shape)
            link = graph.default_right_down_link(branch_shape, else_input_shape, text='NO')
            shape_group.append(link)
            shape_group.extend(else_group)
            upload_group_stack()
            output_shape_id.append(else_output_shape_id)
            line_length = get_y_offset(shape_id_list=output_shape_id, group=shape_group)
            output_shape = get_min_y_shape_obj(shape_id_list=output_shape_id, group=shape_group)
            output_line = graph.default_down_line(output_shape, line_length)
            output_coor = mx.get_object_coor(output_line)
            shape_group.append(output_line)
            for shape_id in output_shape_id:
                shape_obj = get_shape_from_id(shape_group, shape_id)
                if shape_obj != output_shape:
                    link = graph.default_down_left_or_right(shape_obj, output_coor)
                    shape_group.append(link)
            output_node = mx.get_shape_id(output_line)
            test_create_group(shape_group)
        else:
            continue
    if else_flag is False:
        line_length = get_y_offset(shape_id_list=output_shape_id, group=shape_group)
        output_shape = get_min_y_shape_obj(shape_id_list=output_shape_id, group=shape_group)
        output_line = graph.default_down_line(output_shape, line_length)
        output_line_coor = mx.get_object_coor(output_line)
        no_else_target_coor_x = output_line_coor[0]
        no_else_target_coor_y = str(int(output_line_coor[1]) - 20)
        no_else_target_coor = (no_else_target_coor_x, no_else_target_coor_y)
        for shape_id in output_shape_id:
            shape_obj = get_shape_from_id(shape_group, shape_id)
            if shape_obj != output_shape:
                shape_obj = get_shape_from_id(shape_group, shape_id)
                link = graph.default_down_left_or_right(shape_obj, output_line_coor)
                shape_group.append(link)
        if_branch_right_x = int(get_obj_coor(if_tree, direction='right')[0])
        branch_shape_right_x = int(get_obj_coor(branch_shape, 'right')[0])
        last_link = graph.default_right_down_left_link(branch_shape, no_else_target_coor, rel_x=max(if_branch_right_x, branch_shape_right_x),
                                                       text='NO')
        shape_group.append(output_line)
        shape_group.append(last_link)
        output_node = mx.get_shape_id(output_line)
        test_create_group(shape_group)
    shape_info = (shape_group, input_node, output_node)
    return shape_info


def task_analyze(task):
    global group_progress_stack
    info_list = list()
    shape_group = list()
    new_input_node = None
    new_output_node = None
    last_group = None
    last_output_shape = None
    for item in task:
        item_type = cp.get_phrase_type(item)
        if item_type == 'content':
            res_info = content_process(item)
        elif item_type == 'IF':
            res_info = if_process(item)
        elif item_type == 'FOR':
            res_info = for_process(item)
        elif item_type == 'WHILE':
            res_info = while_process(item)
        elif item_type == 'DO_WHILE':
            res_info = do_while_process(item)
        elif item_type == 'SWITCH':
            res_info = switch_process(item)
        else:
            res_info = None
        info_list.append(res_info)
    info_num = len(info_list)
    if info_num == 1:
        put_item_to_stack(info_list[0])
        test_create_group(info_list[0][0])
    else:
        for idx in range(info_num):
            package = info_list[idx]
            group = package[0]
            input_node = package[1]
            output_node = package[2]
            if idx == 0:
                shape_group.extend(group)
                last_group = group
                new_input_node = input_node
                last_output_shape = get_shape_from_id(group, output_node)
            else:
                input_shape = get_shape_from_id(group, input_node)
                graph.put_shape_group(last_group, group, put_mode=group_group)
                link = graph.default_down_link(last_output_shape, input_shape)
                shape_group.extend(group)
                shape_group.append(link)
                last_group = group
                last_output_shape = get_shape_from_id(group, output_node)
                test_create_group(shape_group)
        new_output_node = mx.get_shape_id(last_output_shape)
        res_info = (shape_group, new_input_node, new_output_node)
        test_create_group(shape_group)
        put_item_to_stack(res_info)


def draw_mx_graph(code_object):
    fifo: list = cp.phrase_process(code_object)
    for task in fifo:
        task_analyze(task)
    finally_group = get_group_from_stack()
    res = graph.create_graph(finally_group)
    upload_group_stack()
    return res


def get_graph_xml(code_object):
    res = draw_mx_graph(code_object)
    return res


if __name__ == '__main__':
    with open('_test/test.txt', mode='r') as obj:
        content = obj.read()
    res = get_graph_xml(content)
    with open('_test/test.xml', 'w') as obj_xml:
        obj_xml.write(res)