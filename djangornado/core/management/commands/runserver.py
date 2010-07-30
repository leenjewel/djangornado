# -*- coding:utf-8 -*-
'''
Created on 2010-7-30

@author: leenjewel
'''

from djangornado.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os
import sys
import tornado.web
import tornado.httpserver
import djangornado

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--pnum', dest = 'pnum', default = '1', help = 'Set pnum ,default is 1'),
        make_option('--daemon', action = 'store_false', dest = 'is_daemon', default = False, help = 'Run server with daemon')
    )
    help = "Starts a lightweight Web server for development."
    args = '[optional port number, or ipaddr:port]'

    # Validation is called explicitly each time the server is reloaded.
    requires_model_validation = False

    def handle(self, addrport='', *args, **options):
        if args:
            raise CommandError('Usage is runserver %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'

        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)

        shutdown_message = options.get('shutdown_message', '')
        pnum = options.get("pnum", "1")
        is_daemon = options.get("is_daemon", False)
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        def inner_run():
            from djangornado.conf import settings
            from djangornado.http.handler import DjangornadoHandler
            print "\nDjangornado version %s" % (djangornado.get_version())
            print "Development server is running at http://%s:%s/" % (addr, port)
            print "Quit the server with %s." % quit_command

            try:
                application = tornado.web.Application([('^/(.*)$', DjangornadoHandler),], **settings)
                http_server = tornado.httpserver.HTTPServer(application)
                http_server.bind(int(port), addr)
                http_server.start(int(pnum))
                tornado.ioloop.IOLoop.instance().start()
            except Exception, e:
                sys.stderr.write("Error: %s \n" % str(e))
                os._exit(1)
            except KeyboardInterrupt:
                if shutdown_message:
                    print shutdown_message
                sys.exit(0)
        if is_daemon:
            # do the UNIX double-fork magic, see Stevens' "Advanced
            # Programming in the UNIX Environment" for details (ISBN 0201563177)
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
        inner_run()