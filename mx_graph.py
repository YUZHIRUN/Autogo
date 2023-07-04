from xml.etree import ElementTree as ec
import graph_phase_process

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
Yes = 'Yes'
No = 'No'


# graph_task =
# (
# 	 shape
#    (id, output_coor, output_description)
#    (width, height)
# )

# def get_task_id(task_input: tuple):
#     return task_input[-1]['id']
#
#
# def get_task_shape(task_input: tuple):
#     return task_input[0]
#
#
# def get_task_size(task_input: tuple) -> tuple:
#     """
#     0, width 1, height
#     :param task_input:
#     :return:
#     """
#     return task_input[-1]
#
#
# def get_task_output(task_input):
#     output_info = task_input[-2]
#     return output_info
#
#
# def get_task_input(task_input):
#     input_info = task_input[-3]['input']
#     input_source = input_info[0]
#     input_coor = input_info[1]
#     return input_source, input_coor


def get_shape_id(input_shape):
    return input_shape[0]['id']


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


def get_position(draw_size, obj_info, behavior=down_position, mode='shapes'):
    draw_width = int(draw_size[0])
    draw_height = int(draw_size[1])
    obj_position = obj_info[0]
    obj_size = obj_info[1]
    obj_width = int(obj_size[0])
    obj_height = int(obj_size[1])
    obj_position_x = int(obj_position[0])
    obj_position_y = int(obj_position[1])
    if behavior == down_position:
        draw_position_y = obj_position_y + obj_height + 60
        draw_position_x = obj_position_x - int((draw_width - obj_width) / 2)
    elif behavior == right_position:
        draw_position_x = obj_position_x + obj_width + 100
        if mode == 'group':
            draw_position_y = obj_position_y
        else:
            draw_position_y = obj_position_y - int((draw_height - obj_height) / 2)
    elif behavior == left_position:
        draw_position_x = obj_position_x - 100 - draw_width
        if mode == 'group':
            draw_position_y = obj_position_y
        else:
            draw_position_y = obj_position_y - int((draw_height - obj_height) / 2)
    else:
        draw_position_y = obj_position_y + obj_height + 60
        draw_position_x = obj_position_x - int((draw_width - obj_width) / 2)
    draw_position = (str(draw_position_x), str(draw_position_y))
    return draw_position


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


def get_shape_info(input_task, shape_type=None):
    if shape_type is None:
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


def get_shapes_pack_info(shapes):
    min_x = int('0xFFFF', 16)
    max_x = 0
    min_y = int('0xFFFF', 16)
    max_y = 0
    for shape in shapes:
        shape_id = get_shape_id(shape)
        if shape_id.count('line') != 0:
            continue
        obj_position = get_shape_info(shape)[0]
        obj_size = get_shape_info(shape)[1]
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


class create_graph:
    def __init__(self):

        self.module_id = 'module_1'
        self.line_id = 'line_1'
        self.mx_cell = 'mxCell'
        self.mx_geometry = 'mxGeometry'
        self.mx_point = 'mxPoint'
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

    def direction_to_coor(self, direction='down'):
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
    def upload_new_module_id(self):
        module_id_num = int(self.module_id.split('_')[1])
        module_id_num = module_id_num + 1
        self.module_id = 'module_' + str(module_id_num)

    def upload_new_line_id(self):
        line_id_num = int(self.line_id.split('_')[1])
        line_id_num = line_id_num + 1
        self.line_id = 'line_' + str(line_id_num)

    def draw_ellipse(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text)
        if rel_task is not None:
            try:
                task_num = len(rel_task[0])
                obj_info = get_shape_info(rel_task, 'shapes')
            except Exception:
                obj_info = get_shape_info(rel_task)
            position = get_position(draw_size, obj_info, act)
        else:
            position = self.default_position
        draw_id = str(self.module_id)
        labels = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': labels}
        level_1_label = {'id': draw_id, 'value': text, 'style': 'ellipse;whiteSpace=wrap;html=1;', 'vertex': '1',
                         'parent': '1'}
        level_2_label = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                         'as': 'geometry'}
        self.upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_rectangle(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text)
        if rel_task is not None:
            try:
                task_num = len(rel_task[0])
                obj_info = get_shape_info(rel_task, 'shapes')
            except Exception:
                obj_info = get_shape_info(rel_task)
            position = get_position(draw_size, obj_info, act)
        else:
            position = self.default_position
        draw_id = str(self.module_id)
        labels = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': labels}
        level_1_label = {'id': draw_id, 'value': text, 'style': 'rounded=0;whiteSpace=wrap;html=1;', 'vertex': '1',
                         'parent': '1'}
        level_2_label = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                         'as': 'geometry'}
        self.upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_rectangle_round(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text)
        if rel_task is not None:
            try:
                task_num = len(rel_task[0])
                obj_info = get_shape_info(rel_task, 'shapes')
            except Exception:
                obj_info = get_shape_info(rel_task)
            position = get_position(draw_size, obj_info, act)
        else:
            position = self.default_position
        draw_id = str(self.module_id)
        labels = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'label': labels}
        level_1_label = {'id': draw_id, 'value': text, 'style': 'rounded=1;whiteSpace=wrap;html=1;', 'vertex': '1',
                         'parent': '1'}
        level_2_label = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                         'as': 'geometry'}
        self.upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_parallelogram(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text)
        if rel_task is not None:
            try:
                task_num = len(rel_task[0])
                obj_info = get_shape_info(rel_task, 'shapes')
            except Exception:
                obj_info = get_shape_info(rel_task)
            position = get_position(draw_size, obj_info, act)
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
        self.upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_rhombus(self, text, rel_task=None, act=down_position):
        draw_size = get_shape_size(text, rhombus)
        if rel_task is not None:
            try:
                task_num = len(rel_task[0])
                obj_info = get_shape_info(rel_task, 'shapes')
            except Exception:
                obj_info = get_shape_info(rel_task)
            position = get_position(draw_size, obj_info, act)
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
        self.upload_new_module_id()
        task = (info, level_1_label, level_2_label)
        return task

    def draw_point_line(self, source, target, coor=(('0.5', '1'), ('0.5', '0')), text='', point_array=None):
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
        if point_array is not None:
            # control line
            pass
        self.upload_new_line_id()
        return task

    def create_graph(self, graph_task):
        mx_graph = ec.Element('mxGraphModel', attrib=self.mx_graph_attribute)
        root = ec.SubElement(mx_graph, 'root')
        ec.SubElement(root, self.mx_cell, attrib=self.init_mx_graph_attribute)
        ec.SubElement(root, self.mx_cell, attrib=self.init_mx_cell_attribute)
        for task in graph_task:
            info: dict = task[0]
            task_depth: tuple = info['label']
            task_depth_len = len(task_depth)
            mx_cell = ec.SubElement(root, task_depth[0], attrib=task[1])
            for module in range(1, task_depth_len):
                mx_cell = ec.SubElement(mx_cell, task_depth[module], attrib=task[module + 1])
        xml_obj = ec.ElementTree(mx_graph)
        xml_obj.write('_test/test.xml')

    # endregion------------------------------------------------------------------------------------------------------------------
    def get_link_node(self, input_shape, direction, text=''):
        shape_id = get_shape_id(input_shape)
        coor = self.direction_to_coor(direction)
        output = (shape_id, coor, text)
        return output

    def link_shapes(self, last_output, this_input):
        source = last_output[0]
        target = this_input[0]
        output_coor = last_output[1]
        input_coor = this_input[1]
        text = last_output[2]
        coor = (output_coor, input_coor)
        link_shape = self.draw_point_line(source, target, coor, text)
        return link_shape

    def link_shape_group(self, output_node, input_node):
        link = self.link_shapes(output_node, input_node)
        return link

    def connect_shape_group(self, shape_group_output, shape_group_input, act=down_position):
        output_info = get_shapes_pack_info(shape_group_output)
        input_info = get_shapes_pack_info(shape_group_input)
        input_size = input_info[1]
        position = get_position(input_size, output_info, act, mode='group')
        self.set_shape_group_position(shape_group_input, position)
        return position

    def set_shape_group_position(self, shape_group, position):
        res_group = shape_group
        position_x = int(position[0])
        position_y = int(position[1])
        group_info = get_shapes_pack_info(shape_group)
        group_position = group_info[0]
        position_x = position_x + abs(int(group_position[0]))
        for shape in res_group:
            shape_id = get_shape_id(shape)
            if shape_id.count('module') != 0:
                shape[2]['x'] = str(int(shape[2]['x']) + position_x)
                shape[2]['y'] = str(int(shape[2]['y']) + position_y)
        return res_group

    # def create_group_task(self, input_content: str):
    #     """
    #
    #     :param input_content: input content
    #     :return: (shape_group, contents, outputs, inputs)
    #     """
    #     graph = create_graph()
    #     start_shape = graph.init_shape
    #     start_output = graph.get_link_node(start_shape, 'down')
    #
    #     shape_group = list()
    #     last_shape_info = list()
    #
    #     content_list = input_content.split('\n')
    #     for content_line in content_list:
    #         if content_line.count('IF') == 0:
    #             if len(last_shape_info) != 0:
    #                 shape = graph.draw_rectangle(content_line, last_shape_info[0][0])
    #                 this_shape_input = graph.get_link_node(shape, 'up')
    #             else:
    #                 shape = graph.draw_rectangle(content_line)
    #         else:
    #             text = content_line.replace('IF', '')
    #             text = text.strip()
    #             shape = graph.draw_rhombus(text=text, rel_task=last_shape_info[0][0])


if __name__ == '__main__':
    graph = create_graph()
    start_shape = graph.init_shape
    start_output = graph.get_link_node(start_shape, 'down')
    with open('_test/test.txt', 'r') as obj:
        content = obj.read()
        code = graph_phase_process.phase_process(content)
    code_list = code.split('\n')
    last_shape_pool = list()
    shape_group = list()
    shape_group.append(start_shape)
    last_shape_pool.append((start_shape, start_output))

    group1_output = list()
    group2_input = list()

    for code_line in code_list:
        shape = graph.draw_rectangle(text=code_line, rel_task=last_shape_pool[0][0])
        if code_line.count('IF') != 0:
            output_node = graph.get_link_node(shape, 'right', text='yes')
            group1_output.append(output_node)
        this_shape_input = graph.get_link_node(shape, 'up')
        this_shape_output = graph.get_link_node(shape, 'down')
        last_shape_output = last_shape_pool[0][1]
        link = graph.link_shapes(last_shape_output, this_shape_input)
        shape_group.append(shape)
        shape_group.append(link)
        last_shape_pool.remove(last_shape_pool[0])
        last_shape_pool.append((shape, this_shape_output))
    last_shape_pool.clear()
    #
    shape_group_1 = list()
    for code_line in code_list:
        if len(last_shape_pool) != 0:
            shape = graph.draw_rectangle(text=code_line, rel_task=last_shape_pool[0][0])
            input_node = graph.get_link_node(shape, 'up')
            group2_input.append(input_node)
            this_shape_input = graph.get_link_node(shape, 'up')
            this_shape_output = graph.get_link_node(shape, 'down')
            last_shape_output = last_shape_pool[0][1]
            link = graph.link_shapes(last_shape_output, this_shape_input)
            last_shape_pool.remove(last_shape_pool[0])
            shape_group_1.append(link)
        else:
            shape = graph.draw_rectangle(text=code_line)
            input_node = graph.get_link_node(shape, 'up')
            group2_input.append(input_node)
            this_shape_output = graph.get_link_node(shape, 'down')
        shape_group_1.append(shape)
        last_shape_pool.append((shape, this_shape_output))
    position = graph.connect_shape_group(shape_group, shape_group_1, left_position)
    link = graph.link_shape_group(group1_output[0], group2_input[0])


    shape_group.extend(shape_group_1)
    shape_group.append(link)
    graph.create_graph(shape_group)
