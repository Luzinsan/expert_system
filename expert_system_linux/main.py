import dearpygui.dearpygui as dpg
import numpy as np

estimates = np.array([1, 1, 1])
count_alter = 0
WIDTH = 1920
HEIGHT = 1080

dpg.create_context()


## region ######################################################Main Window########################################################
def add_alternative(sender, new_count_alter):
    dpg.delete_item('next_to_experts')
    dpg.add_button(label="Продолжить", tag='next_to_experts', width=150, callback=experts, parent='Main')
    global count_alter
    if new_count_alter > count_alter:
        dpg.add_input_text(tag=f'alter_text{new_count_alter - 1}', multiline=True,
                           default_value=f'Альтернатива решения #{new_count_alter}',
                           height=50, parent='alternatives_window', width=1850)
    else:
        dpg.delete_item(f'alter_text{count_alter - 1}')
    count_alter = new_count_alter


with dpg.window(label="Main", tag="Main", width=WIDTH, height=HEIGHT):
    dpg.add_child_window(height=200)
    with dpg.group(horizontal=True):
        dpg.add_text(default_value='Введите рассматриваемую цель: ')
        dpg.add_input_text(tag='target', hint='цель для решения проблемы', width=1495)
    with dpg.group(horizontal=True):
        dpg.add_text(default_value='Введите количество экспертов: ')
        dpg.add_input_int(tag='experts', default_value=3, min_value=1, min_clamped=True, width=223)
    with dpg.group(horizontal=True):
        dpg.add_text(default_value='Введите количество альтернатив: ')
        dpg.add_input_int(tag='alternatives', default_value=count_alter,
                          min_value=1, min_clamped=True, max_value=10, max_clamped=True,
                          width=200, callback=add_alternative)
    dpg.add_child_window(tag='alternatives_window', height=558)
# endregion


# region #######################################################--SWITCHing--####################################################
def on_exit(sender, app_data, user_data):
    print("closed")


def go_back(sender, app_data, expert):
    dpg.configure_item(f'evaluation{expert}', show=False)
    dpg.configure_item(f'evaluation{expert - 1}', show=True)


def switch_expert(sender, app_data, expert_data):
    # expert_data = [number_of_expert, count_of_alternatives, count_of_experts]
    global estimates
    estimates[expert_data[0]] = [[dpg.get_value(f'mark{expert_data[0]}{i}{j}')
                                  for j in range(expert_data[1])]
                                 for i in range(expert_data[1])]
    dpg.configure_item(f'evaluation{expert_data[0]}', show=False)
    if expert_data[0] + 1 != expert_data[2]:
        dpg.configure_item(f'evaluation{expert_data[0] + 1}', show=True)
    else:
        ranging([expert_data[2], expert_data[1]])
# endregion


def coefficient_variation():
    pass


def ranging(user_data):
    global estimates
    dpg.delete_item('list_alternatives')
    count_expert, count_alternatives = user_data
    common_matrix = np.empty((count_alternatives, count_alternatives), dtype=np.bool_)
    for i in range(0, count_alternatives):
        for j in range(0, count_alternatives):
            sum_marks = 0
            for expert in range(count_expert):
                sum_marks += estimates[expert][i][j]
            common_matrix[i][j] = True if sum_marks > count_expert / 2 else False
    with dpg.child_window(tag=f'range_window', parent='experts_window', height=720, width=1920):
        for expert in range(count_expert):
            with dpg.group(horizontal=True, tag=f"group_expert{expert}"):
                dpg.add_text(default_value=f"Эксперт #{expert + 1}: ")
                dpg.add_input_text(default_value=dpg.get_value(f'role{expert}'), readonly=True)
        # проранжированные альтернативы
        with dpg.table(tag=f'range_table',
                       row_background=True,
                       resizable=True, policy=dpg.mvTable_SizingStretchProp,
                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                       borders_outerV=True):
            dpg.add_table_column(label='Альтернативы', tag=f'alter_col')
            dpg.add_table_column(label='Ранг', tag=f'marks_col')
            calc_marks = np.empty(count_alternatives, dtype=np.int64)
            for i in range(count_alternatives):
                with dpg.table_row(tag=f'row{i}'):
                    dpg.add_text(default_value=dpg.get_value(f'alter_text{i}'), tag=f'alter_row{i}')
                    calc_marks[i] = sum(common_matrix[i])
                    dpg.add_text(tag=f'common_range{i}', default_value=calc_marks[i])

            not_viewed_indices = list(range(count_alternatives))
            viewed_indices = []
            rank = 1
            while rank < count_alternatives + 1:
                # узнаём максимальную сумму среди непросморенных
                max_value = np.max(calc_marks[not_viewed_indices])
                # реализуем связные ранги
                temp_lst = list(np.where(calc_marks == max_value)[0])
                # отсекаем просмотренные индексы
                temp_lst = [item for item in temp_lst if item not in viewed_indices]
                # убираем найденные индексы в стороны - теперь они просмотрены
                not_viewed_indices = [item for item in not_viewed_indices if item not in temp_lst]
                viewed_indices += temp_lst
                # присваиваем связные ранги
                calc_marks[temp_lst] = sum(range(rank, rank + len(temp_lst))) / len(temp_lst)
                rank += len(temp_lst)
            [dpg.set_value(f'common_range{i}', calc_marks[i]) for i in range(count_alternatives)]
        with dpg.group(horizontal=True):
            dpg.add_text(default_value="Наилучшая альтернатива: ")
            dpg.add_input_text(default_value=dpg.get_value(f'alter_text{np.argmin(calc_marks)}'),
                               readonly=True, multiline=True)


def check_mark(sender, checked_mark, reflected_mark):
    if checked_mark == dpg.get_value(f'mark{reflected_mark[0]}{reflected_mark[1]}{reflected_mark[2]}'):
        dpg.set_value(f'mark{reflected_mark[0]}{reflected_mark[1]}{reflected_mark[2]}', not checked_mark)


def experts():
    dpg.delete_item('list_alternatives')
    dpg.delete_item('experts_window')
    dpg.set_value('output_target', dpg.get_value('target'))
    count_experts = dpg.get_value('experts')
    count_alternatives = dpg.get_value('alternatives')
    alternatives = [dpg.get_value(f'alter_text{expert}') for expert in range(count_alternatives)]
    dpg.add_listbox(tag='list_alternatives', items=alternatives, parent='expert_window',
                    tracked=True, width=1310, num_items=count_alternatives)
    estimates.resize([count_experts, count_alternatives, count_alternatives])
    with dpg.child_window(tag='experts_window', parent='expert_window', autosize_y=True, no_scrollbar=True):
        for expert in range(count_experts):
            with dpg.child_window(tag=f'evaluation{expert}', autosize_x=True, show=False):
                with dpg.group(horizontal=True):
                    if expert > 0:
                        dpg.add_button(arrow=True, direction=dpg.mvDir_Left,
                                       callback=go_back, user_data=expert)
                    dpg.add_text(default_value=f"Роль эксперта #{expert + 1}: ")
                    dpg.add_input_text(tag=f'role{expert}', default_value='Аноним', width=1100 - bool(expert) * 40)
                # табличка с альтернативами
                with dpg.table(tag=f'table{expert}',
                               header_row=True, row_background=True,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=True, scrollX=True, height=410):
                    dpg.add_table_column(label=' ', width_fixed=True, width=200)
                    for row in range(0, count_alternatives):
                        dpg.add_table_column(label=f'Альтернатива #{row + 1}', width_fixed=True, width=200)
                    for row in range(0, count_alternatives):
                        with dpg.table_row():
                            dpg.add_text(default_value=f'Альтернатива #{row + 1}')
                            for col in range(0, count_alternatives):
                                default_value = 0
                                if col > row:
                                    default_value = 1
                                if col == row:
                                    dpg.add_input_int(tag=f'mark{expert}{row}{col}',
                                                      default_value=1, readonly=True, width=200)
                                else:
                                    dpg.add_input_int(tag=f'mark{expert}{row}{col}', default_value=default_value,
                                                      min_value=0, max_value=1,
                                                      min_clamped=True, max_clamped=True,
                                                      callback=check_mark, user_data=[expert, col, row], width=200)
                # Переход к другому эксперту
                if expert + 1 != count_experts:
                    dpg.add_button(label=f"Перейти к эксперту #{expert + 2}",
                                   callback=switch_expert, user_data=[expert, count_alternatives, count_experts])
                else:  # Выход к результатам
                    dpg.add_button(label="Вычислить наилучшую альтернативу",
                                   callback=switch_expert, user_data=[expert, count_alternatives, count_experts])
    dpg.configure_item('evaluation0', show=True)
    dpg.configure_item('expert_window', show=True)


with dpg.window(label="Expert", tag="expert_window", show=False, width=WIDTH, height=HEIGHT-150,
                no_move=True, no_resize=True, no_scrollbar=True):
    with dpg.group(horizontal=True):
        dpg.add_text(default_value="ЦЕЛЬ: ", tag='label_target')
        dpg.add_input_text(tag='output_target', readonly=True, width=1220)

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (77, 7, 143), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvInputInt):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 77, 70), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvText):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (15, 61, 131), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

with dpg.font_registry():
    with dpg.font(f'/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', 20, default_font=True, id="Default font"):
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
dpg.bind_font("Default font")

dpg.bind_theme(global_theme)
########################################################################################################################
dpg.create_viewport(title='ГРУППОВОЕ ПАРНОЕ ОЦЕНИВАНИЕ', width=1920, height=920)
dpg.set_global_font_scale(1.25)
dpg.set_exit_callback(on_exit)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Main", True)
dpg.start_dearpygui()
dpg.destroy_context()
