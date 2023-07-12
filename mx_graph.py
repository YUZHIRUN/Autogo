import copy
from copy import deepcopy
from xml.etree import ElementTree as ec
import graph_phrase_process as cp

g_content = ''
g_path = r'_test/test.txt'
rectangle_round = 0
rectangle = 1
ellipse = 2
rhombus = 3
parallelogram = 4
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
# ---------------------------------------
Yes = 'Yes'
No = 'No'

def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# def get_object_type(unknown_input):
#     if isinstance(unknown_input[0], tuple) is True:
#         res = Group
#     else:
#         res = Shape
#     return res

def get_object_type(unknown_input):
    if isinstance(unknown_input[0], dict) is True:
        res = Shape
    else:
        res = Group
    return res


def get_shape_id(input_shape):
    return input_shape[0]['id']


def get_shape_text(input_shape):
    return input_shape[1]['value']


def get_row_num(input_list: list):
    row_num = 1
    list_length = len(input_list)
    max_length = get_list_max_item(input_list)
    str_len = 0
    for idx in range(list_length):
        str_len = str_len + len(input_list[idx]) + 1
        if str_len > max_length:
            row_num += 1
            str_len = 0
    return row_num


def get_list_max_item(input_list: list, shape_type=rectangle):
    res = 0
    if shape_type == rectangle:
        for e in input_list:
            length = len(e)
            if length > res:
                res = length
        if res < 20:
            res = 20
    elif shape_type == rhombus:
        for e in input_list:
            length = len(e)
            if length > res:
                res = length
        if res < 28:
            res = 28
    else:
        for e in input_list:
            length = len(e)
            if length > res:
                res = length
        if res < 20:
            res = 20
    return res


def get_last_shape(shape_package):
    last_shape = None
    max_y = 0
    for shape in shape_package:
        shape_id = get_shape_id(shape)
        if shape_id.count('line') != 0 or shape_id.count('arrow') != 0:
            continue
        else:
            shape_y = get_object_info(shape)[0][1]
            if int(shape_y) > int(max_y):
                max_y = int(shape_y)
                last_shape = shape
    return last_shape


def get_first_shape(shape_package):
    min_y = int('0xFFFF', 16)
    first_shape = None
    for shape in shape_package:
        shape_id = get_shape_id(shape)
        if shape_id.count('line') != 0 or shape_id.count('arrow') != 0:
            continue
        else:
            shape_y = get_object_info(shape)[0][1]
            if int(shape_y) < int(min_y):
                min_y = int(shape_y)
                first_shape = shape
    return first_shape


def get_shape_relative_position(this_draw_size, object_shape, behavior=down_position):
    draw_width = int(this_draw_size[0])
    obj_type = get_object_type(object_shape)
    obj_info = get_object_info(object_shape, shape_type=obj_type)
    obj_position = obj_info[0]
    obj_size = obj_info[1]
    obj_width = int(obj_size[0])
    obj_height = int(obj_size[1])
    obj_position_x = int(obj_position[0])
    obj_position_y = int(obj_position[1])
    offset_y = 60
    if behavior == down_position:
        draw_position_y = obj_position_y + obj_height + offset_y
        draw_position_x = obj_position_x - int((draw_width - obj_width) / 2)
    else:  # right
        draw_position_x = obj_position_x + obj_width + 100
        draw_position_y = obj_position_y
    draw_position = (str(draw_position_x), str(draw_position_y))
    return draw_position

def get_this_group_rel_info(group):
    min_y = int('0xFFFF', 16)
    rel_shape_info = None
    for shape in group:
        shape_id = get_shape_id(shape)
        if shape_id.count('arrow') != 0:
            continue
        shape_position = get_object_info(shape)[0]
        shape_y = int(shape_position[1])
        if shape_y < min_y:
            min_y = shape_y
            rel_shape_info = get_object_info(shape)
    return rel_shape_info

def get_obj_group_rel_info(group):
    min_x = int('0xFFFF', 16)
    max_y = 0
    min_x_shape_size = ('120', '60')
    for shape in group:
        shape_id = get_shape_id(shape)
        shape_position = get_object_info(shape)[0]
        shape_x = int(shape_position[0])
        shape_y = int(shape_position[1])
        # if shape_id.count('arrow') != 0:
        #     shape_y = int()
        if shape_y > max_y:
            max_y = shape_y
        if shape_id.count('arrow') != 0 or shape_id.count('line') != 0:
            continue
        if shape_x < min_x:
            min_x = shape_x
            shape_info = get_object_info(shape)
            min_x_shape_size = shape_info[1]
    rel_shape_position = (str(min_x), str(max_y))
    rel_shape_size = min_x_shape_size
    rel_shape_info = (rel_shape_position, rel_shape_size)
    return rel_shape_info

def get_object_relative_potion(rel_obj, this_obj, position=down_position, put_mode=shape_shape):
    this_type = get_object_type(this_obj)
    rel_type = get_object_type(rel_obj)
    if position == down_position and this_type == Group and rel_type == Group:
        this_info = get_this_group_rel_info(this_obj)
        rel_obj_info = get_obj_group_rel_info(rel_obj)
    elif position == down_position and rel_type == Group and this_type == Shape:
        this_info = get_object_info(this_obj)
        rel_obj_info = get_obj_group_rel_info(rel_obj)
    elif position == down_position and rel_type == Shape and this_type == Group:
        this_info = get_this_group_rel_info(this_obj)
        rel_obj_info = get_object_info(rel_obj, shape_type=Shape)
    else:
        # rel_type = get_object_type(rel_obj)
        rel_obj_info = get_object_info(rel_obj, rel_type)
        this_info = get_object_info(this_obj, this_type)

    this_position = this_info[0]
    this_size = this_info[1]
    this_width = int(this_size[0])
    this_height = int(this_size[1])
    this_x = int(this_position[0])
    this_y = int(this_position[1])
    rel_position = rel_obj_info[0]
    rel_size = rel_obj_info[1]
    rel_width = int(rel_size[0])
    rel_height = int(rel_size[1])
    rel_x = int(rel_position[0])
    rel_y = int(rel_position[1])
    offset_y = 60
    offset_x = 40
    if rel_type == Shape and this_type == Shape:
        if position == down_position:
            draw_position_y = rel_y + rel_height + offset_y
            draw_position_x = rel_x - int((this_width - rel_width) / 2)
        else:  # right
            draw_position_x = rel_x + rel_width + offset_x
            draw_position_y = rel_y
    elif rel_type == Shape and this_type == Group:
        if position == down_position:
            draw_position_y = rel_y + rel_height + offset_y
            draw_position_x = int((rel_width + rel_x * 2) / 2) - int((this_width + this_x * 2) / 2)
        else:
            draw_position_y = rel_y
            draw_position_x = rel_x + rel_width + offset_x + abs(this_x)
    elif rel_type == Group and this_type == Shape:
        if position == down_position:
            draw_position_x = rel_x - int((this_width - rel_width) / 2)
            draw_position_y = rel_y + rel_height + offset_y
        else:
            draw_position_x = rel_x + rel_width + offset_x
            draw_position_y = rel_y
    else:
        if position == down_position:
            draw_position_y = rel_y + offset_y
            draw_position_x = int((rel_width + rel_x * 2) / 2) - int((this_width + this_x * 2) / 2)
        else:
            draw_position_y = rel_y
            draw_position_x = rel_x + rel_width + offset_x + abs(this_x)
    draw_position = (str(draw_position_x), str(draw_position_y))
    return draw_position


def get_object_coor(obj, position='down'):
    obj_id = get_shape_id(obj)
    if obj_id.count('arrow') != 0:
        coor = get_arrow_target_position(obj)
    else:
        obj_info = get_object_info(obj)
        obj_x = int(obj_info[0][0])
        obj_y = int(obj_info[0][1])
        obj_width = int(obj_info[1][0])
        obj_height = int(obj_info[1][1])
        if position == 'up':
            coor_x = obj_x + obj_width / 2
            coor_y = obj_y
        elif position == 'left':
            coor_x = obj_x
            coor_y = obj_y + obj_height / 2
        elif position == 'right':
            coor_x = obj_x + obj_width
            coor_y = obj_y + obj_height / 2
        else:
            coor_x = obj_x + obj_width / 2
            coor_y = obj_y + obj_height
        coor = (str(int(coor_x)), str(int(coor_y)))
    return coor


def get_shape_size(input_str: str, widget_type=rectangle):
    str_list = input_str.split(' ')
    if widget_type == rectangle:
        max_length = get_list_max_item(str_list)
        row_num = get_row_num(str_list)
        default_width = '120'
        default_height = '60'
        if len(input_str) <= 20:
            x_level = 0
        else:
            x_level = int(float((max_length - 20) / 7) - 0.005) + 1
        if row_num <= 4:
            y_level = 0
        else:
            y_level = int(float((row_num - 4) / 3) - 0.005) + 1
        res_width = str(int(default_width) + (40 * x_level))
        res_height = str(int(default_height) + (40 * y_level))
        res = (res_width, res_height)
    elif widget_type == rhombus:
        max_length = get_list_max_item(str_list)
        row_num = get_row_num(str_list)
        default_width = '160'
        default_height = '80'
        if len(input_str) <= 28:
            x_level = 0
        else:
            x_level = int(float((max_length - 28) / 12) - 0.005) + 1
        if row_num <= 2:
            y_level = 0
        else:
            y_level = int(float(row_num - 4) - 0.005) + 1
        res_width = str(int(default_width) + (40 * x_level))
        res_height = str(int(default_height) + (40 * y_level))
        res = (res_width, res_height)
    else:
        res = ('0', '0')
    return res


def get_arrow_info(input_arrow):
    """
    get arrow size and position
    :param input_arrow:
    :return:
    """
    source_x = int(input_arrow[3]['x'])
    source_y = int(input_arrow[3]['y'])
    target_x = int(input_arrow[4]['x'])
    target_y = int(input_arrow[4]['y'])
    min_x = int('0xFFFF', 16)
    max_x = 0
    min_y = int('0xFFFF', 16)
    max_y = 0
    if len(input_arrow[6]) != 0:
        for array in input_arrow[6]:
            array_x = int(array['x'])
            array_y = int(array['y'])
            if array_x > max_x:
                max_x = array_x
            if array_x < min_x:
                min_x = array_x
            if array_y > max_y:
                max_y = array_y
            if array_y < min_y:
                min_y = array_y
            if source_x > max_x:
                max_x = source_x
            if source_x < min_x:
                min_x = source_x
            if source_y > max_y:
                max_y = source_y
            if source_y < min_y:
                min_y = source_y
        size = (str(max_x - min_x), str(max_y - min_y))
        position = (str(min_x), str(max_y))
    else:
        if source_x == target_x:
            size = ('40', str(abs(target_y - source_y)))
            position = (str(source_x), str(min(source_y, target_y)))
        elif source_y == target_y:
            size = (str(abs(source_x - target_x)), '40')
            position = (str(min(source_x, target_x)), str(source_y))
        else:
            size = (str(abs(source_x - target_x)), str(abs(source_y - target_y)))
            position = (str(min(source_x, target_x)), str(min(source_y, target_y)))
    info = (position, size)
    return info


def get_object_info(input_task, shape_type=Shape) -> (tuple, tuple):
    if shape_type == Shape:
        shape_id = get_shape_id(input_task)
        if shape_id.count('arrow') != 0:
            info = get_arrow_info(input_task)
        else:
            x_position = input_task[2]['x']
            y_position = input_task[2]['y']
            width = input_task[2]['width']
            height = input_task[2]['height']
            position = (x_position, y_position)
            draw_size = (width, height)
            info = (position, draw_size)
    else:
        info = get_shapes_pack_info(input_task)

    return info


def get_shapes_pack_info(shapes) -> tuple:
    """
    get group information
    :param shapes:
    :return:
    """
    min_x = int('0xFFFF', 16)
    max_x = 0
    min_y = int('0xFFFF', 16)
    max_y = 0
    for shape in shapes:
        shape_id = get_shape_id(shape)
        if shape_id.count('line') != 0:
            continue
        obj_position = get_object_info(shape)[0]
        obj_size = get_object_info(shape)[1]
        if int(obj_position[0]) < min_x:
            min_x = int(obj_position[0])
        if int(obj_position[0]) + int(obj_size[0]) > max_x:
            max_x = int(obj_position[0]) + int(obj_size[0])
        if int(obj_position[1]) < min_y:
            min_y = int(obj_position[1])
        if int(obj_position[1]) + int(obj_size[1]) > max_y:
            max_y = int(obj_position[1]) + int(obj_size[1])
    max_height = max_y - min_y
    max_width = max_x - min_x
    shapes_size = (max_width, max_height)
    shapes_position = (min_x, min_y)
    shapes_info = (shapes_position, shapes_size)
    return shapes_info


def get_arrow_source_position(shape):
    position_x = shape[3]['x']
    position_y = shape[3]['y']
    position = (position_x, position_y)
    return position


def get_arrow_target_position(shape):
    position_x = shape[4]['x']
    position_y = shape[4]['y']
    position = (position_x, position_y)
    return position


class create_graph:
    def __init__(self):

        self.module_id = 'module_1'
        self.line_id = 'line_1'
        self.arrow_id = 'arrow_1'
        self.mx_cell = 'mxCell'
        self.mx_geometry = 'mxGeometry'
        self.mx_point = 'mxPoint'
        self.array = 'Array'
        self.point_left = '0'
        self.point_right = '1'
        self.point_middle = '0.5'
        self.point_up = '0'
        self.point_down = '1'
        self.mx_graph_attribute = {'dx': '1422', 'dy': '746', 'grid': '1', 'gridSize': '10', 'guides': '1',
                                   'tooltips': '1', 'connect': '1', 'fold': '1', 'page': '1', 'pageScale': '1',
                                   'pageWidth': '827', 'pageHeight': '1169'}
        self.init_mx_graph_attribute = {'id': '0'}
        self.init_mx_cell_attribute = {'id': '1', 'parent': '0'}

        self.default_position = ('0', '0')
        self.down_link = ((self.point_middle, self.point_down), (self.point_middle, self.point_up))
        self.left_link = ((self.point_left, self.point_middle), (self.point_right, self.point_middle))
        self.right_link = ((self.point_right, self.point_middle), (self.point_left, self.point_middle))
        self.left_left_link = ((self.point_left, self.point_middle), (self.point_left, self.point_middle))
        self.right_right_link = ((self.point_right, self.point_middle), (self.point_right, self.point_middle))
        self.right_down_link = ((self.point_right, self.point_middle), (self.point_middle, self.point_up))
        self.init_shape = self.draw_rectangle_round('Start')

    def __direction_to_coor(self, direction='down'):
        if direction == 'up':
            coor = (self.point_middle, self.point_up)
        elif direction == 'left':
            coor = (self.point_left, self.point_middle)
        elif direction == 'right':
            coor = (self.point_right, self.point_middle)
        else:
            coor = (self.point_middle, self.point_down)
        return coor

    # region draw shapes
    def __upload_new_module_id(self):
        module_id_num = int(self.module_id.split('_')[1])
        module_id_num = module_id_num + 1
        self.module_id = 'module_' + str(module_id_num)

    def __upload_new_line_id(self):
        line_id_num = int(self.line_id.split('_')[1])
        line_id_num = line_id_num + 1
        self.line_id = 'line_' + str(line_id_num)

    def __upload_new_arrow_id(self):
        arrow_id_num = int(self.arrow_id.split('_')[1])
        arrow_id_num = arrow_id_num + 1
        self.arrow_id = 'arrow_' + str(arrow_id_num)

    def draw_ellipse(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text)
        if rel_task is not None:
            position = get_shape_relative_position(draw_size, rel_task, act)
        else:
            position = self.default_position
        draw_id = str(self.module_id)
        labels = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': labels}
        level_1_label = {'id': draw_id, 'value': text, 'style': 'ellipse;whiteSpace=wrap;html=1;', 'vertex': '1',
                         'parent': '1'}
        level_2_label = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                         'as': 'geometry'}
        self.__upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_rectangle(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text)
        if rel_task is not None:
            position = get_shape_relative_position(draw_size, rel_task, act)
        else:
            position = self.default_position
        draw_id = str(self.module_id)
        labels = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': labels}
        level_1_label = {'id': draw_id, 'value': text, 'style': 'rounded=0;whiteSpace=wrap;html=1;', 'vertex': '1',
                         'parent': '1'}
        level_2_label = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                         'as': 'geometry'}
        self.__upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_rectangle_round(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text)
        if rel_task is not None:
            position = get_shape_relative_position(draw_size, rel_task, act)
        else:
            position = self.default_position
        draw_id = str(self.module_id)
        labels = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': labels}
        level_1_label = {'id': draw_id, 'value': text, 'style': 'rounded=1;whiteSpace=wrap;html=1;', 'vertex': '1',
                         'parent': '1'}
        level_2_label = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                         'as': 'geometry'}
        self.__upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_parallelogram(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text)
        if rel_task is not None:
            position = get_shape_relative_position(draw_size, rel_task, act)
        else:
            position = self.default_position
        draw_id = self.module_id
        labels = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': labels}
        level_1_label = {'id': draw_id, 'value': text,
                         'style': 'shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;',
                         'vertex': '1',
                         'parent': '1'}
        level_2_label = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                         'as': 'geometry'}
        self.__upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_rhombus(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text, rhombus)
        if rel_task is not None:
            position = get_shape_relative_position(draw_size, rel_task, act)
        else:
            position = self.default_position
        draw_id = self.module_id
        labels = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': labels}
        level_1_label = {'id': draw_id, 'value': text,
                         'style': 'rhombus;whiteSpace=wrap;html=1;',
                         'vertex': '1',
                         'parent': '1'}
        level_2_label = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                         'as': 'geometry'}
        self.__upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_auto_line(self, source, target, coor=(('0.5', '1'), ('0.5', '0')), text=''):
        draw_id = self.line_id
        depth = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': depth}
        draw_style = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=$0;exitY=$1;exitDx=0;exitDy=0;entryX=@0;entryY=@1;entryDx=0;entryDy=0;'
        draw_style = draw_style.replace('$0', coor[0][0])
        draw_style = draw_style.replace('$1', coor[0][1])
        draw_style = draw_style.replace('@0', coor[1][0])
        draw_style = draw_style.replace('@1', coor[1][1])
        level_1_label = {'id': draw_id, 'value': text, 'style': draw_style, 'parent': '1', 'source': source,
                         'target': target, 'edge': '1'}
        level_2_label = {'relative': '1', 'as': 'geometry'}
        task = [info, level_1_label, level_2_label]
        self.__upload_new_line_id()
        return task

    def draw_arrow_line(self, source, target, array: list = None, text='', arrow_mode='classic'):
        draw_id = self.arrow_id
        depth = (self.mx_cell, self.mx_geometry, self.mx_point, self.mx_point, self.array, self.mx_point)
        info = {'id': draw_id, 'label': depth}
        if arrow_mode == 'classic':
            level_1_label = {'id': draw_id, 'value': text,
                             'style': 'endArrow=classic;rounded=0;html=1;',
                             'edge': '1',
                             'parent': '1'}
        else:
            level_1_label = {'id': draw_id, 'value': text,
                             'style': 'endArrow=none;rounded=0;html=1;',
                             'edge': '1',
                             'parent': '1'}
        level_2_label = {'width': '40', 'height': '40', 'relative': '1', 'as': 'geometry'}
        level_3_label = {'x': source[0], 'y': source[1], 'as': 'sourcePoint'}
        level_4_label = {'x': target[0], 'y': target[1], 'as': 'targetPoint'}
        level_5_label = {'as': 'points'}
        array_label = list()
        if array is not None:
            array_num = len(array)
            for array_idx in range(array_num):
                coor = array[array_idx]
                label = {'x': coor[0], 'y': coor[1]}
                array_label.append(label)
        shape = [info, level_1_label, level_2_label, level_3_label, level_4_label, level_5_label, array_label]
        self.__upload_new_arrow_id()
        return shape

    def create_graph(self, graph_task):
        mx_graph = ec.Element('mxGraphModel', attrib=self.mx_graph_attribute)
        root = ec.SubElement(mx_graph, 'root')
        ec.SubElement(root, self.mx_cell, attrib=self.init_mx_graph_attribute)
        ec.SubElement(root, self.mx_cell, attrib=self.init_mx_cell_attribute)
        for task in graph_task:
            info: dict = task[0]
            task_id: str = info['id']
            if task_id.count('arrow') != 0:
                task_depth: tuple = info['label']
                mx_cell = ec.SubElement(root, task_depth[0], attrib=task[1])
                mx_geometry = ec.SubElement(mx_cell, task_depth[1], attrib=task[2])
                ec.SubElement(mx_geometry, task_depth[2], attrib=task[3])
                ec.SubElement(mx_geometry, task_depth[3], attrib=task[4])
                if len(task[6]) != 0:
                    array = ec.SubElement(mx_geometry, task_depth[4], attrib=task[5])
                    for e in task[6]:
                        ec.SubElement(array, task_depth[5], attrib=e)
            else:
                task_depth: tuple = info['label']
                task_depth_len = len(task_depth)
                mx_cell = ec.SubElement(root, task_depth[0], attrib=task[1])
                for module in range(1, task_depth_len):
                    mx_cell = ec.SubElement(mx_cell, task_depth[module], attrib=task[module + 1])
        indent(mx_graph)
        res = ec.tostring(mx_graph).decode()
        return res

    # endregion------------------------------------------------------------------------------------------------------------------

    def get_arrow_node(self, shape, direction='down', text=''):
        shape_id = get_shape_id(shape)
        if shape_id.count('arrow') == 0:
            node_coor = get_object_coor(shape, direction)
        else:
            node_coor = get_arrow_target_position(shape)
        output = (node_coor, text)
        return output

    def arrow_link_shapes(self, output_node, input_node):
        source_coor = output_node[0]
        target_coor = input_node[0]
        text = output_node[1]
        link = self.draw_arrow_line(source_coor, target_coor, text=text)
        return link

    def default_down_link(self, source_shape, target_shape, text=''):
        source_coor = get_object_coor(source_shape)
        target_coor = get_object_coor(target_shape, 'up')
        source_coor_x = int(source_coor[0])
        source_coor_y = int(source_coor[1])
        target_coor_x = int(target_coor[0])
        target_coor_y = int(target_coor[1])
        if source_coor_x == target_coor_x:
            link = self.draw_arrow_line(source_coor, target_coor, text=text)
        else:
            array_1_x = source_coor_x
            array_1_y = source_coor_y + int((target_coor_y - source_coor_y) / 2)
            array_2_x = target_coor_x
            array_2_y = array_1_y
            array_1 = (str(array_1_x), str(array_1_y))
            array_2 = (str(array_2_x), str(array_2_y))
            array = [array_1, array_2]
            link = self.draw_arrow_line(source_coor, target_coor, array, text=text)
        return link

    def default_right_link(self, source_shape, target_shape, text=''):
        source_coor = get_object_coor(source_shape, 'right')
        target_coor = get_object_coor(target_shape, 'left')
        source_coor_x = int(source_coor[0])
        source_coor_y = int(source_coor[1])
        target_coor_x = int(target_coor[0])
        target_coor_y = int(target_coor[1])
        if source_coor_y == target_coor_y:
            link = self.draw_arrow_line(source_coor, target_coor, text=text)
        else:
            array_1_x = source_coor_x + int((target_coor_x - source_coor_x) / 2)
            array_1_y = source_coor_y
            array_2_x = array_1_x
            array_2_y = target_coor_y
            array_1 = (str(array_1_x), str(array_1_y))
            array_2 = (str(array_2_x), str(array_2_y))
            array = [array_1, array_2]
            link = self.draw_arrow_line(source_coor, target_coor, array, text=text)
        return link


    def default_down_line(self, shape, line_length=30):
        output_coor = get_object_coor(shape)
        output_coor_x = output_coor[0]
        output_coor_y = output_coor[1]
        destination_coor_x = output_coor_x
        destination_coor_y = str(int(output_coor_y) + line_length)
        destination_coor = (destination_coor_x, destination_coor_y)
        link = self.draw_arrow_line(source=output_coor, target=destination_coor, arrow_mode='None')
        return link

    def default_up_line(self, shape, line_length=30, text=''):
        output_coor = get_object_coor(shape, 'up')
        output_coor_x = int(output_coor[0])
        output_coor_y = int(output_coor[1])
        des_coor_x = output_coor_x
        des_coor_y = output_coor_y - line_length
        des_coor = (str(des_coor_x), str(des_coor_y))
        link = self.draw_arrow_line(source=output_coor, target=des_coor, arrow_mode='None', text=text)
        return link

    def default_down_line_from_coor(self, coor, line_length=30, text=''):
        destination_coor_x = coor[0]
        destination_coor_y = str(int(coor[1]) + line_length)
        destination_coor = (destination_coor_x, destination_coor_y)
        link = self.draw_arrow_line(coor, destination_coor, arrow_mode='None', text=text)
        return link


    def default_down_left_or_right(self, source_shape, target_coor, mode='classic'):
        source_coor = get_object_coor(source_shape)
        source_coor_x = int(source_coor[0])
        source_coor_y = int(source_coor[1])
        target_coor_x = int(target_coor[0])
        target_coor_y = int(target_coor[1])
        array_1_x = source_coor_x
        array_1_y = target_coor_y
        array_1 = (str(array_1_x), str(array_1_y))
        array = [array_1, ]
        link = self.draw_arrow_line(source_coor, target_coor, array, arrow_mode=mode)
        return link

    def default_right_down_link(self, source_shape, target_shape, text=''):
        source_coor = get_object_coor(source_shape, 'right')
        target_coor = get_object_coor(target_shape, 'up')
        source_coor_x = int(source_coor[0])
        source_coor_y = int(source_coor[1])
        target_coor_x = int(target_coor[0])
        target_coor_y = int(target_coor[1])
        array_1_x = target_coor_x
        array_1_y = source_coor_y
        array_1 = (str(array_1_x), str(array_1_y))
        array = [array_1, ]
        link = self.draw_arrow_line(source_coor, target_coor, array, text=text)
        return link

    def default_left_up_right_link(self, source_shape, target_shape, rel_x):
        source_coor = get_object_coor(source_shape)
        target_coor = get_object_coor(target_shape, 'left')
        source_info = get_object_info(source_shape)[1]
        source_width = int(source_info[0])
        source_coor_x = int(source_coor[0])
        source_coor_y = int(source_coor[1])
        target_coor_y = int(target_coor[1])
        array_1_x = rel_x - 40
        array_1_y = source_coor_y
        array_2_x = array_1_x
        array_2_y = target_coor_y
        array_1 = (str(array_1_x), str(array_1_y))
        array_2 = (str(array_2_x), str(array_2_y))
        array = [array_1, array_2]
        link = self.draw_arrow_line(source_coor, target_coor, array)
        return link

    def default_down_left_up_right_link(self, source_shape, target_shape, rel_x, text=''):
        source_coor = get_object_coor(source_shape, 'down')
        target_coor = get_object_coor(target_shape, 'left')
        source_coor_x = int(source_coor[0])
        source_coor_y = int(source_coor[1])
        target_coor_x = int(target_coor[0])
        target_coor_y = int(target_coor[1])

        array_1_x = source_coor_x
        array_1_y = source_coor_y + 30
        array_2_x = rel_x - 40
        array_2_y = array_1_y
        array_3_x = array_2_x
        array_3_y = target_coor_y
        array_1 = (str(array_1_x), str(array_1_y))
        array_2 = (str(array_2_x), str(array_2_y))
        array_3 = (str(array_3_x), str(array_3_y))
        array = [array_1, array_2, array_3]
        link = self.draw_arrow_line(source_coor, target_coor, array, text=text)
        return link, array_1

    def default_right_down_left_link(self, source_shape, target_coor, rel_x, text=''):
        source_coor = get_object_coor(source_shape, 'right')
        size = get_object_info(source_shape)[1]
        source_width = int(size[0])
        source_coor_x = int(source_coor[0])
        source_coor_y = int(source_coor[1])
        target_coor_x = int(target_coor[0])
        target_coor_y = int(target_coor[1])
        array_1_x = rel_x + 40
        array_1_y = source_coor_y
        array_2_x = array_1_x
        array_2_y = target_coor_y
        array_1 = (str(array_1_x), str(array_1_y))
        array_2 = (str(array_2_x), str(array_2_y))
        array = [array_1, array_2]
        link = self.draw_arrow_line(source_coor, target_coor, array, text=text)
        return link

    def default_right_down_left_down_line(self, source_shape, output_coor, rel_x, text=''):
        source_coor = get_object_coor(source_shape, 'right')
        size = get_object_info(source_shape)[1]
        source_width = int(size[0])
        source_coor_x = int(source_coor[0])
        source_coor_y = int(source_coor[1])
        output_coor_x = int(output_coor[0])
        output_coor_y = int(output_coor[1])
        target_coor_x = output_coor_x
        target_coor_y = output_coor_y + 60
        target_coor = (str(target_coor_x), str(target_coor_y))
        array_1_x = rel_x + 40
        array_1_y = source_coor_y
        array_2_x = array_1_x
        array_2_y = output_coor_y + 30
        array_3_x = output_coor_x
        array_3_y = array_2_y
        array_1 = (str(array_1_x), str(array_1_y))
        array_2 = (str(array_2_x), str(array_2_y))
        array_3 = (str(array_3_x), str(array_3_y))
        array = [array_1, array_2, array_3]
        link = self.draw_arrow_line(source_coor, target_coor, arrow_mode='None', array=array, text=text)
        return link, target_coor

    def put_shape_group(self, rel_obj, this_obj, act=down_position, put_mode=shape_shape):
        position = get_object_relative_potion(rel_obj, this_obj, act, put_mode)
        this_type = get_object_type(this_obj)
        if this_type == Shape:
            self.set_shape_position(this_obj, position)
        else:
            self.set_shape_group_position(this_obj, position)

    def set_shape_position(self, shape, position):
        position_x = int(position[0])
        position_y = int(position[1])
        shape_id = get_shape_id(shape)
        if shape_id.count('module') != 0:
            shape[2]['x'] = str(int(shape[2]['x']) + position_x)
            shape[2]['y'] = str(int(shape[2]['y']) + position_y)
        if shape_id.count('arrow') != 0:
            shape[3]['x'] = str(int(shape[3]['x']) + position_x)
            shape[3]['y'] = str(int(shape[3]['y']) + position_y)
            shape[4]['x'] = str(int(shape[4]['x']) + position_x)
            shape[4]['y'] = str(int(shape[4]['y']) + position_y)
            if len(shape[6]) != 0:
                for e in shape[6]:
                    e['x'] = str(int(e['x']) + position_x)
                    e['y'] = str(int(e['y']) + position_y)

    def set_shape_group_position(self, shape_group, position):
        res_group = shape_group
        position_x = int(position[0])
        position_y = int(position[1])
        for shape in res_group:
            shape_id = get_shape_id(shape)
            if shape_id.count('module') != 0:
                shape[2]['x'] = str(int(shape[2]['x']) + position_x)
                shape[2]['y'] = str(int(shape[2]['y']) + position_y)
            if shape_id.count('arrow') != 0:
                shape[3]['x'] = str(int(shape[3]['x']) + position_x)
                shape[3]['y'] = str(int(shape[3]['y']) + position_y)
                shape[4]['x'] = str(int(shape[4]['x']) + position_x)
                shape[4]['y'] = str(int(shape[4]['y']) + position_y)
                if len(shape[6]) != 0:
                    for e in shape[6]:
                        e['x'] = str(int(e['x']) + position_x)
                        e['y'] = str(int(e['y']) + position_y)


#
if __name__ == '__main__':
    graph = create_graph()
    group = list()
    task_0 = graph.init_shape
    down_line = graph.default_down_line(task_0)
    group_0 = [task_0, down_line]
    task_1 = graph.draw_rectangle(text='test_1')
    graph.put_shape_group(group_0, task_1)
    # group.append(task_0)
    # group.append(down_line)
    group.extend(group_0)
    group.append(task_1)
    graph.create_graph(group)