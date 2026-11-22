from django.shortcuts import render


def about(request):
    response = render(request, 'library_info/legacy_about.html')
    response['Content-Type'] = 'text/html'
    return response


def about_page(request):
    return render(request, 'library_info/about.html')
