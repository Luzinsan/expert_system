from settings import *

estimates = np.array([1, 1, 1])


# region ####################################################--CONSISTENCY--##################################################
def get_eigenvector(table_expert: np.ndarray):
    # Вычисление собственного вектора (придлиженный метод - геометрическое среднее)
    norm_table = np.array([[0.5 if item == 0 else 2
                            for item in table_expert[row]]
                           for row in range(table_expert.shape[0])], dtype=np.float64)
    eigenvector = np.array([ pow(np.prod(norm_table[row]), 1/norm_table.shape[0])
                            for row in range(norm_table.shape[0])], dtype=np.float64)
    return eigenvector, norm_table


def get_norm_eigenvector(eigenvector: np.ndarray):
    return np.array([item / sum(eigenvector) for item in eigenvector], dtype=np.float64)


def get_max_eigenvalue(eigenvector: np.ndarray, norm_table: np.ndarray[[]]):
    return np.sum([np.sum(norm_table[:, column]) * eigenvector[column]
                   for column in range(norm_table.shape[1])])


with dpg.colormap_registry(tag='consistency'):
    dpg.add_colormap(0.5, qualitative=True)


def check_consistency(expert, table_expert: np.ndarray[[]]):
    eigenvector, norm_table = get_eigenvector(table_expert)
    norm_eigenvector = get_norm_eigenvector(eigenvector)
    max_eigenvalue = get_max_eigenvalue(norm_eigenvector, norm_table)
    amount = norm_table.shape[0]
    consistency_index = (max_eigenvalue - amount) / (amount - 1)
    print(consistency_index)
    random_matrix_consistency = [0.00000001, 0.00000001, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
    consistency_relation = consistency_index / random_matrix_consistency[amount - 1]
    print(consistency_relation)
    dpg.set_value(f'consistency{expert}', 0.1 / np.sum(eigenvector))
    dpg.delete_item(f'text_consistency{expert}')
    dpg.add_text(tag=f'text_consistency{expert}', default_value='Согласованность матрицы',
                 color=[0, 255, 0], before=f'consistency{expert}')
    # return consistency_relation > 0.1
    return True
# endregion


# region ####################################################--SWITCHing--#######################################################
def go_back(sender, app_data, expert):
    dpg.configure_item(f'evaluation{expert}', show=False)
    dpg.configure_item(f'evaluation{expert - 1}', show=True)


def switch_expert(sender, app_data, expert_data):
    # expert_data = [number_of_expert, count_of_alternatives, count_of_experts]
    global estimates
    dpg.delete_item('error_expert')
    expert, count_of_alternatives, count_of_experts = expert_data
    estimates[expert] = [[dpg.get_value(f'mark{expert}{i}{j}')
                          for j in range(count_of_alternatives)]
                         for i in range(count_of_alternatives)]
    if check_consistency(expert, estimates[expert]):
        dpg.configure_item(f'evaluation{expert}', show=False)
        if expert + 1 != count_of_experts:
            dpg.configure_item(f'evaluation{expert + 1}', show=True)
        else:
            preparation_for_ranking([count_of_experts, count_of_alternatives])
    else:
        dpg.add_text(default_value='Матрица не согласована. Проверьте данные.',
                     parent=f'evaluation{expert}', tag='error_expert', color='red')


def check_mark(sender, checked_mark, reflected_mark):
    if checked_mark == dpg.get_value(f'mark{reflected_mark[0]}{reflected_mark[1]}{reflected_mark[2]}'):
        dpg.set_value(f'mark{reflected_mark[0]}{reflected_mark[1]}{reflected_mark[2]}', not checked_mark)


# endregion


# region ###################################################--Expert Window--####################################################
with dpg.window(label="Expert", tag="expert_window", show=False, width=WIDTH, height=HEIGHT - 150,
                no_move=True, no_resize=True, no_scrollbar=True):
    with dpg.group(horizontal=True):
        dpg.add_text(default_value="ЦЕЛЬ: ", tag='label_target')
        dpg.add_input_text(tag='output_target', readonly=True, width=1220)
# endregion


# region ###################################################--ranging--##########################################################
def ranging(count_alternatives, calc_marks) -> np.ndarray:
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
    return calc_marks


def add_ranging_table(count_alternatives, common_matrix) -> np.ndarray:
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
        calc_marks = ranging(count_alternatives, calc_marks)
        [dpg.set_value(f'common_range{i}', calc_marks[i]) for i in range(count_alternatives)]
        return calc_marks


def preparation_for_ranking(count_experts_alters):
    global estimates
    dpg.delete_item('list_alternatives')
    count_expert, count_alternatives = count_experts_alters
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
        calc_marks = add_ranging_table(count_alternatives, common_matrix)
        with dpg.group(horizontal=True):
            dpg.add_text(default_value="Наилучшая альтернатива: ")
            dpg.add_input_text(default_value=dpg.get_value(f'alter_text{np.argmin(calc_marks)}'),
                               readonly=True, multiline=True)
# endregion


# region ##################################################--Experts--###########################################################
def add_alters_table(expert, count_alternatives):
    # табличка с альтернативами
    with dpg.table(tag=f'table{expert}', parent=f'evaluation{expert}',
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


def add_expert(expert, count_alternatives, count_experts):
    with dpg.child_window(tag=f'evaluation{expert}', autosize_x=True, show=False, parent='experts_window'):
        with dpg.group(horizontal=True):
            if expert > 0:
                dpg.add_button(arrow=True, direction=dpg.mvDir_Left,
                               callback=go_back, user_data=expert)
            dpg.add_text(default_value=f"Роль эксперта #{expert + 1}: ")
            dpg.add_input_text(tag=f'role{expert}', default_value='Аноним', width=1100 - bool(expert) * 40)
        with dpg.group(horizontal=True):
            dpg.add_text(default_value="Согласованность матрицы: ", tag=f'text_consistency{expert}')
            dpg.add_input_text(tag=f'consistency{expert}', width=998, readonly=True)
        add_alters_table(expert, count_alternatives)
        # Переход к другому эксперту
        if expert + 1 != count_experts:
            dpg.add_button(label=f"Перейти к эксперту #{expert + 2}",
                           callback=switch_expert, user_data=[expert, count_alternatives, count_experts])
        else:  # Выход к результатам
            dpg.add_button(label="Вычислить наилучшую альтернативу",
                           callback=switch_expert, user_data=[expert, count_alternatives, count_experts])


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
            add_expert(expert, count_alternatives, count_experts)
    dpg.configure_item('evaluation0', show=True)
    dpg.configure_item('expert_window', show=True)
# endregion


# region ######################################################Main Window########################################################
def add_alternative(sender, new_count_alter):
    global count_alter
    if new_count_alter > count_alter:
        dpg.add_input_text(tag=f'alter_text{new_count_alter - 1}', multiline=True,
                           default_value=f'Альтернатива решения #{new_count_alter}',
                           height=50, parent='alternatives_window', width=1850)
    else:
        dpg.delete_item(f'alter_text{count_alter - 1}')
    count_alter = new_count_alter


offset = '\t\t\t'
with dpg.window(label="Main", tag="Main", width=WIDTH, height=HEIGHT):
    with dpg.child_window(height=200):
        dpg.add_text(wrap=WIDTH - 50, default_value=f'''\tДанная программа предназначена для оценивания альтернатив на основе метода группового парного сравнения (с системой оценок 1/0).
                                Инструкция: 
{offset}1) Введите цель, достижение которой поможет вашей команде решить выявленную проблему в организации;
{offset}2) Выберите количество экспертов, 
которые будут участвовать в оценивании введённых альтернатив достижения цели (в пределах от 1 до 8 включительно);
{offset}3) Добавьте альтернативы, которые будут сравниваться между собой (в пределах от 2 до 10 включительно);
{offset}4) Как только будут определены: цель, количество экспертов, альтернативы
- то после нажатия кнопки <Продолжить> необходимо поочередно каждому из экспертов сравнить введённые альтернативы
(выведенные в пронумерованном виде)
- с помощью меню сверху будет возможность свернуть панель эксперта и поменять количество экспертов или альтернатив.
Чтобы применить изменения, нажмите кнопку <Продолжить> и раскройте только что закрытую панель с экспертами
(оценка будет производиться с самого первого эксперта)
{offset}5) Заполнение таблицы (система оценок 1/0). Правила:
- Если альтернатива в соответствующей строке лучше или эквивалентна альтернативе в соответствующем столбце,
{offset}{offset}      то значение равно __1__
- В противном случае значение равно __0__
            Механика:
- По диагонали неизменно стоят единицы, так как сравнивается одна и та же альтернатива
- При изменении оценки сравнения по строке i и столбцу j, 
автоматически меняется оценка сравнения по строке j и столбцу i (зеркальный элемент)
- Программой предусмотрено вычисление индекса согласованности матрицы. 
Чтобы матрица была согласованной, необходимо выполнение условие:
--> если один элемент лучше другого, а тот, в свою очередь, лучше третьего, то первый также должен быть лучше третьего.
{offset}6) Далее производится вычисление и вывод связных рангов альтернатив, 
где чем меньше значение, тем более предпочтительнее альтернатива,
а эквивалентные альтернативы принимают среднее математическое ожидание на основе рангов.
В процессе вычисления, заполняется обобщённая матрица с помощью метода нахождения медианы (половина или большинство голосов)
{offset}7) Выводится наилучшая альтернатива, которая имеет наименьшее значение ранга.
''')
        dpg.add_separator()
        dpg.add_text(wrap=WIDTH,
                     default_value=f'{offset}{offset}{offset}{offset}{offset}{offset}{offset}{offset}{offset}{offset}{offset}{offset}Разработано студенткой 3-го курса гр. 430-2: Лузинсан А.А.')

    with dpg.group(horizontal=True):
        dpg.add_text(default_value='Введите рассматриваемую цель: ')
        dpg.add_input_text(tag='target', hint='цель для решения проблемы', width=1495)
    with dpg.group(horizontal=True):
        dpg.add_text(default_value='Введите количество экспертов: ')
        dpg.add_input_int(tag='experts', default_value=3, min_value=1, min_clamped=True, width=223)
    with dpg.group(horizontal=True):
        dpg.add_text(default_value='Введите количество альтернатив: ')
        dpg.add_input_int(tag='alternatives', default_value=count_alter,
                          min_value=2, min_clamped=True, max_value=10, max_clamped=True,
                          width=200, callback=add_alternative)
    with dpg.child_window(tag='alternatives_window', height=558):
        dpg.add_input_text(tag='alter_text0', multiline=True,
                           default_value='Альтернатива решения #1',
                           height=50, width=1850)
        dpg.add_input_text(tag='alter_text1', multiline=True,
                           default_value='Альтернатива решения #2',
                           height=50, width=1850)
    dpg.add_button(label="Продолжить", width=150, callback=experts)
dpg.set_primary_window("Main", True)
# endregion


########################################################################################################################
dpg.create_viewport(title='ГРУППОВОЕ ПАРНОЕ ОЦЕНИВАНИЕ', width=1920, height=920)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
