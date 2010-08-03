# -*- coding:utf-8 -*-
import os
import sys
from optparse import OptionParser, NO_DEFAULT
import imp

import djangornado
from djangornado.core.management.base import BaseCommand, CommandError, handle_default_options
from djangornado.utils.importlib import import_module

get_version = djangornado.get_version

_commands = None

def find_commands(management_dir):
    command_dir = os.path.join(management_dir, 'commands')
    try:
        return [f[:-3] for f in os.listdir(command_dir)
                if not f.startswith('_') and f.endswith('.py')]
    except OSError:
        return []

def find_management_module(app_name):
    parts = app_name.split('.')
    parts.append('management')
    parts.reverse()
    part = parts.pop()
    path = None

    try:
        f, path, descr = imp.find_module(part,path)
    except ImportError,e:
        if os.path.basename(os.getcwd()) != part:
            raise e

    while parts:
        part = parts.pop()
        f, path, descr = imp.find_module(part, path and [path] or None)
    return path

def load_command_class(app_name, name):
    module = import_module('%s.management.commands.%s' % (app_name, name))
    return module.Command()

def get_commands():
    global _commands
    if _commands is None:
        _commands = dict([(name, 'djangornado.core') for name in find_commands(__path__[0])])
    return _commands

def call_command(name, *args, **options):
    try:
        app_name = get_commands()[name]
        if isinstance(app_name, BaseCommand):
            # If the command is already loaded, use it directly.
            klass = app_name
        else:
            klass = load_command_class(app_name, name)
    except KeyError:
        raise CommandError("Unknown command: %r" % name)

    defaults = dict([(o.dest, o.default)
                     for o in klass.option_list
                     if o.default is not NO_DEFAULT])
    defaults.update(options)

    return klass.execute(*args, **defaults)

class LaxOptionParser(OptionParser):
    def error(self, msg):
        pass

    def print_help(self):
        pass

    def print_lax_help(self):
        OptionParser.print_help(self)

    def _process_args(self, largs, rargs, values):
        while rargs:
            arg = rargs[0]
            try:
                if arg[0:2] == "--" and len(arg) > 2:
                    # process a single long option (possibly with value(s))
                    # the superclass code pops the arg off rargs
                    self._process_long_opt(rargs, values)
                elif arg[:1] == "-" and len(arg) > 1:
                    # process a cluster of short options (possibly with
                    # value(s) for the last one only)
                    # the superclass code pops the arg off rargs
                    self._process_short_opts(rargs, values)
                else:
                    # it's either a non-default option or an arg
                    # either way, add it to the args list so we can keep
                    # dealing with options
                    del rargs[0]
                    raise Exception
            except:
                largs.append(arg)

class ManagementUtility(object):
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])

    def main_help_text(self):
        usage = ['',"Type '%s help <subcommand>' for help on a specific subcommand." % self.prog_name,'']
        usage.append('Available subcommands:')
        commands = get_commands().keys()
        commands.sort()
        for cmd in commands:
            usage.append('  %s' % cmd)
        return '\n'.join(usage)

    def fetch_command(self, subcommand):
        try:
            app_name = get_commands()[subcommand]
            if isinstance(app_name, BaseCommand):
                # If the command is already loaded, use it directly.
                klass = app_name
            else:
                klass = load_command_class(app_name, subcommand)
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" % \
                (subcommand, self.prog_name))
            sys.exit(1)
        return klass

    def execute(self):
        parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                                 version=get_version(),
                                 option_list=BaseCommand.option_list)
        try:
            options, args = parser.parse_args(self.argv)
            handle_default_options(options)
        except:
            pass # Ignore any option errors at this point.

        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help' # Display help if no arguments were given.

        if subcommand == 'help':
            if len(args) > 2:
                self.fetch_command(args[2]).print_help(self.prog_name, args[2])
            else:
                parser.print_lax_help()
                sys.stderr.write(self.main_help_text() + '\n')
                sys.exit(1)
        elif self.argv[1:] == ['--version']:
            pass
        elif self.argv[1:] == ['--help']:
            parser.print_lax_help()
            sys.stderr.write(self.main_help_text() + '\n')
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)

def setup_environ(settings_mod, original_settings_path=None):
    if '__init__.py' in settings_mod.__file__:
        p = os.path.dirname(settings_mod.__file__)
    else:
        p = settings_mod.__file__
    project_directory, settings_filename = os.path.split(p)
    if project_directory == os.curdir or not project_directory:
        project_directory = os.getcwd()
    project_name = os.path.basename(project_directory)

    # Strip filename suffix to get the module name.
    settings_name = os.path.splitext(settings_filename)[0]

    # Strip $py for Jython compiled files (like settings$py.class)
    if settings_name.endswith("$py"):
        settings_name = settings_name[:-3]

    # Set DJANGO_SETTINGS_MODULE appropriately.
    if original_settings_path:
        os.environ['DJANGORNADO_SETTINGS_MODULE'] = original_settings_path
    else:
        os.environ['DJANGORNADO_SETTINGS_MODULE'] = '%s.%s' % (project_name, settings_name)

    sys.path.append(os.path.join(project_directory, os.pardir))
    project_module = import_module(project_name)
    sys.path.pop()

    return project_directory

def execute_from_command_line(argv=None):
    utility = ManagementUtility(argv)
    utility.execute()

def execute_manager(settings_mod, argv=None):
    setup_environ(settings_mod)
    utility = ManagementUtility(argv)
    utility.execute()