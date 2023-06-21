import time
import autogo_input
import re
from selenium.webdriver.support.wait import WebDriverWait
import generate_code
import regular_expression
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import error_code
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.common import WebDriverException
from selenium.common import exceptions as driver_err

g_xpath = regular_expression.Xpath()
regular = regular_expression.RegularClass()
g_user = ''
g_key = ''
g_browser = ''
g_link = ''
g_base_coor = ''
g_obj_coor = ''
g_table_type = {'include': 'x2', 'macro': 'x3', 'enum': 'x3', 'struct': 'x3', 'global_var': 'x4', 'union': 'x3',
                'input': 'x4', 'output': 'x4', 'return': 'x3', 'unit_var': 'x6', 'func_dynamic': '6x5'}

err = error_code.err_class()
WAIT_TIME = 15

# enums
information = 0
folder = 1
function = 2
object_type = ['Information', 'Heading', 'Functional']


def get_chrome_driver():
    global driver
    if g_browser == 'chrome' or g_browser == 'Chrome':
        from selenium.webdriver.chrome.service import Service
        # if g_visible is False:
        #     option = webdriver.ChromeOptions()
        #     option.add_argument('--headless')
        #     option.add_argument('--ignore-ssl-errors')
        #     option.add_argument('--ignore-certificate-errors')
        #     driver = webdriver.Chrome(service=Service('.driver/chromedriver.exe'), options=option)
        # else:
        option = webdriver.ChromeOptions()
        option.add_argument('--ignore-certificate-errors')
        option.add_argument('--ignore-ssl-errors')
        driver = webdriver.Chrome(service=Service('.driver/chromedriver.exe'), options=option)
    else:
        from selenium.webdriver.edge.service import Service
        # if g_visible is False:
        #     option = webdriver.EdgeOptions()
        #     option.add_argument('--headless')
        #     option.add_argument('--ignore-ssl-errors')
        #     option.add_argument('--ignore-certificate-errors')
        #     driver = webdriver.Edge(service=Service('.driver/msedgedriver.exe'), options=option)
        # else:
        option = webdriver.EdgeOptions()
        option.add_argument('--ignore-certificate-errors')
        option.add_argument('--ignore-ssl-errors')
        driver = webdriver.Edge(service=Service('.driver/msedgedriver.exe'), options=option)
    driver.get(g_link)


def get_cfg(config):
    res = err.ok
    global g_user, g_key, g_browser, g_link, g_base_coor, g_obj_coor
    g_user = str(config['user id'])
    g_key = str(config['user key'])
    g_browser = str(config['browser'])
    g_link = str(config['link'])
    g_base_coor = config['base folder']
    g_obj_coor = config['object folder']
    if base_coor_check(g_base_coor) is False:
        res = err.base_coor_err
    else:
        get_chrome_driver()
    return res


def base_coor_check(base_coor: str):
    res = True
    base_coor_list = base_coor.split('.')
    for e in base_coor_list:
        if e.isdigit() is False:
            res = False
    return res

# ----------------------------------------------------------------------------------------------------------------------
def get_xpath_index(fold_index: str):
    xpath_default = '/ul/li[$]'
    xpath_index = xpath_default.replace('$', fold_index)
    return xpath_index


def get_destination_xpath(coordinate: str):
    origin_xpath = g_xpath.origin_item
    xpath_res = origin_xpath
    coor_list = coordinate.split('.')
    for coor in coor_list:
        xpath_debris = get_xpath_index(str(coor))
        xpath_0 = xpath_res[:-2]
        xpath_1 = xpath_res[-2:]
        xpath_res = xpath_0 + xpath_debris + xpath_1
    return xpath_res


def open_fold_xpath(coordinate: str):
    coor_list = coordinate.split('.')
    xpath_list = list()
    origin_xpath = g_xpath.origin_folder
    for coor_idx in coor_list:
        xpath_idx = get_xpath_index(str(coor_idx))
        xpath = origin_xpath[:-2] + xpath_idx + origin_xpath[-2:]
        origin_xpath = xpath
        xpath_list.append(origin_xpath)
    for xpath in xpath_list:
        driver.find_element(By.XPATH, value=xpath).click()


# ----------------------------------------------------------------------------------------------------------------------


# -----------------------------------------------browser operate--------------------------------------------------------
def wait_loading():
    driver.implicitly_wait(WAIT_TIME)


def context_click(xpath: str):
    ActionChains(driver).context_click(driver.find_element(By.XPATH, value=xpath)).perform()


def double_click(xpath: str):
    ActionChains(driver).double_click(driver.find_element(By.XPATH, value=xpath)).perform()


def click(xpath: str):
    driver.find_element(By.XPATH, value=xpath).click()


def move_to_element(xpath: str):
    ActionChains(driver).scroll_to_element(driver.find_element(By.XPATH, value=xpath)).perform()


def send_key(xpath: str, content: str):
    driver.find_element(By.XPATH, value=xpath).send_keys(content)


def move_mouse_to(xpath: str):
    ActionChains(driver).move_to_element(to_element=driver.find_element(By.XPATH, value=xpath)).perform()


def input_title(content: str):
    send_key(g_xpath.input_title, content)


def select_item(xpath: str, content: str):
    Select(driver.find_element(By.XPATH, value=xpath)).select_by_visible_text(content)


def wait_item_load(xpath: str):
    locator = (By.XPATH, xpath)
    WebDriverWait(driver, WAIT_TIME).until(ec.presence_of_element_located(locator))


def input_save():
    move_to_element(g_xpath.input_title)
    driver.find_element(By.XPATH, value=g_xpath.input_title).send_keys(Keys.CONTROL, 's')

# -----------------------------------------------browser operate--------------------------------------------------------


def get_coor(xpath: str):
    info = xpath.replace(g_xpath.base_item, '')
    li_list = info.split('/')
    coor_list = list()
    for e in li_list:
        if re.search(regular.li_coor, e) is not None:
            num = re.search(regular.li_coor, e).group(1)
            coor_list.append(num)
        elif e == 'li':
            coor_list.append('1')
        else:
            continue
    res = '.'.join(coor_list)
    return res


def select_object_type(item_type):
    wait_item_load(g_xpath.draft)
    time.sleep(0.5)
    double_click(g_xpath.object_type)
    select_item(g_xpath.object_type_select, item_type)


def get_table_end_xpath(table_formate: str):
    start_fmt = int(table_formate.split('x')[0])
    end_fmt = int(table_formate.split('x')[1])
    tab_end = str((start_fmt - 1) * 10 + end_fmt)
    res = g_xpath.tab_xpath.replace('$', tab_end)
    return res


def tab_button_init(table_format: str):
    init = 2
    init_1 = 'x1'
    init_count = int(table_format.split('x')[0]) - 1
    for i in range(init_count):
        init_xpath = str(init) + init_1
        init_xpath = get_table_end_xpath(init_xpath)
        move_mouse_to(init_xpath)
        init = init + 1


def merge_unit_tab(start_fmt: str, end_fmt: str):
    start_row = start_fmt.split('x')[0]
    start_col = start_fmt.split('x')[1]
    end_row = end_fmt.split('x')[0]
    end_col = end_fmt.split('x')[1]
    start_xpath = g_xpath.tab_content.replace('$0', str(start_row))
    start_xpath = start_xpath.replace('$1', str(start_col))
    end_xpath = g_xpath.tab_content.replace('$0', str(end_row))
    end_xpath = end_xpath.replace('$1', str(end_col))
    start_ele = driver.find_element(By.XPATH, value=start_xpath)
    end_ele = driver.find_element(By.XPATH, value=end_xpath)
    ActionChains(driver).drag_and_drop(start_ele, end_ele).perform()
    click(g_xpath.merge_bt)
    click(g_xpath.select_merge)


def get_tab_input_xpath(tab_fmt: str):
    tab_fmt_list = tab_fmt.split('x')
    row = tab_fmt_list[0]
    col = tab_fmt_list[1]
    res = g_xpath.tab_content.replace('$0', row)
    res = res.replace('$1', col)
    return res


def set_tab_head_color(tab_fmt, col_skip=None):
    if col_skip is None:
        col_skip = []
    col = tab_fmt.split('x')[1]
    row_idx = 1
    col_idx = 1
    for i in range(int(col)):
        if len(col_skip) != 0:
            if col_skip.count(col_idx) != 0:
                col_idx = col_idx + 1
                continue
        set_tab_xpath = g_xpath.tab_content.replace('$0', str(row_idx))
        set_tab_xpath = set_tab_xpath.replace('$1', str(col_idx))
        click(set_tab_xpath)
        click(g_xpath.set_color_bt)
        click(g_xpath.color_gray)
        col_idx = col_idx + 1


def tab_process(table_format: str):
    tab_row = table_format.split('x')[0]
    tab_col = table_format.split('x')[1]
    click(g_xpath.paint_button)
    # time.sleep()
    click(g_xpath.insert_table)
    if int(tab_row) > 10:
        paint_row = 10
        remain_row = int(tab_row) - 10
        if int(tab_col) > 10:
            paint_col = 10
            remain_col = int(tab_col) - 10
            paint_fmt = str(paint_row) + 'x' + str(paint_col)
            tab_button_init(paint_fmt)
            table_end_xpath = get_table_end_xpath(paint_fmt)
            move_mouse_to(table_end_xpath)
            click(table_end_xpath)
            for i in range(remain_col):
                paint_col = 10 + i
                last_tab_xpath = g_xpath.tab_content.replace('$0', str(paint_row))
                last_tab_xpath = last_tab_xpath.replace('$1', str(paint_col))
                move_to_element(last_tab_xpath)
                click(last_tab_xpath)
                click(g_xpath.add_col_bt)
                click(g_xpath.add_col_select)
            paint_col = paint_col + 1
            for j in range(remain_row):
                paint_row = 10 + j
                last_tab_xpath = g_xpath.tab_content.replace('$0', str(paint_row))
                last_tab_xpath = last_tab_xpath.replace('$1', str(paint_col))
                move_to_element(last_tab_xpath)
                click(last_tab_xpath)
                click(g_xpath.add_row_bt)
                click(g_xpath.add_row_select)
        else:
            paint_col = int(tab_col)
            paint_fmt = str(paint_row) + 'x' + str(paint_col)
            tab_button_init(paint_fmt)
            table_end_xpath = get_table_end_xpath(paint_fmt)
            move_mouse_to(table_end_xpath)
            click(table_end_xpath)
            for i in range(remain_row):
                paint_row = 10 + i
                last_tab_xpath = g_xpath.tab_content.replace('$0', str(paint_row))
                last_tab_xpath = last_tab_xpath.replace('$1', str(paint_col))
                move_to_element(last_tab_xpath)
                click(last_tab_xpath)
                click(g_xpath.add_row_bt)
                click(g_xpath.add_row_select)
    elif int(tab_col) > 10:
        paint_row = int(tab_row)
        paint_col = 10
        remain_col = int(tab_col) - 10
        paint_fmt = str(paint_row) + 'x' + str(paint_col)
        tab_button_init(paint_fmt)
        table_end_xpath = get_table_end_xpath(paint_fmt)
        move_mouse_to(table_end_xpath)
        click(table_end_xpath)
        for i in range(remain_col):
            paint_col = 10 + i
            last_tab_xpath = g_xpath.tab_content.replace('$0', str(paint_row))
            last_tab_xpath = last_tab_xpath.replace('$1', str(paint_col))
            move_to_element(last_tab_xpath)
            click(last_tab_xpath)
            click(g_xpath.add_col_bt)
            click(g_xpath.add_col_select)
    else:
        paint_row = int(tab_row)
        paint_col = int(tab_col)
        paint_fmt = str(paint_row) + 'x' + str(paint_col)
        tab_button_init(paint_fmt)
        table_end_xpath = get_table_end_xpath(paint_fmt)
        move_mouse_to(table_end_xpath)
        click(table_end_xpath)


def fill_tab_content(tab_content: list):
    col_idx = 1
    for content in tab_content:
        row_idx = 1
        for item in content:
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, item)
            row_idx = row_idx + 1
        col_idx = col_idx + 1


def get_now_coor(base_coor: str, active):
    if active == 'inner':
        res = base_coor + '.1'
    elif active == 'after':
        if base_coor.count('.') == 0:
            res = str(int(base_coor) + 1)
        else:
            base_coor_list = base_coor.split('.')
            num = int(base_coor_list[-1]) + 1
            base_coor_list[-1] = str(num)
            res = '.'.join(base_coor_list)
    else:
        res = base_coor
    return res


def func_item_build_process(base_position: str, func_name, func_type, current_coor):
    func_info = func_type + '@' + func_name
    build_new_item(position=(base_position, current_coor), title=func_name, item_type=object_type[folder],
                   content=func_info)
    interaction_data_coor = get_now_coor(current_coor, 'inner')
    build_new_item(position=(current_coor, interaction_data_coor), title='Interaction data',
                   item_type=object_type[folder])
    input_coor = get_now_coor(interaction_data_coor, 'inner')
    build_new_item(position=(interaction_data_coor, input_coor), title='Input', item_type=object_type[information],
                   content=('input@' + func_info))
    output_coor = get_now_coor(input_coor, 'after')
    build_new_item((interaction_data_coor, output_coor), title='Output', item_type=object_type[information],
                   content=('output@' + func_info))
    return_coor = get_now_coor(output_coor, 'after')
    build_new_item(position=(interaction_data_coor, return_coor), title='Return', item_type=object_type[information],
                   content='return@' + func_info)
    unit_var_coor = get_now_coor(interaction_data_coor, 'after')
    build_new_item((current_coor, unit_var_coor), title='Unit Variables', item_type=object_type[information],
                   content=('unit_var@' + func_info))
    dynamic_coor = get_now_coor(unit_var_coor, 'after')
    build_new_item(position=(current_coor, dynamic_coor), title='Call Relationship', item_type=object_type[information],
                   content=('func_dynamic@' + func_info))
    flow_chart_coor = get_now_coor(dynamic_coor, 'after')
    build_new_item(position=(current_coor, flow_chart_coor), title='Flow Chart', item_type=object_type[information],
                   content='flow_chart')
    detail_folder_coor = get_now_coor(flow_chart_coor, 'after')
    build_new_item(position=(current_coor, detail_folder_coor), title='Function Logic Description',
                   item_type=object_type[folder])
    detail_coor = get_now_coor(detail_folder_coor, 'inner')
    build_new_item(position=(detail_folder_coor, detail_coor), title='Detailed Description',
                   item_type=object_type[function],
                   content=('detail@' + func_info))


def include_process():
    include_num = len(autogo_input.g_include_item)
    while True:
        if include_num == 0:
            break
        click(g_xpath.input_content)
        include_info = ['File Name']
        include_description = ['Description']
        include_info.extend(autogo_input.g_include_item)
        tab_content = list()
        tab_content.append(include_info)
        tab_content.append(include_description)
        include_len = len(include_info)
        tab_fmt = str(include_len) + g_table_type['include']
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
        break


def macro_process():
    macro_len = len(autogo_input.g_macro[0])
    while True:
        if macro_len == 0:
            break
        click(g_xpath.input_content)
        macro_names = ['Macro Name']
        descriptions = ['Description']
        macro_vars = ['Value']
        macro_names.extend(autogo_input.g_macro[0])
        macro_vars.extend(autogo_input.g_macro[1])
        tab_content = list()
        tab_content.append(macro_names)
        tab_content.append(descriptions)
        tab_content.append(macro_vars)

        macro_len = len(macro_names)
        tab_fmt = str(macro_len) + g_table_type['macro']
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
        break


def enum_item_process(enum_prop: str, xpath: list):
    enum_len = len(autogo_input.g_enum[0])
    while True:
        if enum_len == 0:
            break
        click(g_xpath.input_content)
        enum_idx = int(enum_prop.replace('enum', ''))
        enum_members = ['Member']
        enum_vals = ['Values']
        descriptions = ['Description']
        enum_members.extend(autogo_input.g_enum[1][enum_idx])
        enum_vals.extend(autogo_input.g_enum[2][enum_idx])
        tab_content = list()
        tab_content.append(enum_members)
        tab_content.append(enum_vals)
        tab_content.append(descriptions)
        enum_len = len(enum_members)
        tab_fmt = str(enum_len) + g_table_type['enum']
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
        input_save()
        click(xpath[1])
        select_object_type(object_type[information])
        click(xpath[1])
        break


def struct_item_process(struct_prop, xpath: list):
    st_num = len(autogo_input.g_struct[0])
    while True:
        if st_num == 0:
            break
        click(g_xpath.input_content)
        st_idx = int(struct_prop.replace('struct', ''))
        st_members = ['Member']
        st_types = ['Type']
        descriptions = ['Description']
        st_members.extend(autogo_input.g_struct[2][st_idx])
        st_types.extend(autogo_input.g_struct[1][st_idx])
        tab_content = list()
        tab_content.append(st_members)
        tab_content.append(st_types)
        tab_content.append(descriptions)

        st_len = len(st_members)
        tab_fmt = str(st_len) + g_table_type['struct']
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
        input_save()
        click(xpath[1])
        select_object_type(object_type[information])
        click(xpath[1])
        break


def union_item_process(union_prop, xpath: list):
    un_num = len(autogo_input.g_union[0])
    while True:
        if un_num == 0:
            break
        un_idx = int(union_prop.replace('union', ''))
        un_members = ['Member']
        un_types = ['Type']
        descriptions = ['Description']
        un_members.extend(autogo_input.g_union[2][un_idx])
        un_types.extend(autogo_input.g_union[1][un_idx])
        tab_content = list()
        tab_content.append(un_members)
        tab_content.append(un_types)
        tab_content.append(descriptions)
        un_len = len(un_members)
        tab_fmt = str(un_len) + g_table_type['union']
        # operate
        click(g_xpath.input_content)
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
        input_save()
        click(xpath[1])
        select_object_type(object_type[information])
        click(xpath[1])
        break


def global_var_item_process():
    var_names = ['Global Variable']
    var_types = ['Data Type']
    var_init_vals = ['Initial Value']
    des = ['Description']
    var_names.extend(autogo_input.g_global_var[0])
    var_types.extend(autogo_input.g_global_var[1])
    var_len = len(autogo_input.g_global_var[0])
    content_len = len(var_names)
    while True:
        if var_len == 0:
            break
        tab_fmt = str(content_len) + g_table_type['global_var']
        tab_content = list()
        tab_content.append(var_names)
        tab_content.append(var_types)
        tab_content.append(var_init_vals)
        tab_content.append(des)
        click(g_xpath.input_content)
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
        break


def detail_process(content: str):
    content_info = content.replace('detail@', '')
    content_info = content_info.split('@')
    func_type = content_info[0]
    func_name = content_info[1]
    if func_type == 'local':
        local_func_list = autogo_input.g_local_func
        try:
            obj_func_idx = local_func_list.index(func_name)
            func_content = autogo_input.detail_pro(func_type, obj_func_idx)
        except Exception:
            func_content = ''
    else:
        global_func_list = autogo_input.g_global_func
        try:
            obj_func_idx = global_func_list.index(func_name)
            func_content = autogo_input.detail_pro(func_type, obj_func_idx)
        except Exception:
            func_content = ''
    click(g_xpath.input_content)
    send_key(g_xpath.input_content, func_content)


def enum_build_process(base_position: str):
    enum_items = autogo_input.g_enum[0]
    enum_items_len = len(enum_items)
    current_coor = get_now_coor(base_position, 'inner')
    if enum_items_len != 0:
        for enum_items_idx in range(enum_items_len):
            item_name = enum_items[enum_items_idx] + '(enum)'
            content = 'enum' + str(enum_items_idx)
            build_new_item(position=(base_position, current_coor), title=item_name, item_type=object_type[information],
                           content=content)
            current_coor = get_now_coor(current_coor, 'after')
        return current_coor
    else:
        return current_coor


def struct_build_process(base_position: str, current_coor):
    struct_items = autogo_input.g_struct[0]
    st_item_len = len(struct_items)
    current_item_coor = current_coor
    if st_item_len != 0:
        for st_item_idx in range(st_item_len):
            item_name = struct_items[st_item_idx] + '(struct)'
            content = 'struct' + str(st_item_idx)
            build_new_item(position=(base_position, current_item_coor), title=item_name,
                           item_type=object_type[information], content=content)
            current_item_coor = get_now_coor(current_item_coor, 'after')
        return current_item_coor
    else:
        return current_coor


def union_build_process(base_position: str, current_coor):
    union_item = autogo_input.g_union[0]
    un_item_len = len(union_item)
    current_item_coor = current_coor
    if un_item_len != 0:
        for un_item_idx in range(un_item_len):
            item_name = union_item[un_item_idx] + '(union)'
            content = 'union' + str(un_item_idx)
            build_new_item(position=(base_position, current_item_coor), title=item_name,
                           item_type=object_type[information], content=content)
            current_item_coor = get_now_coor(current_item_coor, 'after')
    else:
        pass


def func_build_process(content: str):
    func_type = content.split('@')[0]
    func_name = content.split('@')[1]
    if func_type == 'local':
        func_names = generate_code.g_local_func_names
        try:
            func_idx = func_names.index(func_name)
        except Exception:
            func_idx = 0
        prototype = autogo_input.g_local_func_prototype[func_idx]
    else:
        func_names = generate_code.g_global_func_names
        try:
            func_idx = func_names.index(func_name)
        except Exception:
            func_idx = 0
        prototype = autogo_input.g_global_func_prototype[func_idx]
    fill_info = "Prototype: " + prototype
    click(g_xpath.input_content)
    send_key(g_xpath.input_content, fill_info)


def input_process(content: str):
    func_info = content.replace('input@', '')
    func_type = func_info.split('@')[0]
    func_name = func_info.split('@')[1]
    param_list = autogo_input.get_func_param(func_name, func_type)
    param_mode = param_list[0]
    param_len = len(param_mode)
    param_types = list()
    param_members = list()
    for idx in range(param_len):
        if param_mode[idx] == 'input':
            param_type = param_list[1][idx]
            param_member = param_list[2][idx]
            param_types.append(param_type)
            param_members.append(param_member)
    input_item_len = len(param_types)
    if input_item_len != 0:
        name_list = ['Name']
        type_list = ['Type']
        scope_list = ['Scope']
        description = ['Description']
        tab_content = list()
        name_list.extend(param_members)
        type_list.extend(param_types)
        tab_content.append(name_list)
        tab_content.append(type_list)
        tab_content.append(scope_list)
        tab_content.append(description)
        tab_fmt = str(len(name_list)) + g_table_type['input']
        click(g_xpath.input_content)
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
    else:
        click(g_xpath.input_content)
        send_key(g_xpath.input_content, 'None')


def output_process(content: str):
    func_info = content.replace('output@', '')
    func_type = func_info.split('@')[0]
    func_name = func_info.split('@')[1]
    param_list = autogo_input.get_func_param(func_name, func_type)
    param_mode = param_list[0]
    param_len = len(param_mode)
    param_types = list()
    param_members = list()
    for idx in range(param_len):
        if param_mode[idx] == 'output':
            param_type = param_list[1][idx]
            param_member = param_list[2][idx]
            param_types.append(param_type)
            param_members.append(param_member)
    output_item_len = len(param_types)
    if output_item_len != 0:
        name_list = ['Name']
        type_list = ['Type']
        scope_list = ['Scope']
        description = ['Description']
        tab_content = list()
        name_list.extend(param_members)
        type_list.extend(param_types)
        tab_content.append(name_list)
        tab_content.append(type_list)
        tab_content.append(scope_list)
        tab_content.append(description)
        tab_fmt = str(len(name_list)) + g_table_type['output']
        click(g_xpath.input_content)
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
    else:
        click(g_xpath.input_content)
        send_key(g_xpath.input_content, 'None')


def return_item_process(content: str):
    func_info = content.replace('return@', '')
    func_type = func_info.split('@')[0]
    func_name = func_info.split('@')[1]
    return_info = autogo_input.return_info_process(func_name, func_type)
    if return_info != 'None':
        return_type = return_info.split('@')[0]
        return_var = return_info.split('@')[1]
        return_names = ['Name']
        return_types = ['Type']
        return_des = ['Description']
        return_names.append(return_var)
        return_types.append(return_type)
        tab_content = list()
        tab_content.append(return_names)
        tab_content.append(return_types)
        tab_content.append(return_des)
        tab_fmt = '2' + g_table_type['return']
        click(g_xpath.input_content)
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
    else:
        click(g_xpath.input_content)
        send_key(g_xpath.input_content, 'None')


def unit_var_item_process(content: str):
    func_info = content.replace('unit_var@', '')
    func_type = func_info.split('@')[0]
    func_name = func_info.split('@')[1]
    unit_type_info, unit_name_info = autogo_input.get_unit_var(func_name, func_type)
    unit_len = len(unit_name_info)
    if unit_len != 0:
        unit_names = ['Variable Name']
        unit_types = ['Variable Type']
        unit_ranges = ['Range']
        unit_init = ['Initial Value']
        des = ['Description']
        unit_source = ['Source']
        unit_names.extend(unit_name_info)
        unit_types.extend(unit_type_info)
        tab_fmt = str(len(unit_names)) + g_table_type['unit_var']
        tab_content = list()
        tab_content.append(unit_names)
        tab_content.append(unit_types)
        tab_content.append(unit_ranges)
        tab_content.append(unit_init)
        tab_content.append(des)
        tab_content.append(unit_source)
        click(g_xpath.input_content)
        tab_process(tab_fmt)
        fill_tab_content(tab_content)
        set_tab_head_color(tab_fmt)
    else:
        click(g_xpath.input_content)
        send_key(g_xpath.input_content, 'None')


def func_dynamic_item_process(content):
    func_info = content.replace('func_dynamic@', '')
    func_type = func_info.split('@')[0]
    func_name = func_info.split('@')[1]
    called_items = ['Called Functions']
    called_sources = ['Called Source']
    # black_0 = []
    func_proto = ['Function Name']
    # black_1 = []
    calling_items = ['Calling Functions']
    calling_sources = ['Calling Source']
    func_proto.append(func_name)
    tab_fmt = g_table_type['func_dynamic']
    tab_content = list()
    tab_content.append(called_items)
    tab_content.append(called_sources)
    # tab_content.append(black_0)
    tab_content.append(func_proto)
    # tab_content.append(black_1)
    tab_content.append(calling_items)
    tab_content.append(calling_sources)
    click(g_xpath.input_content)
    tab_process(tab_fmt)
    fill_tab_content(tab_content)
    set_tab_head_color(tab_fmt)
    merge_unit_tab('2x3', '6x3')


# def check_element(xpath: str):
#     locator = (By.XPATH, xpath)
#     try:
#         res = WebDriverWait(driver, 3).until(ec.presence_of_element_located(locator))
#     except driver_err.TimeoutException:
#         res = False
#     return res
#
# def autogo_test():
#     coor = '24'
#     xpath = get_destination_xpath(coor)
#     res = check_element(xpath)
#     return res

def func_process(base_position, func_type='local'):
    fun_coor = get_now_coor(base_position, 'inner')
    if func_type == 'local':
        func_items = autogo_input.g_local_func
        func_num = len(func_items)
        obj_current_coor = fun_coor
    else:
        func_items = autogo_input.g_global_func
        func_num = len(func_items)
        obj_current_coor = fun_coor
    if func_num != 0:
        for func_idx in range(func_num):
            func_name = func_items[func_idx]
            func_item_build_process(base_position, func_name, func_type, obj_current_coor)
            obj_current_coor = get_now_coor(obj_current_coor, 'after')


def build_new_item(position: tuple, title: str, item_type=object_type[function], content: str = None):
    xpath = get_destination_xpath(position[0])
    end_xpath = get_destination_xpath(position[1])
    xpath_list = [xpath, end_xpath]
    time.sleep(0.5)
    move_to_element(xpath)
    context_click(xpath)
    click(g_xpath.insert_new_child)
    input_title(title)
    while True:
        if content is None:
            pass
        elif content == 'include':
            include_process()
        elif content == 'macro':
            macro_process()
        elif content.count('enum') != 0:
            enum_item_process(content, xpath_list)
            break
        elif content.count('struct') != 0:
            struct_item_process(content, xpath_list)
            break
        elif content.count('union'):
            union_item_process(content, xpath_list)
            break
        elif content.startswith('local@') is True or content.startswith('global@') is True:
            func_build_process(content)
        elif content == 'global_var':
            global_var_item_process()
        elif content == 'dynamic':
            pass
        elif content.startswith('input@') is True:
            input_process(content)
        elif content.startswith('output@') is True:
            output_process(content)
        elif content.startswith('return@') is True:
            return_item_process(content)
        elif content.startswith('unit_var@') is True:
            unit_var_item_process(content)
        elif content.startswith('func_dynamic@') is True:
            func_dynamic_item_process(content)
        elif content == 'flow_chart':
            pass
        elif content.startswith('detail@') != 0:
            detail_process(content)
        elif content == 'test':
            # autogo_test()
            pass
        input_save()
        click(end_xpath)
        select_object_type(item_type)
        click(end_xpath)
        break


def auto_go_active(component: str, config: dict):
    res = get_cfg(config)
    global g_base_coor
    c_file_name = component + '.c'
    coordination = g_base_coor
    while True:
        if res != err.ok:
            break
        # register
        driver.maximize_window()
        driver.find_element(By.ID, value='user').send_keys(g_user)
        driver.find_element(By.ID, value='password').send_keys(g_key)
        driver.find_element(By.XPATH, value='//*[@id="loginForm"]/div/div[2]/input').submit()
        wait_loading()
        open_fold_xpath(coordination)
        component_coor = g_obj_coor
        build_new_item(position=(coordination, component_coor), title=component, item_type=object_type[folder])
        c_file_fold_coor = get_now_coor(component_coor, 'inner')
        build_new_item(position=(component_coor, c_file_fold_coor), title=c_file_name, item_type=object_type[folder])
        component_design_coor = get_now_coor(c_file_fold_coor, 'inner')
        build_new_item(position=(c_file_fold_coor, component_design_coor), item_type=object_type[information],
                       title='Component Design Constraints')
        head_file_coor = get_now_coor(component_design_coor, 'after')
        build_new_item(position=(c_file_fold_coor, head_file_coor), title='Header Files',
                       item_type=object_type[information],
                       content='include')
        component_def_coor = get_now_coor(head_file_coor, 'after')
        build_new_item(position=(c_file_fold_coor, component_def_coor), title='Component Definitions',
                       item_type=object_type[folder])
        macro_folder_coor = get_now_coor(component_def_coor, 'inner')
        build_new_item(position=(component_def_coor, macro_folder_coor), title='Component Macro Definitions ',
                       item_type=object_type[folder])
        macro_coor = get_now_coor(macro_folder_coor, 'inner')
        build_new_item(position=(macro_folder_coor, macro_coor), title='List of Component Macro',
                       item_type=object_type[information],
                       content='macro')
        component_type_coor = get_now_coor(macro_folder_coor, 'after')
        build_new_item(position=(component_def_coor, component_type_coor), title='Component Type Declarations',
                       item_type=object_type[folder])
        enum_current_coor = enum_build_process(component_type_coor)
        struct_current_coor = struct_build_process(component_type_coor, enum_current_coor)
        union_build_process(component_type_coor, struct_current_coor)
        # --------------------------------------------------------------------------------------------------------------
        component_var_def_coor = get_now_coor(component_type_coor, 'after')
        build_new_item(position=(component_def_coor, component_var_def_coor), title='Component Variable Definitions',
                       item_type=object_type[folder])
        global_var_coor = get_now_coor(component_var_def_coor, 'inner')
        build_new_item(position=(component_var_def_coor, global_var_coor), title='Global Variable Definitions',
                       item_type=object_type[information], content='global_var')
        # --------------------------------------------------------------------------------------------------------------
        dynamic_behavior_coor = get_now_coor(component_def_coor, 'after')
        build_new_item(position=(c_file_fold_coor, dynamic_behavior_coor), title='Dynamic Behavior',
                       item_type=object_type[folder])
        dynamic_detail_coor = get_now_coor(dynamic_behavior_coor, 'inner')
        build_new_item(position=(dynamic_behavior_coor, dynamic_detail_coor), title='Dynamic Behavior Detail',
                       item_type=object_type[information], content='dynamic')
        sw_func_coor = get_now_coor(dynamic_behavior_coor, 'after')
        build_new_item(position=(c_file_fold_coor, sw_func_coor), title='Software Functions',
                       item_type=object_type[folder])
        # sw_func_coor = coordination
        local_func_coor = get_now_coor(sw_func_coor, 'inner')
        build_new_item((sw_func_coor, local_func_coor), 'Local Functions ', object_type[folder])
        func_process(local_func_coor, func_type='local')
        global_func_coor = get_now_coor(local_func_coor, 'after')
        build_new_item(position=(sw_func_coor, global_func_coor), title='Global Functions',
                       item_type=object_type[folder])
        func_process(global_func_coor, func_type='global')
        driver.close()
        # print(autogo_test())
        break
    return res


def auto_go_program(config: dict):
    while True:
        component_name = generate_code.g_file_name.split('.')[0]
        if err.void_check(component_name) is True:
            res = err.no_load
            break
        autogo_input.get_information()
        try:
            res = auto_go_active(component_name, config)
        except (WebDriverException, Exception):
            res = err.driver_interrupt
            break
        break
    return res

