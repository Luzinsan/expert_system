from gauss_expert import *

WIDTH = 960
HEIGHT = 540
CENTER = int(WIDTH / 2) - 100

dpg.create_context()

ge = GaussExpert()
print(ge.gauss_parametrs)

# region WINDOW#1: Simple Decision Support System
with dpg.window(label="Simple Decision Support System", tag="Main"):
    # Справочная информация
    dpg.add_child_window(tag='info', height=380)
    # Ввод альтернатив
    with dpg.group(horizontal=True):
        dpg.add_text(default_value='Количество альтернатив: ')
        dpg.add_input_int(tag='alts', default_value=2, min_value=2, min_clamped=True)
    # Ввод критериев
    with dpg.group(horizontal=True):
        with dpg.group(horizontal=False):
            dpg.add_text(default_value='Название критерия #1: ')
            dpg.add_text(default_value='Название критерия #2: ')
        with dpg.group(horizontal=False):
            dpg.add_input_text(tag='crit1', default_value='Критерий #1')
            dpg.add_input_text(tag='crit2', default_value='Критерий #2')
    dpg.add_button(label='Подтвердить', indent=CENTER,
                   callback=lambda: dpg.configure_item('gauss_param', show=True))


# endregion

# region WINDOW#2: Gauss Parameters (with check)
def switch_crit(sender, app_data, crit):
    if check_inputs(crit):
        if crit == 0:
            dpg.delete_item(f'child{crit}')
            dpg.configure_item(f'child{crit + 1}', show=True)
        else:
            dpg.delete_item('gauss_param')
            dpg.configure_item('window_alter', show=True)
            window_alter(ge.alts)


def check_inputs(crit):
    itsok = True
    if dpg.get_value(f'a1_crit{crit}') >= dpg.get_value(f'a2_crit{crit}'):
        dpg.configure_item(f'a2_crit{crit}_except', show=True)
        dpg.set_value(f'a2_crit{crit}_except', 'Значение Ay2 должно быть больше значения Ay1')
        itsok = False
    if dpg.get_value(f'a2_crit{crit}') >= dpg.get_value(f'a3_crit{crit}'):
        dpg.configure_item(f'a3_crit{crit}_except', show=True)
        dpg.set_value(f'a3_crit{crit}_except', 'Значение должно быть больше Ay1 и Ay2')
        itsok = False
    if dpg.get_value(f'j1_crit{crit}') <= dpg.get_value(f'a1_crit{crit}') \
            or dpg.get_value(f'j1_crit{crit}') >= dpg.get_value(f'a2_crit{crit}'):
        dpg.configure_item(f'j1_crit{crit}_except', show=True)
        dpg.set_value(f'j1_crit{crit}_except', 'Значение должно быть между Ay1 и Ay2')
        itsok = False
    if dpg.get_value(f'j2_crit{crit}') <= dpg.get_value(f'a2_crit{crit}') \
            or dpg.get_value(f'j2_crit{crit}') >= dpg.get_value(f'a3_crit{crit}'):
        dpg.configure_item(f'j2_crit{crit}_except', show=True)
        dpg.set_value(f'j2_crit{crit}_except', 'Значение должно быть между Ay2 и Ay3')
        itsok = False
    if itsok:
        for i in range(2):
            ge.gauss_parametrs[crit]['dominant_value'][i] = dpg.get_value(f'a{i + 1}_crit{crit}')
            ge.gauss_parametrs[crit]['bound_neighb'][i] = dpg.get_value(f'j{i + 1}_crit{crit}')
            ge.gauss_parametrs[crit]['membership_deg'][i] = dpg.get_value(f'M{i + 1}_crit{crit}')
        ge.gauss_parametrs[crit]['dominant_value'][2] = dpg.get_value(f'a3_crit{crit}')
        ge.crits = 2
        ge.alts = dpg.get_value('alts')
    return itsok


# region WINDOW#2: Gauss Parameters
with dpg.window(label="Gauss Parameters", tag="gauss_param", width=WIDTH, height=HEIGHT,
                show=False, no_move=True, no_resize=True, modal=True):
    for i in range(2):
        with dpg.child_window(tag=f'child{i}', show=False):
            dpg.add_text(default_value=f'Параметры функции Гаусса для критерия #{i + 1}', indent=CENTER - 120)
            dpg.add_separator()
            # Ввод доминирующих значений
            dpg.add_text(default_value='Доминирующее значение Y нечёткого множества, описывающего терм, ai')
            with dpg.group(horizontal=False):
                for j in range(3):
                    with dpg.group(horizontal=True):
                        dpg.add_text(default_value=f'Ay{j + 1}: ')
                        dpg.add_input_double(tag=f'a{j + 1}_crit{i}', default_value=0, width=150)
                        dpg.add_input_text(tag=f'a{j + 1}_crit{i}_except', show=False)

            dpg.add_separator()
            # Ввод пограничных значений
            dpg.add_text(default_value='Пограничные значения соседних термов, j')
            with dpg.group(horizontal=False):
                for j in range(2):
                    with dpg.group(horizontal=True):
                        dpg.add_text(default_value=f'j{j + 1}: ')
                        dpg.add_input_double(tag=f'j{j + 1}_crit{i}', default_value=0, width=150)
                        dpg.add_input_text(tag=f'j{j + 1}_crit{i}_except', show=False)
            dpg.add_separator()
            # Ввод степени разделения
            dpg.add_text(default_value='Степень принадлежности пограничных значений(степень разделения), М')
            with dpg.group(horizontal=False):
                for j in range(2):
                    with dpg.group(horizontal=True):
                        dpg.add_text(default_value=f'M{j + 1}: ')
                        dpg.add_input_double(tag=f'M{j + 1}_crit{i}', default_value=0, width=150,
                                             min_value=0.0, min_clamped=True, max_value=1.0, max_clamped=True)
                        dpg.add_input_text(tag=f'M{j + 1}_crit{i}_except', show=False)
            dpg.add_button(label='Подтвердить', indent=CENTER,
                           callback=switch_crit, user_data=i)
        dpg.configure_item('child0', show=True)


# endregion
# endregion


# region WINDOW#3: Input Alternatives
def switch_grade():
    if check_crit():
        ge.grades = [[dpg.get_value(f'alt{alter}_crit{crit + 1}')
                     for alter in range(ge.alts)]
                     for crit in range(ge.crits)]
        ge.calculateParams()
        ge.getBestAlternative()
        dpg.configure_item('window_alter', show=False)
        dpg.configure_item('window_gauss_grade', show=True)
        window_gauss_grade(ge.alts)
    else:
        dpg.configure_item('window_exc', show=True)


def check_crit():
    succ = True
    for alter in range(ge.alts):
        for crit in range(ge.crits):
            if dpg.get_value(f'alt{alter}_crit{crit + 1}') < ge.gauss_parametrs[crit]['dominant_value'][0] \
                    or dpg.get_value(f'alt{alter}_crit{crit + 1}') > ge.gauss_parametrs[crit]['dominant_value'][2]:
                print("ERROR")
                dpg.add_text(default_value=f'Error: значение альтернативы {alter + 1} критерия {crit + 1} неверно',
                             parent='window_exc')
                succ = False
    return succ


with dpg.window(label='Предупреждение', tag="window_exc", width=WIDTH, height=HEIGHT,
                show=False, no_move=True, no_resize=True):
    pass

with dpg.window(label="Input Alternatives", tag="window_alter", width=WIDTH, height=HEIGHT,
                show=False, no_move=True, no_resize=True):
    # Ввод альтернатив
    dpg.add_table(tag='table_alts',
                  resizable=True, policy=dpg.mvTable_SizingStretchProp,
                  row_background=True, header_row=False,
                  borders_innerH=True, borders_outerH=True, borders_innerV=True,
                  borders_outerV=True)
    dpg.add_button(label='Продолжить', indent=CENTER, callback=switch_grade)


def window_alter(amount_alts):
    print(ge.gauss_parametrs)
    dpg.add_table_column(parent='table_alts')
    dpg.add_table_column(parent='table_alts')
    for i in range(amount_alts):
        with dpg.table_row(parent='table_alts'):
            dpg.add_text(default_value=f'Альтернатива #{i + 1}')
            dpg.add_input_text(tag=f'alt{i}_text', hint=f'Ввод альтернативы #{i + 1}')
        with dpg.table_row(parent='table_alts'):
            dpg.add_text(default_value=dpg.get_value('crit1'))
            dpg.add_input_float(tag=f'alt{i}_crit1')
        with dpg.table_row(parent='table_alts'):
            dpg.add_text(default_value=dpg.get_value('crit2'))
            dpg.add_input_float(tag=f'alt{i}_crit2')


# endregion


# region WINDOW#4: Gauss Criteria Grade
def window_gauss_grade(amount_alts):
    for crit in range(ge.crits):
        dpg.add_text(label=dpg.get_value(f'crit{crit + 1}'), before=f'table_membership_crit{crit + 1}')
        dpg.add_table_column(label='Альтернатива', parent=f'table_membership_crit{crit + 1}')
        dpg.add_table_column(label='Низкий', parent=f'table_membership_crit{crit + 1}')
        dpg.add_table_column(label='Средний', parent=f'table_membership_crit{crit + 1}')
        dpg.add_table_column(label='Высокий', parent=f'table_membership_crit{crit + 1}')
        for alter in range(amount_alts):
            with dpg.table_row(parent=f'table_membership_crit{crit + 1}'):
                dpg.add_text(default_value=dpg.get_value(f'alt{alter}_text'))
                dpg.add_text(default_value=ge.fuzzy_grades[crit][alter][0])
                dpg.add_text(default_value=ge.fuzzy_grades[crit][alter][1])
                dpg.add_text(default_value=ge.fuzzy_grades[crit][alter][2])


def output_res():
    dpg.configure_item('window_result', show=True)
    dpg.add_table_column(label='Альтернатива', parent='table_result')
    dpg.add_table_column(label='Эффективность', parent='table_result')
    for alter in range(ge.alts):
        with dpg.table_row(parent='table_result'):
            dpg.add_text(default_value=dpg.get_value(f'alt{alter}_text'))
            dpg.add_text(default_value=ge.alts_eff[alter])
    dpg.set_value('output_res', dpg.get_value(f'alt{ge.best_alt[1]}_text'))


with dpg.window(label="Gauss Criteria Grade", tag="window_gauss_grade", width=WIDTH, height=HEIGHT,
                show=False, no_move=True, no_resize=True, popup=True):
    # Таблицы оценок по критериям
    for crit in range(ge.crits):
        dpg.add_table(tag=f'table_membership_crit{crit + 1}',
                      resizable=True, policy=dpg.mvTable_SizingStretchProp,
                      row_background=True,
                      borders_innerH=True, borders_outerH=True, borders_innerV=True,
                      borders_outerV=True)
        dpg.add_separator()

    dpg.add_button(label='Продолжить', indent=CENTER, callback=output_res)
# endregion

# region WINDOW#5:
with dpg.window(label='Results', tag="window_result", width=WIDTH, height=HEIGHT,
                show=False, no_move=True, no_resize=True):
    dpg.add_table(tag='table_result',
                  resizable=True, policy=dpg.mvTable_SizingStretchProp,
                  row_background=True,
                  borders_innerH=True, borders_outerH=True, borders_innerV=True,
                  borders_outerV=True)
    dpg.add_text(default_value='Наилучшая альтернатива: ')
    dpg.add_input_text(tag='output_res', readonly=True)
    pass


# endregion

# region other
def on_exit(sender, app_data, user_data):
    print("closed")


# Оформление
with dpg.theme() as global_theme:
    # with dpg.theme_component(dpg.mvAll):
    #     dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (5, 7, 143), category=dpg.mvThemeCat_Core)
    #     dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvInputInt):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 77, 180), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 177, 180), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvText):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (15, 161, 131), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
dpg.bind_theme(global_theme)

with dpg.font_registry():
    # with dpg.font('C:\Windows\Fonts\CALIBRIL.TTF', 16, default_font=True, id="Default font"):
    #     dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    with dpg.font('FreeSerifBold.ttf', 16, default_font=True, id="Default font"):
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
dpg.bind_font("Default font")


########################################################################################################################
dpg.create_viewport(title='НЕЧЁТКОЕ МНОГОКРИТЕРИАЛЬНОЕ ОЦЕНИВАНИЕ МЕТОДОМ ГАУССА', width=WIDTH, height=HEIGHT,
                    resizable=False)
dpg.set_global_font_scale(1)
dpg.set_exit_callback(on_exit)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Main", True)
dpg.start_dearpygui()
dpg.destroy_context()
# endregion
