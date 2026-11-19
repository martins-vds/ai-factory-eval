from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def about(request):
    return render(request, 'library_info/about.html', content_type='text/html')


@require_GET
def about_page(request):
    return render(request, 'library_info/page.html')
