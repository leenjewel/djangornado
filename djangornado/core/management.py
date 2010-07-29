# -*- coding:utf-8 -*-
'''
Created on 2010-7-28

@author: leenjewel
'''

import sys, os, logging, logging.config
from multiprocessing import Process

import tornado.web
import tornado.httpserver
import djangornado
from djangornado.utils.importlib import import_module

class UndefinedOption(Exception):
    pass

class _Options(dict):
    def __getattr__(self, name):
        if self.has_key(name):
            return self[name]
        else:
            raise UndefinedOption

_options = None

_commands = None

_prog = None

_subcommand = None

def get_options():
    global _options
    if _options is None:
        _options = _Options({
                                'pnum': None,
                                'log': None,
                                'err': None,
                            })
    return _options

def get_commands():
    global _commands
    if _commands is None:
        _commands = {
                       'version': show_version,
                       'help': show_help,
                       'run': run_server,
                       'shell': shell,
                       'daemon': daemon,
                    }
    return _commands

def show_version():
    print djangornado.get_version()

def show_help():
    print '''Usage: %s subcommand [options] [args]

Options:
  --settings=SETTINGS   The path to application configuration file, e.g.
                        "/home/djangoprojects/myproject/conf/settings.conf".
                        If this isn't provided, the RKORNADO_CONF_FILE
                        environment variable will be used.
  --app=APPLICATIONPATH A directory to add to the Python path as
                        application's root path, e.g.
                        "/home/djangoprojects/myproject/src/app/".
  --lib=LIBRARYPATH     A directory to add to the Python path as
                        application's library path, e.g.
                        "/home/djangoprojects/myproject/src/lib/".
  --log-config=CONFIGFILE
                        The path to application logging configuration file,
                        e.g. "//home/djangoprojects/myproject/conf/logconfig.conf"
  --version             show program's version number and exit
  -h, --help            show this help message and exit

Type 'manage.py help <subcommand>' for help on a specific subcommand.

Available subcommands:
shell
run
daemon
help
''' % _prog

def _build_environ(settings_mod, original_settings_path = None):
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

    # Import the project module. We add the parent directory to PYTHONPATH to
    # avoid some of the path errors new users can have.
    sys.path.append(os.path.join(project_directory, os.pardir))
    project_module = import_module(project_name)
    sys.path.pop()
    options = get_options()
    return
    #logging.config.fileConfig(options['log-config'])

def get_tornado_server():
    from conf import settings
    from http.handler import RKHandler
    application = tornado.web.Application(
        [('^/(.*)$', RKHandler),], **settings
    )
    http_server = tornado.httpserver.HTTPServer(application)
    return http_server

def _start_server(host, port, http_server):
    http_server.bind(int(port), host)
    http_server.start(get_options()['pnum'])
    tornado.ioloop.IOLoop.instance().start()

def run_server(*args):
    get_options()['pnum'] = 1
    http_server = get_tornado_server()
    host, port = args[0].split(":")
    _start_server(host, port, http_server)

def _run_daemon(*args):
    http_server = get_tornado_server()
    options = get_options()

    if options['log']:
        std_out = open(options['log'], "a+", 0)
        os.dup2(std_out.fileno(), sys.stdout.fileno())
        sys.stdout = std_out

    if options['err']:
        std_err = open(options['err'], "a+", 0)
        os.dup2(std_err.fileno(), sys.stderr.fileno())
        sys.stderr = std_err

    _start_server(http_server)

def daemon(*args):
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    options = get_options()
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)
    # decouple from parent environment
    # os.chdir("/")
    os.setsid()
    os.umask(0)
    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # start the daemon main loop
    _run_daemon()

def shell(*args):
    import code
    # Set up a dictionary to serve as the environment for the shell, so
    # that tab completion works on objects that are imported at runtime.
    # See ticket 5082.
    imported_objects = {}
    try: # Try activating rlcompleter, because it's handy.
        import readline
    except ImportError:
        pass
    else:
        # We don't have to wrap the following import in a 'try', because
        # we already know 'readline' was imported successfully.
        import rlcompleter
        readline.set_completer(rlcompleter.Completer(imported_objects).complete)
        readline.parse_and_bind("tab:complete")

    # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
    # conventions and get $PYTHONSTARTUP first then import user.
    pythonrc = os.environ.get("PYTHONSTARTUP")
    if pythonrc and os.path.isfile(pythonrc):
        try:
            execfile(pythonrc)
        except NameError:
            pass
        # This will import .pythonrc.py as a side-effect
    import user
    code.interact(local=imported_objects)

def execute_manager(settings, args=None):
    _build_environ(settings)
    args = args or sys.argv[:]
    _parse_command_line(sys.argv[:])

def _parse_command_line(args):
    global _prog
    global _subcommand
    options = get_options()
    try:
        _prog = args[0]
        _subcommand = args[1]
    except:
        print >>sys.stderr, 'Command error!'
        show_help()
    else:
        for item in args[2:]:
            option_pair = item.split('=')
            if len(option_pair) == 2 and option_pair[0][2:] in options:
                if option_pair[0] == '--pnum':
                    option_pair[1] = int(option_pair[1])
                options[option_pair[0][2:]] = option_pair[1]
            elif len(option_pair) == 1 and option_pair[0][2:] in ['version', 'help']:
                _subcommand = option_pair[0][2:]
        if _subcommand in get_commands():
            get_commands()[_subcommand](*args[2:])
        else:
            print >>sys.stderr, 'Command error!'
            show_help()