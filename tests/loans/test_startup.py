from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.management import get_commands, load_command_class


def test_runserver_uses_the_characterized_default_host_and_port():
    command = load_command_class(get_commands()['runserver'], 'runserver')

    assert (command.default_addr, command.default_port) == ('0.0.0.0', '8080')


def test_runserver_serves_the_committed_stylesheet_with_debug_disabled(settings):
    settings.DEBUG = False
    command = load_command_class(get_commands()['runserver'], 'runserver')

    handler = command.get_handler(use_static_handler=True, insecure_serving=False)

    assert isinstance(handler, StaticFilesHandler)
