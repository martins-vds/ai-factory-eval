from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET


@require_GET
def public_about(request):
    return HttpResponse(
        render_to_string('library_info/public_about.html'),
        content_type='text/html',
    )
