# -*- coding:utf-8 -*-
'''
Created on 2010-7-30

@author: leenjewel
'''

from djangornado.core.management.base import BaseCommand, CommandError
import os
import sys
import tornado.web
import tornado.httpserver
import djangornado

class Command(BaseCommand):
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
                http_server.listen(int(port), addr)
                tornado.ioloop.IOLoop.instance().start()
            except Exception, e:
                sys.stderr.write("Error: %s \n" % str(e))
                os._exit(1)
            except KeyboardInterrupt:
                if shutdown_message:
                    print shutdown_message
                sys.exit(0)
        inner_run()