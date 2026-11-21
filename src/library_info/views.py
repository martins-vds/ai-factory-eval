from django.shortcuts import render


def about_page(request):
    return render(request, 'library_info/legacy_about.html')


def about_browser_page(request):
    return render(request, 'library_info/about.html')
