from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET


@require_GET
def legacy_about(request):
    return TemplateResponse(
        request,
        'library_info/legacy_about.html',
        content_type='text/html',
    )


@require_GET
def about_page(request):
    return render(request, 'library_info/about.html')
