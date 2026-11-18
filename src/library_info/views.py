from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

LEGACY_ABOUT_HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>About the Lending Library</title></head>
<body>
  <h1>About the Lending Library</h1>
  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>
  <p>Contact: desk@lending-library.invalid</p>
</body>
</html>
"""


@require_GET
def legacy_about(request):
    return HttpResponse(LEGACY_ABOUT_HTML, content_type='text/html')


@require_GET
def about_page(request):
    return render(request, 'library_info/about.html')
