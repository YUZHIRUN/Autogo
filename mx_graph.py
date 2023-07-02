from xml.etree import ElementTree as ec

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
#
# 	 (level_1)
# 	 (level_2)
#    ...
#    (input_info, output_info)
#    (width, height)
#    (id, depth)
# )

def get_task_id(task_input: tuple):
    return task_input[-1]['id']

def get_task_depth(task_input: tuple):
    return task_input[-1]['depth']

def get_task_size(task_input: tuple) -> tuple:
    """
    0, width 1, height
    :param task_input:
    :return:
    """
    return task_input[-2]

def get_task_output(task_input):
    output_info = task_input[-3]['output']
    output_source = output_info[0]
    output_coor = output_info[1]
    return output_source, output_coor

def get_task_input(task_input):
    input_info = task_input[-3]['input']
    input_source = input_info[0]
    input_coor = input_info[1]
    return input_source, input_coor


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


def get_position(draw_size, obj_info, behavior=down_position):
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
        draw_position_x = obj_position_x + obj_width + 160
        draw_position_y = obj_position_y - int((draw_height - obj_height) / 2)
    elif behavior == left_position:
        draw_position_x = obj_position_x - 160 - draw_width
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


def get_task_info(input_task):
    x_position = input_task[2]['x']
    y_position = input_task[2]['y']
    width = input_task[2]['width']
    height = input_task[2]['height']
    position = (x_position, y_position)
    draw_size = (width, height)
    info = (position, draw_size)
    return info


class creat_graph:
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
        self.down_link = ((self.point_middle, self.point_down), (self.point_middle, self.point_up))
        self.left_link = ((self.point_left, self.point_middle), (self.point_right, self.point_middle))
        self.right_link = ((self.point_right, self.point_middle), (self.point_left, self.point_middle))
        self.left_left_link = ((self.point_left, self.point_middle), (self.point_left, self.point_middle))
        self.right_right_link = ((self.point_right, self.point_middle), (self.point_right, self.point_middle))
        self.right_down_link = ((self.point_right, self.point_middle), (self.point_middle, self.point_up))
        self.init_task = self.draw_rectangle_round('Start', position=('280', '0'))

    def upload_new_module_id(self):
        module_id_num = int(self.module_id.split('_')[1])
        module_id_num = module_id_num + 1
        self.module_id = 'module_' + str(module_id_num)

    def upload_new_line_id(self):
        line_id_num = int(self.line_id.split('_')[1])
        line_id_num = line_id_num + 1
        self.line_id = 'line_' + str(line_id_num)

    def draw_ellipse(self, text, position, draw_size: tuple = ('120', '60')):
        draw_id = str(self.module_id)
        depth = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'level': depth}
        level_1_attribute = {'id': draw_id, 'value': text, 'style': 'ellipse;whiteSpace=wrap;html=1;', 'vertex': '1',
                             'parent': '1'}
        level_2_attribute = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                             'as': 'geometry'}
        self.upload_new_module_id()
        task = (info, level_1_attribute, level_2_attribute)
        return task

    def draw_rectangle(self, text, position, draw_size: tuple = ('120', '60')):
        draw_id = str(self.module_id)
        depth = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'level': depth}
        level_1_attribute = {'id': draw_id, 'value': text, 'style': 'rounded=0;whiteSpace=wrap;html=1;', 'vertex': '1',
                             'parent': '1'}
        level_2_attribute = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                             'as': 'geometry'}
        self.upload_new_module_id()
        task = (info, level_1_attribute, level_2_attribute)
        return task

    def draw_rectangle_round(self, text, position, draw_size: tuple = ('120', '60')):
        draw_id = str(self.module_id)
        depth = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'level': depth}
        level_1_attribute = {'id': draw_id, 'value': text, 'style': 'rounded=1;whiteSpace=wrap;html=1;', 'vertex': '1',
                             'parent': '1'}
        level_2_attribute = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                             'as': 'geometry'}
        self.upload_new_module_id()
        task = (info, level_1_attribute, level_2_attribute)
        return task

    def draw_parallelogram(self, text, position, draw_size: tuple = ('120', '60')):
        draw_id = self.module_id
        depth = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'level': depth}
        level_1_attribute = {'id': draw_id, 'value': text,
                             'style': 'shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;',
                             'vertex': '1',
                             'parent': '1'}
        level_2_attribute = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                             'as': 'geometry'}
        self.upload_new_module_id()
        task = (info, level_1_attribute, level_2_attribute)
        return task

    def draw_rhombus(self, text, position, draw_size: tuple = ('160', '80')):
        draw_id = self.module_id
        depth = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'level': depth}
        level_1_attribute = {'id': draw_id, 'value': text,
                             'style': 'rhombus;whiteSpace=wrap;html=1;',
                             'vertex': '1',
                             'parent': '1'}
        level_2_attribute = {'x': position[0], 'y': position[1], 'width': draw_size[0], 'height': draw_size[1],
                             'as': 'geometry'}
        self.upload_new_module_id()
        task = (info, level_1_attribute, level_2_attribute)
        return task

    def draw_point_line(self, source, target, coor=(('0.5', '1'), ('0.5', '0')), text='', point_array=None):
        draw_id = self.line_id
        depth = (self.mx_cell, self.mx_geometry)
        info = {'id': draw_id, 'level': depth}
        draw_style = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=$0;exitY=$1;exitDx=0;exitDy=0;entryX=@0;entryY=@1;entryDx=0;entryDy=0;'
        draw_style = draw_style.replace('$0', coor[0][0])
        draw_style = draw_style.replace('$1', coor[0][1])
        draw_style = draw_style.replace('@0', coor[1][0])
        draw_style = draw_style.replace('@1', coor[1][1])
        level_1_attribute = {'id': draw_id, 'value': text, 'style': draw_style, 'parent': '1', 'source': source,
                             'target': target, 'edge': '1'}
        level_2_attribute = {'relative': '1', 'as': 'geometry'}
        task = [info, level_1_attribute, level_2_attribute]
        if point_array is not None:
            # control line
            pass
        self.upload_new_line_id()
        return task

    def line_connect(self, line_task, path='_test/test.xml'):
        """

        :param line_task: (source, target, coor, )
        :param path:
        :return:
        """
        tree = ec.parse(path)
        root_node = tree.getroot()
        root = root_node.find('.//root')



    def pack_shapes(self, input_task):
        max_width = 0
        max_height = 0
        source = ''
        output = ''
        






    def create_graph(self, graph_task):
        mx_graph = ec.Element('mxGraphModel', attrib=self.mx_graph_attribute)
        root = ec.SubElement(mx_graph, 'root')
        ec.SubElement(root, self.mx_cell, attrib=self.init_mx_graph_attribute)
        ec.SubElement(root, self.mx_cell, attrib=self.init_mx_cell_attribute)
        for task in graph_task:
            info: dict = task[0]
            task_depth: tuple = info['level']
            task_depth_len = len(task_depth)
            mx_cell = ec.SubElement(root, task_depth[0], attrib=task[1])
            for module in range(1, task_depth_len):
                mx_cell = ec.SubElement(mx_cell, task_depth[module], attrib=task[module + 1])
        xml_obj = ec.ElementTree(mx_graph)
        xml_obj.write('_test/test.xml')

    def graph_link(self, graph_task):
        pass


if __name__ == '__main__':
    graph = creat_graph()
    # with open('_test/test.txt', 'r') as obj:
    #     content = obj.read()
    #     content_list = content.split('\n')
    #     task_list = list()
    #     task_list.append(graph.init_task)
    #     last_task_info = get_task_info(graph.init_task)

