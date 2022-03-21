from django.shortcuts import redirect


def redirect_view(request):
    response = redirect('/shuffle/')

    return response
