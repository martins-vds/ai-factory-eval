from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

_ABOUT_HTML = (
    '<!doctype html>\n'
    '<html lang="en">\n'
    '<head><meta charset="utf-8"><title>About the Lending Library</title></head>\n'
    '<body>\n'
    '  <h1>About the Lending Library</h1>\n'
    '  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>\n'
    '  <p>Contact: desk@lending-library.invalid</p>\n'
    '</body>\n'
    '</html>\n'
)


@require_GET
def about(request):
    return HttpResponse(_ABOUT_HTML, content_type='text/html')


@require_GET
def about_page(request):
    return render(request, 'library_info/about.html')
