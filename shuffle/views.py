import json
import codecs

from django.http import HttpResponse
from django.shortcuts import render
from datetime import timedelta, date
from shuffle.shuffle_logic import get_slots_full, format_result


def shuffle(request):
    days = request.POST.get('days')
    mode = request.POST.get('mode')
    file = request.FILES.get('file-upload')

    res = ''

    if all([days, mode, file, mode == 'full']):
        groups = {'BOTH': []}
        for day in json.loads(days)['week']:
            d = day[list(day.keys())[0]]
            if d['count'] > 0:
                for count in range(d['count']):
                    today = date.today()
                    if today.weekday() >= d['weekday']: d['weekday'] += 7
                    groups['BOTH'].append((today + timedelta(d['weekday'] - today.weekday())).strftime("%d/%m/%Y"))

        res = format_result(get_slots_full(groups, codecs.iterdecode(file, 'utf-8')))

    #elif all([days, mode, file, mode == 'groups']):

    if res:
        response = HttpResponse(res, content_type='application/text charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="result.txt"'

        return response

    return render(request, 'shuffle/shuffle.html')
