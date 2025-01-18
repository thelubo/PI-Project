import html
import os
from datetime import datetime, timedelta

from prettytable import PrettyTable

do_increment = False
i = 0
index = 0
g_full_result = []


def make_table(full_result, login_state, user_privilege, only_exclusive=False, user_name=None):

    global i

    is_empty = False
    if len(full_result) == 0:
        is_empty = True

    only_free = only_taken = False
    # print('only_exclusive is:')
    # print(only_exclusive)
    if only_exclusive is not False:
        # print('enter if')
        if only_exclusive == 'only_free':
            only_free = True
            # print('free state set')
        if only_exclusive == 'only_taken':
            only_taken = True
            # print('free state set 2')

    global g_full_result
    g_full_result = full_result

    g = '<span class="span_green">'
    r = '<span class="span_red">'
    close = '</span>'

    power = 0
    if login_state and not user_privilege:
        power = 1
    if login_state and user_privilege:
        power = 2

    print('LOGIN DATA')
    print(login_state)
    print(user_privilege)
    print(power)

    table = PrettyTable()
    if power == 2:
        table.field_names = ["Начало", "Край", "Състояние", "Специалност", "Група", "Предмет", "Вид",
                             "Преподавател", "", " "]
    elif power == 1:
        table.field_names = ["Начало", "Край", "Състояние", "Специалност", "Група", "Предмет", "Вид", "Преподавател",
                             "", " "]
    else:
        table.field_names = ["Начало", "Край", "Състояние", "Специалност", "Група", "Предмет", "Вид", "Преподавател"]

    global index

    start_time = datetime.strptime("07:30", "%H:%M")
    end_time = datetime.strptime("08:15", "%H:%M")

    while True:
        formatted_time_start = start_time.strftime("%H:%M")
        formatted_time_end = end_time.strftime("%H:%M")

        if power == 0:
            if not is_empty and time_compare(formatted_time_start, formatted_time_end, full_result[i][0],
                                             full_result[i][1]):
                if not only_free:
                    table.add_row([formatted_time_start, formatted_time_end, r + "Заета" + close, full_result[i][4],
                                   full_result[i][5], full_result[i][6], full_result[i][7], full_result[i][8]])
            else:
                if not only_taken:
                    table.add_row([formatted_time_start, formatted_time_end, g + "Свободна" + close,
                                   "-", "-", "-", "-", "-"])

        if power == 1:
            if not is_empty and time_compare(formatted_time_start, formatted_time_end, full_result[i][0],
                                             full_result[i][1]):
                if not only_free:
                    print('test for free')
                    print(user_name)
                    print(full_result[i][11])
                    if user_name == full_result[i][11]:
                        table.add_row([formatted_time_start, formatted_time_end, r + "Заета" + close, full_result[i][4],
                                       full_result[i][5], full_result[i][6], full_result[i][7], full_result[i][8], "",
                                       make_button(index, 2)])
                    else:
                        table.add_row([formatted_time_start, formatted_time_end, r + "Заета" + close, full_result[i][4],
                                       full_result[i][5], full_result[i][6], full_result[i][7], full_result[i][8], "",
                                       ""])
            else:
                if not only_taken:
                    table.add_row([formatted_time_start, formatted_time_end, g + "Свободна" + close,
                                   "-", "-", "-", "-", "-",
                                   make_button(index, 1), ""])

        if power == 2:
            if not is_empty and time_compare(formatted_time_start, formatted_time_end, full_result[i][0],
                                             full_result[i][1]):
                if not only_free:
                    table.add_row([formatted_time_start, formatted_time_end, r + "Заета" + close, full_result[i][4],
                                   full_result[i][5], full_result[i][6], full_result[i][7], full_result[i][8], "",
                                   make_button(index, 2)])
            else:
                if not only_taken:
                    table.add_row([formatted_time_start, formatted_time_end, g + "Свободна" + close,
                                   "-", "-", "-", "-", "-", make_button(index, 1), ""])

        start_time, end_time = do_time(start_time, end_time)

        if end_time > datetime.strptime("19:30", "%H:%M"):
            index = 0
            break

        index += 1

    html_string = table.get_html_string(padding_width=10)
    html_string = html.unescape(html_string)

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # f = open(dir_path + "\\temporary\\table.html", "w", encoding='utf-8')
    # f.write(html_string)
    # f.close()

    i = 0

    return html_string


def do_time(start_time=datetime.strptime("07:30", "%H:%M"), end_time=datetime.strptime("08:15", "%H:%M"), do_times=1):
    while do_times != 0:
        period = timedelta(hours=1)
        start_time += period
        end_time += period
        # print('start_time')
        # print(start_time)
        # print('end_time')
        # print(end_time)

        if start_time == datetime.strptime("13:30", "%H:%M"):
            extra_minutes = timedelta(minutes=15)
            start_time += extra_minutes
            end_time += extra_minutes

        do_times -= 1

    return start_time, end_time


def time_compare(start_table, end_table, start, end):
    global i
    global do_increment

    if do_increment:
        i += 1
        # print("incrementing i")
        # print(i)
        do_increment = False
        start = g_full_result[i][0]
        end = g_full_result[i][1]

    start = start.strftime("%H:%M")
    end = end.strftime("%H:%M")

    start = datetime.strptime(start, "%H:%M").time()
    end = datetime.strptime(end, "%H:%M").time()
    start_table = datetime.strptime(start_table, "%H:%M").time()
    end_table = datetime.strptime(end_table, "%H:%M").time()

    # print(start, end, start_table, end_table)

    # A.end >= B.start AND A.start <= B.end
    # print('end')
    # print(end)
    # print('start_table')
    # print(start_table)
    # print('start')
    # print(start)
    # print('end_table')
    # print(end_table)

    if end >= start_table and start <= end_table:
        if end_table == end and i < (len(g_full_result) - 1):
            do_increment = True
        # print("True")
        return True

    # print("False")
    return False


def make_button(id_button, type_button):
    if type_button == 2:
        type_button_inner = "Remove"
        type_button_inner2 = "Премахване"
    else:
        type_button_inner = "Reserve"
        type_button_inner2 = "Заемане"

    button = '<button type="submit" name="%s_button" value="%s">%s</button>' % (type_button_inner,
                                                                                id_button, type_button_inner2)
    return button


def make_better_button(room_number=None):
    if room_number is None:
        return ''

    button = '<button type="submit" name="room_button" value="%s">%s</button>' % (room_number, room_number)
    return button


def make_table_2(full_result_rooms):
    c = 0
    table = PrettyTable()
    print(len(full_result_rooms))
    row_list = []
    while c < len(full_result_rooms):
        row_list.append(make_better_button(full_result_rooms[c][0]))
        # print(row_list)
        c += 1
        # print(c)
        if c % 7 == 0:
            # print('row_list')
            # print(row_list)
            table.add_rows([row_list])
            row_list = []

    while len(row_list) < 7:
        row_list.append('')

    # print('row_list2')
    # print(row_list)
    table.add_rows([row_list])

    html_string = table.get_html_string(padding_width=10, header=False)
    html_string = html.unescape(html_string)

    return html_string
