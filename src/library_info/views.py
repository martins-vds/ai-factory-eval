from django.shortcuts import render


def about_legacy(request):
    return render(request, 'library_info/legacy.html', content_type='text/html')


def about_page(request):
    return render(request, 'library_info/about.html')
