from django.shortcuts import render


def about(request):
    return render(request, 'library_info/about_legacy.html')


def about_page(request):
    return render(request, 'library_info/about.html')
