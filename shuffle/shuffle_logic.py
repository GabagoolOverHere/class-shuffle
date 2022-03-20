import csv
from datetime import datetime, timedelta, date
from itertools import islice
import random
from jours_feries_france import JoursFeries
from vacances_scolaires_france import SchoolHolidayDates


def dispatch_slots(groups: dict, count_full: int = 0, count_a: int = 0, count_b : int = 0) -> dict:
    """
    use get_available_slots() depending of the configuration (2 groups, or full classroom)
    :param groups: A and B of the BOTH for the full classroom
    :param count: the number of students
    :return: dict[group]: [dates available according to holidays]
    """
    if len(groups) == 1 and groups.get('FULL'):
        days = groups.get('FULL')
        groups['FULL'] = get_available_slots(days, count_full)
    elif all([len(groups) == 2, groups.get('A'), groups.get('B')]):
        groups['A'] = get_available_slots(groups['A'], count_a)
        groups['B'] = get_available_slots(groups['B'], count_b)

    return groups


def get_available_slots(slot_list: list, count) -> list:
    """
    get the possible day, considering holidays
    :param slot_list: the days of the week available
    :param count: the number of students
    :return: dict[group]: [dates available according to holidays]
    """
    d, f = SchoolHolidayDates(), JoursFeries()
    week = timedelta(days=7)
    slots = [[datetime.strptime(x, '%d/%m/%Y').date(), slot_list.count(x), []] for x in set(slot_list)]

    for slot in slots:
        if sum([x[1] for x in slots]) >= count: break
        for i in range(1, 8):
            new_date = slot[0] + week * i
            if not (d.is_holiday_for_zone(new_date, 'B') or f.is_bank_holiday(new_date, zone='Métropole')):
                slots.append([new_date, slot[1], []])
                break

    return slots


def get_students_list(*files, mode: str) -> dict:
    """
    extract the students in the csv file, shuffle them, and return them in a dict
    :param file: the csv file
    :param mode: full, or groups
    :return: dict contaning a shuffled list of students
    """
    if mode == 'BOTH':
        d = {'FULL': []}
        for file in files:
            students = []
            doc = csv.reader(file, delimiter=';')
            # islice allow slicing on iterators
            for row in islice(doc, 1, None):
                students.append(' '.join(x.strip('"') for x in row[0].split() if not x.isupper()))

            random.shuffle(students)
            d['FULL'].extend(students)

        return d

    elif mode == 'GROUPS':
        d = {'A': [], 'B': []}
        for file in files:
            students = []
            doc = csv.reader(file[1], delimiter=';')
            # islice allow slicing on iterators
            for row in islice(doc, 1, None):
                students.append(' '.join(x.strip('"') for x in row[0].split() if not x.isupper()))

            random.shuffle(students)
            d[file[0]].extend(students)

        return d


def students_to_spots(groups: dict, slots: dict):
    """
    assign students to a slot depending on group config, holidays...
    :param groups: full classroom or 2 groups
    :param slots: the slots available
    :return: d[group]: [date, number of slot, [students assigned]]
    """
    for group, students in groups.items():
        for student in students:
            for slot in slots[group]:
                if len(slot[2]) < slot[1]:
                    slot[2].append(student)
                    break
    final_res = []
    if len(slots) > 1:
        for a in slots['A']:
            for b in slots['B']:
                if a[0] == b[0]:
                    a[1] += b[1]
                    a[2].extend(b[2])
                    slots['B'].remove(b)
        final_res.extend(slots['A'])
        final_res.extend(slots['B'])
    else:
        final_res = slots['FULL']

    return sorted(final_res, key=lambda r: r[0])


def format_result(res):
    """
    format the end result to be written in a text file
    :param res: the end result
    :return: a formatted string
    """
    formatted = []
    for r in res:
        names = [r[2][0]]
        if len(r[2]) > 1:
            names.extend([f' and {n}' for n in r[2][1:]])
        formatted.append(f'{r[0].strftime("%d/%m/%Y")}: {"".join(names)}\n')

    return ''.join(formatted)


def get_slots_full(groups, file):
    """
    handle all the functions so I have to call just this one to have a result
    """
    student_dict = get_students_list(file, mode='BOTH')
    slots = dispatch_slots(groups, count_full=len(student_dict['FULL']))

    return students_to_spots(student_dict, slots)


def get_slots_groups(*files, groups):
    student_dict = get_students_list(('A', files[0]), ('B', files[1]), mode='GROUPS')
    slots = dispatch_slots(groups, count_a=len(student_dict['A']), count_b=len(student_dict['B']))

    return students_to_spots(student_dict, slots)


def format_post_request(schedule: dict, mode: str):
    """
    format the request received in the post request to be compatible with all the logic
    :param schedule: a dict of days selected
    :param mode: full class or two groups
    :return: a dict adapted to the other function in the module
    """
    groups = {}
    if mode == 'BOTH':
        groups = {'FULL': []}
    elif mode == 'GROUPS':
        groups = {'A': [], 'B': []}

    for group in schedule:
        for day in schedule[group]:
            d = day[list(day.keys())[0]]
            if d['count'] > 0:
                for count in range(d['count']):
                    today = date.today()
                    if today.weekday() >= d['weekday']: d['weekday'] += 7
                    groups[group].append((today + timedelta(d['weekday'] - today.weekday())).strftime("%d/%m/%Y"))

    return groups
