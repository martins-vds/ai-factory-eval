from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def about_endpoint(request):
    response = render(request, 'library_info/legacy.html')
    response['Content-Type'] = 'text/html'
    return response


@require_GET
def about_page(request):
    return render(request, 'library_info/about.html')
