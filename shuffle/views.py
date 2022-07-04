import json
import codecs

from django.http import HttpResponse
from django.shortcuts import render
from shuffle.shuffle_logic import get_slots_full, get_slots_groups, format_result, format_post_request


def shuffle(request):
    days = request.POST.get('days')
    mode = request.POST.get('mode')

    full = request.FILES.get('full-file-upload')
    a_group = request.FILES.get('a-file-upload')
    b_group = request.FILES.get('b-file-upload')

    if all([days, mode, full, mode == 'BOTH']):
        schedule = json.loads(days)['BOTH']
        groups = format_post_request(schedule, mode)

        res = format_result(get_slots_full(groups, codecs.iterdecode(full, 'utf-8')))

        response = HttpResponse(res, content_type='application/text charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="result.txt"'

        return response

    elif all([days, mode, a_group, b_group, mode == 'GROUPS']):
        schedule = json.loads(days)['GROUPS']
        groups = format_post_request(schedule, mode)

        res = format_result(
            get_slots_groups(
                codecs.iterdecode(a_group, 'utf-8'), codecs.iterdecode(b_group, 'utf-8'), groups=groups
            )
        )

        response = HttpResponse(res, content_type='application/text charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="result.txt"'

        return response

    return render(request, 'shuffle/shuffle.html')
