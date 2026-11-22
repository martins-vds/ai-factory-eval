from django.http import HttpResponse
from django.shortcuts import render

OPENING_HOURS = 'Open Monday to Saturday, 9:00 to 18:00.'
LENDING_PERIOD = 'Books are lent for 14 days.'
CONTACT_ADDRESS = 'desk@lending-library.invalid'

ABOUT_PAGE = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>About the Lending Library</title></head>
<body>
  <h1>About the Lending Library</h1>
  <p>{OPENING_HOURS} {LENDING_PERIOD}</p>
  <p>Contact: {CONTACT_ADDRESS}</p>
</body>
</html>
"""


def about_page(request):
    return HttpResponse(ABOUT_PAGE, content_type='text/html')


def about_ui(request):
    return render(
        request,
        'library_info/about.html',
        {
            'opening_hours': OPENING_HOURS,
            'lending_period': LENDING_PERIOD,
            'contact_address': CONTACT_ADDRESS,
        },
    )
