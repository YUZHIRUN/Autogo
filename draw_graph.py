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
    graph.create_graph(group)


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
            coor_y = obj_y +int(obj_height / 2)
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


def content_process(content_key: str):
    content_progress = list()
    content_group = list()
    start_flag = True
    start_shape = None
    end_shape = None
    content_task = cp.get_content(content_key)
    content_line = content_task.split('\n')
    for e in content_line:
        code = cp.clean_code(e)
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
    put_item_to_stack(res_info)

def for_process(content_key: str):
    shape_group = list()
    input_node = None
    output_node = None

    code_obj = cp.get_content(content_key)
    content_level = cp.get_level(content_key)
    code_lines = code_obj.split('\n')
    for line in code_lines:
        current_depth = cp.get_phrase_depth(line)
        line = cp.clean_code(line)
        if line.count('FOR') != 0 and content_level == current_depth:
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
            for_else_link, target_coor = graph.default_right_down_left_down_line(shape, output_coor, rel_x=for_group_right_x, text='NO')
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
    put_item_to_stack(res_info)


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
        line = cp.clean_code(line)
        if line.count('IF') != 0 and line.count('ELSE') == 0 and content_level == current_depth:
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
        elif line.count('ELSE IF') != 0 and content_level == current_depth:
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
        last_link = graph.default_right_down_left_link(branch_shape, no_else_target_coor, rel_x=if_branch_right_x, text='NO')
        shape_group.append(output_line)
        shape_group.append(last_link)
        output_node = mx.get_shape_id(output_line)
        test_create_group(shape_group)
    shape_info = (shape_group, input_node, output_node)
    put_item_to_stack(shape_info)


def finally_process():
    finally_group = list()
    global group_progress_stack
    item_num = len(group_progress_stack)
    last_output = None
    last_group = None
    for items_idx in range(item_num):
        if items_idx == 0:
            start_group = get_group_from_stack()
            last_group = deepcopy(start_group)
            last_output = get_output_shape_from_group(start_group)
            finally_group.extend(start_group)
            upload_group_stack()
            continue
        else:
            item = get_group_from_stack()
            graph.put_shape_group(last_group, item, put_mode=group_group)
            item_input = get_input_shape_from_group(item)
            item_output = get_output_shape_from_group(item)
            link = graph.default_down_link(last_output, item_input)
            last_output = item_output
            last_group = deepcopy(item)
            finally_group.extend(item)
            finally_group.append(link)
            upload_group_stack()
    return finally_group


if __name__ == '__main__':
    init_operate()
    fifo = cp.phrase_process()
    code_index_task_level_package = cp.phrase_process(g_content)
    for code_index_task_level in code_index_task_level_package:
        for code_index in code_index_task_level:
            task_type = cp.get_phrase_type(code_index)
            if task_type == 'content':
                content_process(code_index)
            elif task_type == 'IF':
                if_process(code_index)
            elif task_type == 'FOR':
                for_process(code_index)
    finally_group = finally_process()
    graph.create_graph(finally_group)
