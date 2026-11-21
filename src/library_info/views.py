from django.shortcuts import render


def legacy_about(request):
    return render(request, 'library_info/about-legacy.html', content_type='text/html')


def about(request):
    return render(request, 'library_info/about.html')
