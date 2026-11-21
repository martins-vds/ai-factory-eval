from django.shortcuts import render


def about_page(request):
    return render(
        request,
        'library_info/about-legacy.html',
        content_type='text/html',
    )


def about_ui_page(request):
    return render(request, 'library_info/about.html')
