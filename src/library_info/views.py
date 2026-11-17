from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def about_endpoint(request):
    return render(request, 'library_info/legacy_about.html')


@require_GET
def about_page(request):
    return render(request, 'library_info/about.html')
