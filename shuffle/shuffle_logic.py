import csv
from datetime import datetime, timedelta
from itertools import islice
import random
from jours_feries_france import JoursFeries
from vacances_scolaires_france import SchoolHolidayDates


def dispatch_slots(groups: dict, count: int) -> dict:
    """
    use get_available_slots() depending of the configuration (2 groups, or full classroom)
    :param groups: A and B of the BOTH for the full classroom
    :param count: the number of students
    :return: dict[group]: [dates available according to holidays]
    """
    if len(groups) == 1 and groups.get('BOTH'):
        days = groups.get('BOTH')
        groups['BOTH'] = get_available_slots(days, count)
    elif all([len(groups) == 2, groups.get('A'), groups.get('B')]):
        groups['A'] = get_available_slots(groups['A'], 6)
        groups['B'] = get_available_slots(groups['B'], 7)

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


def get_students_list(file, mode: str) -> dict:
    """
    extract the students in the csv file, shuffle them, and return them in a dict
    :param file: the csv file
    :param mode: full, or groups
    :return: dict contaning a shuffled list of students
    """
    d = {'BOTH': []} if mode == 'full' else {'A': [], 'B': []}
    students = []
    doc = csv.reader(file, delimiter=';')
    # islice allow slicing on iterators
    for row in islice(doc, 1, None):
        students.append(' '.join(x.strip('"') for x in row[0].split() if not x.isupper()))

    random.shuffle(students)
    d['BOTH'].extend(students)

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
    if len(groups) > 1:
        for a in slots['A']:
            for b in slots['B']:
                if a[0] == b[0]:
                    a[1] += b[1]
                    a[2].extend(b[2])
                    final_res.append(a)
    else:
        final_res = slots['BOTH']

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
    student_dict = get_students_list(file, 'full')
    slots = dispatch_slots(groups, len(student_dict['BOTH']))

    return students_to_spots(student_dict, slots)
