from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def about_page(request):
    return render(request, 'library_info/static_about.html', content_type='text/html')


@require_GET
def about_ui(request):
    return render(request, 'library_info/about.html')
