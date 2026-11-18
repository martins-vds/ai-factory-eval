from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string


def about(request):
    body = render_to_string('library_info/legacy_about.html', request=request)
    return HttpResponse(body, content_type='text/html')


def about_page(request):
    return render(request, 'library_info/about.html')
