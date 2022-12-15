import dearpygui.dearpygui as dpg
import numpy as np
from remapping import *



def on_exit(sender, app_data, user_data):
    print("closed")


estimates = np.array([1, 1, 1])


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


def ranging(user_data):
    global estimates
    count_expert, count_alternatives = user_data
    common_matrix = np.empty((count_alternatives, count_alternatives), dtype=np.bool_)
    for i in range(0, count_alternatives):
        for j in range(0, count_alternatives):
            sum_marks = 0
            for expert in range(count_expert):
                sum_marks += estimates[expert][i][j]
            common_matrix[i][j] = True if sum_marks > count_expert / 2 else False
    with dpg.child_window(tag=f'range_window', parent='expert_window', height=720, width=1920):
        for expert in range(count_expert):
            with dpg.group(horizontal=True, tag=f"group_expert{expert}"):
                dpg.add_text(default_value=f"Эксперт #{expert + 1}: ")
                dpg.add_input_text(default_value=dpg.get_value(f'role{expert}'), readonly=True)
        # проранжированные альтернативы
        with dpg.table(tag=f'range_table',
                       row_background=True,
                       resizable=True, policy=dpg.mvTable_SizingStretchProp,
                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                       borders_outerV=True, width=800):
            dpg.add_table_column(label='Альтернативы', tag=f'alter_col')
            dpg.add_table_column(label='Ранг', tag=f'marks_col', width=20)
            calc_marks = np.empty(count_alternatives, dtype=np.int64)
            for i in range(0, count_alternatives):
                with dpg.table_row():
                    dpg.add_text(default_value=dpg.get_value(f'alter_text{i}'), tag=f'alter_row{i}')
                    calc_marks[i] = count_alternatives - sum(common_matrix[i]) + 1
                    dpg.add_text(tag=f'common_range{i}', default_value=calc_marks[i])
        with dpg.group(horizontal=True):
            dpg.add_text(default_value="Наилучшая альтернатива: ")
            dpg.add_input_text(default_value=dpg.get_value(f'alter_text{np.argmin(calc_marks)}'), readonly=True, width=600)


def check_mark(sender, checked_mark, reflected_mark):
    if checked_mark == dpg.get_value(f'mark{reflected_mark[0]}{reflected_mark[1]}{reflected_mark[2]}'):
        dpg.set_value(f'mark{reflected_mark[0]}{reflected_mark[1]}{reflected_mark[2]}', not checked_mark)


def experts():
    dpg.delete_item('expert_window', children_only=True)
    dpg.configure_item('expert_window', show=True)
    with dpg.group(horizontal=True, tag="group_target_const", parent='expert_window'):
        dpg.add_text(default_value=f"ЦЕЛЬ: ")
        dpg.add_input_text(readonly=True, default_value=dpg.get_value('target'), width=1900)
    count_experts = dpg.get_value('experts')
    count_alternatives = dpg.get_value('alternatives')
    alternatives = []
    for expert in range(count_alternatives):
        alternatives.append(dpg.get_value(f'alter_text{expert}'))

    dpg.add_listbox(tag='list_alternatives', items=alternatives, parent='expert_window',
                    tracked=True, width=1920, num_items=count_alternatives)
    estimates.resize([count_experts, count_alternatives, count_alternatives])
    for expert in range(count_experts):
        with dpg.child_window(tag=f'evaluation{expert}', parent='expert_window', height=720, width=1920, show=False):
            with dpg.group(horizontal=True, tag=f"group_role{expert}"):
                dpg.add_text(default_value=f"Роль эксперта #{expert + 1}: ")
                dpg.add_input_text(tag=f'role{expert}', default_value='Аноним')
            # табличка с альтернативами
            with dpg.table(tag=f'table{expert}',
                           header_row=True, row_background=True,
                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                           borders_outerV=True, width=900):
                dpg.add_table_column(label=' ', tag=f'col{expert}')
                for row in range(0, count_alternatives):
                    dpg.add_table_column(label=f'Альтернатива #{row + 1}', tag=f'col{expert}{row}')
                for row in range(0, count_alternatives):
                    with dpg.table_row():
                        dpg.add_text(default_value=f'Альтернатива #{row + 1}', tag=f'row{expert}{row}')
                        for col in range(0, count_alternatives):
                            default_value = 0
                            if col > row:
                                default_value = 1
                            if col == row:
                                dpg.add_input_int(tag=f'mark{expert}{row}{col}', default_value=1, readonly=True, width=120)
                            else:
                                dpg.add_input_int(tag=f'mark{expert}{row}{col}', default_value=default_value,
                                                  min_value=0, max_value=1,
                                                  min_clamped=True, max_clamped=True,
                                                  callback=check_mark, user_data=[expert, col, row],
                                                  width=120)
            # Переход к другому эксперту
            if expert + 1 != count_experts:
                dpg.add_button(label=f"Перейти к эксперту #{expert + 2}", tag=f'next{expert + 1}',
                               callback=switch_expert, user_data=[expert, count_alternatives, count_experts])
            else:  # Выход к результатам
                dpg.add_button(label="Вычислить наилучшую альтернативу", tag='finish',
                               callback=switch_expert, user_data=[expert, count_alternatives, count_experts])
    dpg.configure_item('evaluation0', show=True)


def add_alternatives():
    dpg.delete_item('alternatives_window', children_only=True)
    for i in range(dpg.get_value('alternatives')):
        dpg.add_input_text(tag=f'alter_text{i}', multiline=True,
                           default_value=f'Альтернатива решения #{i + 1}',
                           height=50, parent='alternatives_window')


with dpg.window(label="Expert", tag="expert_window", autosize=True, show=False, modal=True, width=900):
    dpg.add_separator()

with dpg.window(label="Main", tag="Main", autosize=True):
    with dpg.group(horizontal=True, tag="group_target"):
        dpg.add_text(default_value='Введите рассматриваемую цель: ')
        dpg.add_input_text(label=" ", tag='target', default_value='У самурая нет цели, есть только путь')
    with dpg.group(horizontal=True, tag="group_experts"):
        dpg.add_text(default_value='Выберите количество экспертов: ')
        dpg.add_input_int(label=" ", tag='experts', default_value=3, min_value=1, min_clamped=True)
    with dpg.group(horizontal=True, tag="group_alternatives"):
        dpg.add_text(default_value='Выберите количество альтернатив: ')
        dpg.add_input_int(label=" ", tag='alternatives', default_value=5, min_value=1, min_clamped=True)
    dpg.add_button(label="Ввести альтернативы", width=300, callback=add_alternatives)
    dpg.add_child_window(tag='alternatives_window', height=300)
    dpg.add_button(label="Продолжить", tag='expert_button', width=150, callback=experts)

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


dpg.bind_theme(global_theme)
########################################################################################################################
dpg.create_viewport(title='Expert System', width=1200, height=700)
dpg.set_global_font_scale(1)
dpg.set_exit_callback(on_exit)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Main", True)
dpg.start_dearpygui()
dpg.destroy_context()