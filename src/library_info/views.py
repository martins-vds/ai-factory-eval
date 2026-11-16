from django.http import HttpResponse
from django.shortcuts import render

ABOUT_INFORMATION = {
    'title': 'About the Lending Library',
    'opening_hours': 'Open Monday to Saturday, 9:00 to 18:00.',
    'lending_policy': 'Books are lent for 14 days.',
    'contact_email': 'desk@lending-library.invalid',
}

ABOUT_RESPONSE = (
    '<!doctype html>\n'
    '<html lang="en">\n'
    f'<head><meta charset="utf-8"><title>{ABOUT_INFORMATION["title"]}</title></head>\n'
    '<body>\n'
    f'  <h1>{ABOUT_INFORMATION["title"]}</h1>\n'
    f'  <p>{ABOUT_INFORMATION["opening_hours"]} {ABOUT_INFORMATION["lending_policy"]}</p>\n'
    f'  <p>Contact: {ABOUT_INFORMATION["contact_email"]}</p>\n'
    '</body>\n'
    '</html>\n'
)


def about_endpoint(request):
    return HttpResponse(ABOUT_RESPONSE, content_type='text/html')


def about_page(request):
    return render(request, 'library_info/about.html', {'about': ABOUT_INFORMATION})
