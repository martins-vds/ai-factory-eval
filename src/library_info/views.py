from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string


def about_page(request):
    return HttpResponse(
        render_to_string('library_info/legacy_about.html'),
        content_type='text/html',
    )


def about_ui(request):
    return render(request, 'library_info/about.html')
