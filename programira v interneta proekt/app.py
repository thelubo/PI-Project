import re
from functools import wraps
from datetime import datetime

import flask_login
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from flask_login import current_user, logout_user, login_user, login_required

from flask_toastr import Toastr

import dicts
import table

extra_error = None

app = Flask(__name__)
toastr = Toastr(app)

app.secret_key = "super secret string"  # Change this! No, I won't change it

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = psycopg2.connect(database="postgres",
                        host="localhost",
                        user="postgres",
                        password="134679258",
                        port="5432")
cur = conn.cursor()

# ERRORS
######################################


@app.errorhandler(410)
def custom_error_1(error):
    flash('Невалидна Стая!', 'error')
    return redirect('/')


@app.errorhandler(411)
def custom_error_2(error):
    if extra_error == '':
        flash('Заета зала!', 'error')
    else:
        flash('Заета зала! ' + 'Седмица ' + str(extra_error))
    return redirect('/entry')


@app.errorhandler(415)
def custom_error_6(error):
    flash('Непопълненa седмица!', 'error')
    return redirect('/entry')


@app.errorhandler(416)
def custom_error_7(error):
    flash('Невалидна седмица!', 'error')
    return redirect('/entry')


@app.errorhandler(417)
def custom_error_8(error):
    flash('Непопълнено поле!', 'error')
    return redirect('/entry')


@app.errorhandler(412)
def custom_error_3(error):
    flash('Непопълнено поле!', 'error')
    return redirect('/')


@app.errorhandler(413)
def custom_error_4(error):
    flash('Невалиден час!', 'error')
    return redirect('/')


@app.errorhandler(414)
def custom_error_5(error):
    flash('Непопълнено поле, или дата извън учебната година!', 'error')
    return redirect('/')

# IMPORTED CRAP
######################################


def search_db(room_number, time, date=None, week=None, date_offset=None):
    if week is None or week == '':
        # print('week in none 1')
        week = get_week(date)

    # print('week')
    # print(week)

    ###############################
    sql = ("SELECT start_time, end_time, day_of_week,"
           " rooms.room_number, specializations.name_specialization, "
           "class_groups.number_group, subjects.name_subject, subject_type.type_subject, "
           "lecturers.name_person, all_week_data.id,"
           " week, entry_by_user "
           " FROM all_week_data ")

    sql = sql + "JOIN rooms ON rooms.id = room_id "
    sql = sql + "JOIN specializations ON specializations.id = specialization_id "
    sql = sql + "JOIN class_groups ON class_groups.id = group_id "
    sql = sql + "JOIN subjects ON subjects.id = subject_id "
    sql = sql + "JOIN subject_type ON subject_type.id = subject_type_id "
    sql = sql + "JOIN lecturers ON lecturers.id = lecturer_id "

    sql = sql + "WHERE room_number='%s' " % room_number

    sql = sql + "AND week='%s' " % week

    if date_offset is None:
        date_offset = get_date_offset(str(date), week)
        sql = sql + "AND day_of_week='%s' " % date_offset[0]
    else:
        sql = sql + "AND day_of_week='%s' " % date_offset

    # this is fucked, I hate python
    if time != ":":
        sql = sql + "AND '%s' BETWEEN start_time AND end_time " % time

    sql = sql + "ORDER BY start_time"

    print('search sql here')
    print(sql)
    cur.execute(sql)
    results = cur.fetchall()

    full_result = []
    for result in results:
        # print(result)
        full_result.append(result)

    print('full_result')
    print(full_result)

    return full_result


def get_week(date):
    sql_week = "SELECT id FROM week_periods WHERE '%s' BETWEEN date_start AND date_end" % date
    print('sql week')
    print(sql_week)
    cur.execute(sql_week)
    results = cur.fetchone()
    table_get_table = results[0]

    return table_get_table


def get_date_offset(date2, week=None):
    if week == '' or week is None:
        week = get_week(date2)
        # print('week is none')

    sql_date = "SELECT date_start FROM week_periods WHERE id = '%s'" % week
    print('sql date')
    print(sql_date)
    cur.execute(sql_date)
    results = cur.fetchone()

    try:
        result_date_object = datetime.strptime(str(results[0]), '%Y-%m-%d')
        # print(result_date_object)

        date_object = datetime.strptime(date2, '%Y-%m-%d')
        # print(date_object)

        date_offset = abs(result_date_object - date_object).days
        # print(date_offset)
    except ValueError:
        date_offset = 0

    return date_offset, week


######################################
# dupes
######################################

def dupechecker(room_number, time_start, time_end, formatted_week, day_of_week, prevent_date=None, long_message=False):
    time_start_cycle, time_end_cycle = time_start, time_end
    time_start_cycle = datetime.strptime(time_start_cycle, "%H:%M")
    time_end_cycle = datetime.strptime(time_end_cycle, "%H:%M")
    time_end_compare = datetime.strptime(time_end, "%H:%M")
    while time_start_cycle < time_end_compare:
        dupe_checker = search_db(room_number, time_start_cycle.strftime("%H:%M"), prevent_date,
                                 formatted_week, day_of_week)
        time_start_cycle, time_end_cycle = table.do_time(time_start_cycle, time_end_cycle)
        global extra_error
        extra_error = ''
        if len(dupe_checker) != 0:
            if long_message:
                extra_error = str(formatted_week)
                abort(411)
            else:
                abort(411)


def dupechecker2(room_number, formatted_week, day_of_week, check_time=False, time=None):
    space_found = False
    time_start_cycle, time_end_cycle = '07:30', '08:30'

    if check_time:
        time_start_cycle = time_end_cycle = time

    time_start_cycle = datetime.strptime(time_start_cycle, "%H:%M")
    time_end_cycle = datetime.strptime(time_end_cycle, "%H:%M")
    time_end_compare = datetime.strptime('19:30', "%H:%M")

    while True:
        dupe_checker = search_db(room_number, time_start_cycle.strftime("%H:%M"), None,
                                 formatted_week, str(day_of_week))
        time_start_cycle, time_end_cycle = table.do_time(time_start_cycle, time_end_cycle)
        if len(dupe_checker) == 0:
            space_found = True
            break
        if time_start_cycle < time_end_compare:
            break

    return space_found


######################################
# LOGIN STUFF START
######################################


class User(flask_login.UserMixin):
    def __init__(self, id_user, user_name, password_, is_admin):
        self.id = id_user
        self.name = user_name
        self.password = password_
        self.is_admin = is_admin


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_admin:
            return f(*args, **kwargs)
        else:
            logout_user()
            return redirect(url_for('login_1'))

    return wrap


@login_manager.user_loader
def user_loader(id_user):
    sql_login_loader = "SELECT * FROM users WHERE id='%s'" % id_user
    cur.execute(sql_login_loader)
    user = cur.fetchone()
    if user is None:
        return None
    # print(user[0], user[1], user[2], user[3])
    return User(user[0], user[1], user[2], user[3])


@app.get("/login")
def login_1():
    return render_template("login.html")


@app.post("/login")
def login_2():
    user = request.form.get("username")
    password = request.form.get("password")

    # print(user)
    # print(password)

    sql_login2 = "SELECT * FROM users WHERE user_name='%s' AND password_='%s'" % (user, password)
    cur.execute(sql_login2)
    user = cur.fetchone()
    if user is None:
        return render_template("login.html", error=1)
    user = user[0]
    user_object = user_loader(user)

    if user_object is not None:
        # print("login triggered")
        # print(login_user(user_object))
        login_user(user_object)

    return redirect(url_for("search_string"))


@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('search_string'))


# LOGIN STUFF END
########################################

@app.route('/help')
def help_page():
    return render_template("help.html")


@app.route('/', methods=['POST', 'GET'])
def search_string():
    date_today = datetime.now()
    session['date_p3'] = str(date_today.year)
    login_state = current_user.is_authenticated
    if login_state:
        user_privilege = current_user.is_admin
    else:
        user_privilege = False

    if request.method == 'POST':
        if request.form.get('search_button') == 'Search' or request.form.get('room_button') is not None:
            if request.form.get('search_button') == 'Search':
                room_number = session['room_number'] = request.form.get("room_number")
                print(room_number)

                date_p1 = session['date_p1'] = request.form.get("date_month")
                date_p2 = session['date_p2'] = request.form.get("date_day")
                date_p3 = session['date_p3'] = request.form.get("date_year")

                date = session['date'] = date_p3 + "-" + date_p1 + "-" + date_p2
                print(date)

                time1 = session['time1'] = request.form.get("time_hour")
                time2 = session['time2'] = request.form.get("time_minute")
                time = session['time'] = time1 + ":" + time2
                print(time)

                week = session['week'] = request.form.get('week')
                day_of_week = session['day_of_week'] = request.form.get("day_of_week")

                throw_error = True

                if re.fullmatch('\\d\\d\\d\\d', session['room_number']):
                    throw_error = False
                if session['room_number'] == 'салон':
                    throw_error = False
                if session['room_number'] == 'аула':
                    throw_error = False
                if session['room_number'] == '':
                    throw_error = False

                if throw_error:
                    abort(410)
            else:
                room_number = session['room_number'] = request.form.get("room_button")  # str(4425)

                date_p1 = session['date_p1']
                date_p2 = session['date_p2']
                date_p3 = session['date_p3']
                date = session['date'] = date_p3 + "-" + date_p1 + "-" + date_p2

                time1 = session['time1']
                time2 = session['time2']
                time = session['time'] = time1 + ":" + time2

                week = session['week']
                day_of_week = session['day_of_week']

            print('week and day of week')
            print(week)
            print(day_of_week)
            if week == '' or day_of_week == '':
                day_of_week = week = None

            only_exclusive = request.form.get("only_exclusive")

            # For empty rooms slot
            if room_number == '':

                print('timetester')
                print(time1)
                print(time2)
                if (time1 == '') ^ (time2 == ''):
                    abort(413)
                    # abort(400, 'Невалиден час!')

                print('reached room part')

                # if date_p1 != '' and date_p2 != '' or week != '' and day_of_week != '':
                #     conn.rollback()
                #     abort(400, 'Непопълнено поле, или дата извън учебната година!')

                sql_find_rooms = "SELECT room_number FROM rooms ORDER BY room_number"
                cur.execute(sql_find_rooms)
                results = cur.fetchall()
                result = results[0]

                time_for_dupechecker = None
                pass_in_time_dupechecker = False
                if time != ':':
                    time_for_dupechecker = time
                    pass_in_time_dupechecker = True

                if week is None:
                    try:
                        week = get_week(date)
                        day_of_week = get_date_offset(date, week)[0]
                        conn.rollback()
                    except (psycopg2.errors.InvalidDatetimeFormat, TypeError):
                        conn.rollback()
                        abort(414)

                try:
                    dupechecker2(result, week, day_of_week, pass_in_time_dupechecker, time_for_dupechecker)
                except (psycopg2.errors.InvalidDatetimeFormat, psycopg2.errors.DatetimeFieldOverflow):
                    conn.rollback()
                    abort(414)
                    # abort(400, 'Непопълнено поле, или дата извън учебната година!')

                full_result_rooms = []
                for result in results:
                    # print(result)
                    if dupechecker2(result, week, day_of_week, pass_in_time_dupechecker, time_for_dupechecker):
                        full_result_rooms.append(result)
                # print('room results')
                # print(full_result_rooms)

                # abort(400, 'BLACK')

                return render_template('results_rooms_only.html', incoming_table=table.make_table_2(full_result_rooms))

            else:
                try:
                    full_result = search_db(room_number, time, date, week, day_of_week)
                except (psycopg2.Error, UnboundLocalError, TypeError):
                    conn.rollback()
                    abort(414)

            if time == ':':
                time = 'Цял ден'
            elif len(full_result) != 0:
                only_exclusive = 'only_taken'

            day_name = get_date_offset(date, week)
            session["default_table"] = day_name[1]

            if len(date_p1) == 0 or len(date_p2) == 0:
                date_or_week = 'Седмица %s' % week
                day_top = dicts.offset_to_days[int(day_of_week)]
            else:
                date_or_week = date
                day_top = dicts.offset_to_days[day_name[0]]

            try:
                query_info = ('Стая ' + room_number + '<br>' + date_or_week + ', ' + time + '<br>' +
                              day_top)
            except UnboundLocalError:
                abort(414)
                # abort(400, 'Непопълнено поле, или дата извън учебната година!')

            if login_state:
                user_name = current_user.name
            else:
                user_name = None

            return render_template('results.html', query_info=query_info,
                                   incoming_table=table.make_table(full_result, login_state, user_privilege,
                                                                   only_exclusive, user_name))

        if request.form.get('Reserve_button') is not None and 0 <= int(request.form.get('Reserve_button')) <= 11:
            if not login_state:
                abort(401)
            button_index = session['button_index'] = int(request.form.get('Reserve_button'))
            # print('button index' + str(button_index))
            return redirect(url_for("entry"))

        if request.form.get('Remove_button') is not None and 0 <= int(request.form.get('Remove_button')) <= 11:
            if not login_state:
                abort(401)
            # if not user_privilege:
            #     abort(401)
            button_index = int(request.form.get('Remove_button'))

            time1, time2 = table.do_time(do_times=button_index)

            try:
                to_remove = search_db(session['room_number'], time1, session['date'])
                # sql_table = (get_week(session['date']))
            except psycopg2.errors.InvalidDatetimeFormat:
                conn.rollback()
                to_remove = search_db(session['room_number'], time1, session['date'],
                                      session['week'], session['day_of_week'])
                # sql_table = session['week']

            sql_remove = """DELETE FROM all_week_data WHERE all_week_data.id=%s """ % to_remove[0][9]
            cur.execute(sql_remove)
            conn.commit()

            print('REMOVE REACHED')
            session['coming_from_entry'] = 1
            session['action_type'] = 'Премахване'

            return redirect(url_for("search_string"))

    def_year = session['date_p3']

    try:
        def_room = session['room_number']
        def_time1 = session['time1']
        def_time2 = session['time2']
    except KeyError:
        def_room = def_time1 = def_time2 = ''

    try:
        def_day = session['date_p2']
        def_month = session['date_p1']
    except KeyError:
        def_day = def_month = ''

    try:
        day_label = ''
        def_week = session['week']
        def_day_of_week = session['day_of_week']
        if def_day_of_week != 'None':
            day_label = dicts.offset_to_days[int(def_day_of_week)]
        if def_week == '':
            day_label = ''
    except (KeyError, UnboundLocalError, ValueError):
        def_week = def_day_of_week = day_label = ''

    try:
        month_label = dicts.int_to_months[int(session['date_p1'])]
    except (ValueError, KeyError):
        month_label = ''

    try:
        coming_from_entry = session['coming_from_entry']
        action_type = session['action_type']
        session.pop('coming_from_entry')
        session.pop('action_type')
    except KeyError:
        coming_from_entry = action_type = ''

    if current_user.is_authenticated:
        login_state = 1
        admin = 0
        username = current_user.name
        if current_user.is_admin:
            admin = 1
    else:
        login_state = 0
        admin = 0
        username = ''

    return render_template('main.html', coming_from_entry=coming_from_entry, action_type=action_type,
                           default_year_main=def_year, default_room_main=def_room, default_day_main=def_day,
                           default_month_main=def_month, default_hour_main=def_time1, default_minute_main=def_time2,
                           login_state=login_state, admin_state=admin, username=username, default_week_main=def_week,
                           default_day_of_week_main_label=day_label,
                           default_day_of_week_main=def_day_of_week, default_month_main_label=month_label)


@app.route('/entry', methods=['POST', 'GET'])
@login_required
def entry():
    date1 = session['date_p1']
    date2 = session['date_p2']
    date3 = session['date_p3']
    room_number = session['room_number']

    button_index = session['button_index']

    time1, time2 = table.do_time(do_times=button_index)
    formatted_time1 = time1.strftime("%H:%M")
    formatted_time2 = time2.strftime("%H:%M")
    formatted_week = session["week"]
    if formatted_week == '':
        formatted_week = get_week(session['date'])

    default_day_of_week_entry = session['day_of_week']
    if default_day_of_week_entry != '':
        default_day_of_week_entry_label = dicts.offset_to_days[int(default_day_of_week_entry)]
    else:
        date = datetime.strptime(session['date'], '%Y-%m-%d')
        default_day_of_week_entry_label = dicts.offset_to_days[date.weekday()]

    if request.method == 'POST':
        if request.form.get('reserve_button_final') == 'Reserve':
            # date1 = request.form.get("date_day_reserve")
            # date2 = request.form.get("date_month_reserve")
            # date3 = request.form.get("date_year_reserve")

            time_start = request.form.get("time_start_reserve")
            time_end = session['time_end_e'] = request.form.get("time_end_reserve")

            day_of_week = session['day_of_week'] = request.form.get("day_of_week_entry")

            room_number = request.form.get("room_number_reserve")
            room_key = inserter('rooms', 'room_number', room_number)

            spec = session['spec_e'] = request.form.get("specialization_reserve")
            spec_key = inserter('specializations', 'name_specialization', spec)

            group = session['group_e'] = request.form.get("group_reserve")
            group_key = inserter('class_groups', 'number_group', group)

            subj = session['subj_e'] = request.form.get("subject_reserve")
            subj_key = inserter('subjects', 'name_subject', subj)

            type_r = session['type_r_e'] = request.form.get("type_reserve")
            if type_r is None or type_r == '':
                type_r = 'Л'
            type_r_key = inserter('subject_type', 'type_subject', type_r)

            name_r = session['name_r_e'] = request.form.get("name_reserve")

            if len(name_r) == 0:
                name_r = session['name_r_e'] = '-'
            name_r_key = inserter('lecturers', 'name_person', name_r)

            week_function = request.form.get("multi_week")
            print(week_function)

            try:
                week_start = int(request.form.get("week_start"))
            except ValueError:
                week_start = get_week(session["date"])

            week_end = int(request.form.get("week_end"))
            print('weekcrap')
            print(session['date'])

            # prevent empty strings date1, date2, date3,
            if '' in {time_start, time_end, room_number, spec, group, subj, type_r, name_r}:
                abort(417)
                # abort(400, 'Непопълнено поле!')

            # prevent time travel
            time_mismatch1 = datetime.strptime(time_start, '%H:%M')
            time_mismatch2 = datetime.strptime(time_end, '%H:%M')
            if time_mismatch1 > time_mismatch2:
                abort(413)
                # abort(400, 'Невалиден час!')

            # prevent duplicates
            prevent_date = date3 + "-" + date1 + "-" + date2
            if day_of_week == '':
                date = datetime.strptime(session['date'], '%Y-%m-%d')
                day_of_week = date.weekday()

            if week_function == 'False':
                print('dupechecker called')
                dupechecker(room_number, time_start, time_end, formatted_week, day_of_week, prevent_date)
                # time_start_cycle, time_end_cycle = time_start, time_end
                # time_start_cycle = datetime.strptime(time_start_cycle, "%H:%M")
                # time_end_cycle = datetime.strptime(time_end_cycle, "%H:%M")
                # time_end_compare = datetime.strptime(time_end, "%H:%M")
                # while time_start_cycle < time_end_compare:
                #     dupe_checker = search_db(room_number, time_start_cycle.strftime("%H:%M"), prevent_date,
                #                              formatted_week)
                #     time_start_cycle, time_end_cycle = table.do_time(time_start_cycle, time_end_cycle)
                #     if len(dupe_checker) != 0:
                #         abort(400, 'Заета зала!')

            insert_count = 0
            week_start_increment = 1
            print('session week')
            print(session['week'])
            week_number = session['week']

            if week_function == 'multi_week_all' or week_function == 'multi_week_specific':

                counter = week_start

                if '' in {week_start, week_end}:
                    abort(415)
                    # abort(400, 'Непопълненa седмица!')
                if week_start > week_end and week_function == 'multi_week_specific':
                    abort(416)
                    # abort(400, 'Невалидна седмица!')
                if week_end > 13:
                    week_end = 13
                if week_function == 'multi_week_all':
                    # if not no_date_input:
                    #     week_start = get_table(prevent_date)
                    # else:
                    week_start = session['week']
                    week_end = 13

                # all_dupes = []
                # dupe_found = False
                while counter <= week_end:
                    print('dupechecker called for multiweek')
                    dupechecker(room_number, time_start, time_end, counter, day_of_week, None, True)
                    # week_dupe = "week%s" % counter
                    # dupe_checker = search_db(room_number, time_start, None, week_dupe, day_of_week)
                    # if len(dupe_checker) != 0:
                    #     dupe_found = True
                    #     all_dupes.append(week_dupe)
                    counter += 1
                # if dupe_found:
                #     print(all_dupes)
                #     for i in range(len(all_dupes)):
                #         all_dupes[i] = (all_dupes[i])[4:]
                #     abort(400, 'Заета зала! ' + 'Седмица ' + (str(all_dupes)[1:-1]).strip('\''))

                insert_count = int(week_end) - int(week_start)
                week_number = session['week']
                week_start_increment = int(week_start)

                print('insert count, week_number, increment')
                print(insert_count)
                print(week_function)
                print(week_start_increment)

            if current_user.is_authenticated:
                user_for_table = current_user.name
            else:
                user_for_table = None

            if week_number == '':
                week_number = get_week(session['date'])

            while insert_count >= 0:
                sql_reserve = ("""INSERT INTO all_week_data VALUES 
                (DEFAULT, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" %
                               (spec_key, group_key, room_key, time_start, time_end,
                                subj_key, type_r_key, name_r_key, day_of_week, week_number,
                                user_for_table))
                cur.execute(sql_reserve)
                conn.commit()
                print('COMMIT REACHED')
                insert_count -= 1
                print(insert_count)
                week_start_increment += 1
                print(week_start_increment)
                week_number = week_start_increment
                print(week_number)

            session['coming_from_entry'] = 1
            session['action_type'] = 'Заемане'
            return redirect(url_for("search_string"))

    default_week_end = min(int(formatted_week) + 1, 13)

    try:
        if session['time_end_e'] is None:
            pass
    except KeyError:
        session['time_end_e'] = ''
    try:
        if session['spec_e'] is None:
            pass
    except KeyError:
        session['spec_e'] = ''
    try:
        if session['group_e'] is None:
            pass
    except KeyError:
        session['group_e'] = ''
    try:
        if session['subj_e'] is None:
            pass
    except KeyError:
        session['subj_e'] = ''
    try:
        if session['type_r_e'] is None:
            pass
    except KeyError:
        session['type_r_e'] = ''
    try:
        if session['name_r_e'] is None:
            pass
    except KeyError:
        session['name_r_e'] = ''

    return render_template('entry.html', default_room=room_number, default_time1=formatted_time1,
                           default_time2=session['time_end_e'], default_week_start=formatted_week,
                           default_day_of_week_entry=default_day_of_week_entry,
                           default_day_of_week_entry_label=default_day_of_week_entry_label,
                           default_week_end=default_week_end,
                           default_spec_e=session['spec_e'], default_group_e=session['group_e'],
                           default_subj_e=session['subj_e'], default_type_r_e=session['type_r_e'],
                           default_name_r_e=session['name_r_e'])


def inserter(table_name, col_name, value):
    sql_return = "SELECT * FROM %s WHERE %s='%s'" % (table_name, col_name, value)
    cur.execute(sql_return)
    result = cur.fetchone()

    if result is None:
        sql_return_2 = """INSERT INTO %s VALUES (DEFAULT, '%s')""" % (table_name, value)
        cur.execute(sql_return_2)
        conn.commit()
        cur.execute(sql_return)
        result = cur.fetchone()

    key_for_main = result[0]
    return key_for_main


if __name__ == '__main__':
    app.run(debug=True)
