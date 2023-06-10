import json
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

g_xpath = regular_expression.Xpath()
regular = regular_expression.RegularClass()
g_user = ''
g_key = ''
g_browser = ''
g_link = ''
g_table_type = {'include': 'x2', 'macro': 'x3', 'enum': 'x3', 'struct': 'x3', 'global_var': 'x3', 'union': 'x3'}

err = error_code.err_class()
WAIT_TIME = 30

# enums
information = 0
folder = 1
function = 2
object_type = ['Information', 'Heading', 'Functional']


def get_chrome_driver():
    global driver
    if g_browser == 'chrome' or g_browser == 'Chrome':
        from selenium.webdriver.chrome.service import Service
        # option = webdriver.chrome.
        driver = webdriver.Chrome(service=Service('chromedriver.exe'))
    else:
        from selenium.webdriver.edge.service import Service
        driver = webdriver.Edge(service=Service('msedgedriver.exe'))
    driver.get(g_link)


def get_cfg():
    res = err.ok
    global g_user, g_key, g_browser, g_link
    with open('config.json', mode='r') as cfg_obj:
        cfg: dict = json.load(cfg_obj)
        cfg_key_list = list(cfg.keys())
        if cfg_key_list.count('user') != 0 and cfg_key_list.count('password') != 0 and cfg_key_list.count(
                'browser') != 0 and cfg_key_list.count('link') != 0:
            g_user = cfg['user']
            g_key = cfg['password']
            g_browser = cfg['browser']
            g_link = cfg['link']
        else:
            res = err.cfg_err
    get_chrome_driver()
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
    wait_loading()
    # destination_folder_xpath = xpath_list[-1][:-1] + 'a'
    # return destination_folder_xpath


# ----------------------------------------------------------------------------------------------------------------------


# -----------------------------------------------browser operate--------------------------------------------------------
def wait_loading():
    driver.implicitly_wait(WAIT_TIME)


def context_click(xpath: str):
    ActionChains(driver).context_click(driver.find_element(By.XPATH, value=xpath)).perform()
    wait_loading()


def double_click(xpath: str):
    ActionChains(driver).double_click(driver.find_element(By.XPATH, value=xpath)).perform()
    wait_loading()


def click(xpath: str):
    driver.find_element(By.XPATH, value=xpath).click()
    # driver.execute_script('arguments[0].click();', driver.find_element(By.XPATH, xpath))
    wait_loading()


def move_to_element(xpath: str):
    ActionChains(driver).scroll_to_element(driver.find_element(By.XPATH, value=xpath)).perform()


def send_key(xpath: str, content: str):
    driver.find_element(By.XPATH, value=xpath).send_keys(content)
    wait_loading()


def move_mouse_to(xpath: str):
    ActionChains(driver).move_to_element(to_element=driver.find_element(By.XPATH, value=xpath)).perform()


def input_title(content: str):
    send_key(g_xpath.input_title, content)


def select_item(xpath: str, content: str):
    Select(driver.find_element(By.XPATH, value=xpath)).select_by_visible_text(content)
    wait_loading()


def wait_item_load(xpath: str):
    locator = (By.XPATH, xpath)
    WebDriverWait(driver, WAIT_TIME).until(ec.presence_of_element_located(locator))


def input_save():
    move_to_element(g_xpath.input_title)
    driver.find_element(By.XPATH, value=g_xpath.input_title).send_keys(Keys.CONTROL, 's')
    wait_loading()


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


def get_tab_input_xpath(tab_fmt: str):
    tab_fmt_list = tab_fmt.split('x')
    row = tab_fmt_list[0]
    col = tab_fmt_list[1]
    res = g_xpath.tab_content.replace('$0', row)
    res = res.replace('$1', col)
    return res


def set_tab_head_color(tab_fmt):
    col = tab_fmt.split('x')[1]
    row_idx = 1
    col_idx = 1
    for i in range(int(col)):
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


def include_process():
    include_num = len(autogo_input.g_include_item)
    while True:
        if include_num == 0:
            break
        click(g_xpath.input_content)
        include_info = ['File Name']
        include_description = ['Description']
        include_info.extend(autogo_input.g_include_item)
        include_len = len(include_info)
        tab_fmt = str(include_len) + g_table_type['include']
        tab_process(tab_fmt)
        row_idx = 1
        for include_item in include_info:
            col_idx = 1
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, include_item)
            row_idx = row_idx + 1
        row_idx = 1
        for des_item in include_description:
            col_idx = 2
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, des_item)
            row_idx = row_idx + 1
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
        macro_len = len(macro_names)
        tab_fmt = str(macro_len) + g_table_type['macro']
        tab_process(tab_fmt)
        row_idx = 1
        for macro_item in macro_names:
            col_idx = 1
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, macro_item)
            row_idx = row_idx + 1
        row_idx = 1
        for des_item in descriptions:
            col_idx = 2
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, des_item)
            row_idx = row_idx + 1
        row_idx = 1
        for macro_var in macro_vars:
            col_idx = 3
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, macro_var)
            row_idx = row_idx + 1
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
        enum_len = len(enum_members)
        tab_fmt = str(enum_len) + g_table_type['enum']
        tab_process(tab_fmt)
        row_idx = 1
        for en_member in enum_members:
            col_idx = 1
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, en_member)
            row_idx = row_idx + 1
        row_idx = 1
        for des_item in descriptions:
            col_idx = 2
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, des_item)
            row_idx = row_idx + 1
        row_idx = 1
        for en_val in enum_vals:
            col_idx = 3
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, en_val)
            row_idx = row_idx + 1
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
        st_len = len(st_members)
        tab_fmt = str(st_len) + g_table_type['struct']
        tab_process(tab_fmt)
        row_idx = 1
        for st_member in st_members:
            col_idx = 1
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, st_member)
            row_idx = row_idx + 1
        row_idx = 1
        for st_type in st_types:
            col_idx = 2
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, st_type)
            row_idx = row_idx + 1
        row_idx = 1
        for des_item in descriptions:
            col_idx = 3
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, des_item)
            row_idx = row_idx + 1
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
        click(g_xpath.input_content)
        un_idx = int(union_prop.replace('union', ''))
        un_members = ['Member']
        un_types = ['Type']
        descriptions = ['Description']
        un_members.extend(autogo_input.g_union[2][un_idx])
        un_types.extend(autogo_input.g_union[1][un_idx])
        un_len = len(un_members)
        tab_fmt = str(un_len) + g_table_type['union']
        tab_process(tab_fmt)
        row_idx = 1
        for un_member in un_members:
            col_idx = 1
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, un_member)
            row_idx = row_idx + 1
        row_idx = 1
        for un_type in un_types:
            col_idx = 2
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, un_type)
            row_idx = row_idx + 1
        row_idx = 1
        for des_item in descriptions:
            col_idx = 3
            tab_input = str(row_idx) + 'x' + str(col_idx)
            input_xpath = get_tab_input_xpath(tab_input)
            click(input_xpath)
            send_key(input_xpath, des_item)
            row_idx = row_idx + 1
        set_tab_head_color(tab_fmt)
        input_save()
        click(xpath[1])
        select_object_type(object_type[information])
        click(xpath[1])
        break


def detail_process(func_type, func_name):
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


def func_item_process(base_position: str, func_name, func_type, current_coor):
    build_new_item(position=(base_position, current_coor), title=func_name, item_type=object_type[folder])
    interaction_data_coor = get_now_coor(current_coor, 'inner')
    build_new_item(position=(current_coor, interaction_data_coor), title='Interaction data',
                   item_type=object_type[folder])
    input_coor = get_now_coor(interaction_data_coor, 'inner')
    build_new_item(position=(interaction_data_coor, input_coor), title='Input', item_type=object_type[information],
                   content='input')
    output_coor = get_now_coor(input_coor, 'after')
    build_new_item((interaction_data_coor, output_coor), title='Output', item_type=object_type[information],
                   content='output')
    return_coor = get_now_coor(output_coor, 'after')
    build_new_item(position=(interaction_data_coor, return_coor), title='Return', item_type=object_type[information],
                   content='return')
    unit_var_coor = get_now_coor(interaction_data_coor, 'after')
    build_new_item((current_coor, unit_var_coor), title='Unit Variables', item_type=object_type[information],
                   content='unit_var')
    dynamic_coor = get_now_coor(unit_var_coor, 'after')
    build_new_item(position=(current_coor, dynamic_coor), title='Call Relationship', item_type=object_type[information],
                   content='func_dynamic')
    flow_chart_coor = get_now_coor(dynamic_coor, 'after')
    build_new_item(position=(current_coor, flow_chart_coor), title='Flow Chart', item_type=object_type[information],
                   content='flow_chart')
    detail_coor = get_now_coor(flow_chart_coor, 'after')
    build_new_item(position=(current_coor, detail_coor), title='Detailed Description', item_type=object_type[function],
                   content=(func_type + '@detail@' + func_name))


def enum_process(base_position: str):
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


def struct_process(base_position: str, current_coor):
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


def union_process(base_position: str, current_coor):
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
            func_item_process(base_position, func_name, func_type, obj_current_coor)
            obj_current_coor = get_now_coor(obj_current_coor, 'after')


def build_new_item(position: tuple, title: str, item_type=object_type[function], content: str = None):
    xpath = get_destination_xpath(position[0])
    end_xpath = get_destination_xpath(position[1])
    xpath_list = [xpath, end_xpath]
    wait_loading()
    time.sleep(0.5)
    # click(xpath)
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
        elif content == 'global_var':
            pass
        elif content == 'dynamic':
            pass
        elif content == 'input':
            pass
        elif content == 'output':
            pass
        elif content == 'return':
            pass
        elif content == 'unit_var':
            pass
        elif content == 'func_dynamic':
            pass
        elif content == 'flow_chart':
            pass
        elif content.count('detail') != 0:
            content_info = content.split('@')
            func_type = content_info[0]
            func_name = content_info[2]
            detail_process(func_type, func_name)
        input_save()
        click(end_xpath)
        select_object_type(item_type)
        click(end_xpath)
        break


def auto_go_active(component: str):
    start = time.time()
    res = get_cfg()
    c_file_name = component + '.c'
    coordination = '23'  # test
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

        component_coor = get_now_coor(coordination, 'inner')
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
        enum_current_coor = enum_process(component_type_coor)
        struct_current_coor = struct_process(component_type_coor, enum_current_coor)
        union_process(component_type_coor, struct_current_coor)
        dynamic_behavior_coor = get_now_coor(component_def_coor, 'after')
        build_new_item(position=(c_file_fold_coor, dynamic_behavior_coor), title='Dynamic Behavior',
                       item_type=object_type[folder])
        dynamic_detail_coor = get_now_coor(dynamic_behavior_coor, 'inner')
        build_new_item(position=(dynamic_behavior_coor, dynamic_detail_coor), title='Dynamic Behavior Detail',
                       item_type=object_type[information], content='dynamic')
        sw_func_coor = get_now_coor(dynamic_behavior_coor, 'after')
        build_new_item(position=(c_file_fold_coor, sw_func_coor), title='Software Functions',
                       item_type=object_type[folder])
        local_func_coor = get_now_coor(sw_func_coor, 'inner')
        build_new_item((sw_func_coor, local_func_coor), 'Local Functions ', object_type[folder])
        func_process(local_func_coor, func_type='local')
        global_func_coor = get_now_coor(local_func_coor, 'after')
        build_new_item(position=(sw_func_coor, global_func_coor), title='Global Functions', item_type=object_type[folder])
        func_process(global_func_coor, func_type='global')
        end = time.time()
        print('time: ', end - start)
        # time.sleep(5)
        input('Auto go is testing...')
        driver.close()
        break
        # print(driver.page_source)


def auto_go_program():
    component_name = generate_code.g_file_name.split('.')[0]
    autogo_input.get_information()
    auto_go_active(component_name)
    # auto_go_active()
