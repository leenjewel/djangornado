# -*- coding:utf-8 -*-
'''
Created on 2010-8-2

@author: leenjewel
'''

import os, sys
import tornado.web
import tornado.httpserver
import djangornado
from djangornado.core.management.base import BaseCommand

class Command(BaseCommand):
    DAEMON_HELP = r"""
    Run this project with daemon

    rundaemon [options] [fcgi settings]
    
Optional settings: (setting=value)
    pnum:    max number of spare processes / threads.
    workdir: change to this directory when daemonizing.
    pidfile: write the spawned process-id to this file.
    host:    hostname to listen on.
    port:    port to listen on.
    outlog:  write stdout to this file.
    errlog:  write stderr to this file.
    umask:   umask to use when daemonizing (default 022).
    """
    
    DAEMON_OPTIONS = {
        'pnum': 1,
        'method':None,
        'workdir': '/',
        'pidfile':None,
        'host': None,
        'port': None,
        'outlog': None,
        'errlog': None,
        'umask': None,
    }
    
    help = "Runs this project as a FastCGI application."
    args = '[various KEY=val options, use `rundaemon help` for help]'

    def handle(self, *args, **options):
        daemon_options = self.DAEMON_OPTIONS.copy()
        daemon_options.update(options)
        for x in args:
            if "=" in x:
                k, v = x.split('=', 1)
            else:
                k, v = x, True
            daemon_options[k.lower()] = v
        
        if os.name == 'posix':
            def become_daemon(our_home_dir='.', out_log='/dev/null',
                              err_log='/dev/null', umask=022):
                "Robustly turn into a UNIX daemon, running in our_home_dir."
                # First fork
                try:
                    if os.fork() > 0:
                        sys.exit(0)     # kill off parent
                except OSError, e:
                    sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
                    sys.exit(1)
                os.setsid()
                os.chdir(our_home_dir)
                os.umask(umask)
        
                # Second fork
                try:
                    if os.fork() > 0:
                        os._exit(0)
                except OSError, e:
                    sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
                    os._exit(1)
        
                si = open('/dev/null', 'r')
                so = open(out_log, 'a+', 0)
                se = open(err_log, 'a+', 0)
                os.dup2(si.fileno(), sys.stdin.fileno())
                os.dup2(so.fileno(), sys.stdout.fileno())
                os.dup2(se.fileno(), sys.stderr.fileno())
                # Set custom file descriptors so that they get proper buffering.
                sys.stdout, sys.stderr = so, se
        else:
            def become_daemon(our_home_dir='.', out_log=None, err_log=None, umask=022):
                """
                If we're not running under a POSIX system, just simulate the daemon
                mode by doing redirections and directory changing.
                """
                os.chdir(our_home_dir)
                os.umask(umask)
                sys.stdin.close()
                sys.stdout.close()
                sys.stderr.close()
                if err_log:
                    sys.stderr = open(err_log, 'a', 0)
                else:
                    sys.stderr = NullDevice()
                if out_log:
                    sys.stdout = open(out_log, 'a', 0)
                else:
                    sys.stdout = NullDevice()
        
            class NullDevice:
                "A writeable object that writes to nowhere -- like /dev/null."
                def write(self, s):
                    pass

        daemon_kwargs = {}
        if daemon_options['outlog']:
            daemon_kwargs['out_log'] = daemon_options['outlog']
        if daemon_options['errlog']:
            daemon_kwargs['err_log'] = daemon_options['errlog']
        if daemon_options['umask']:
            daemon_kwargs['umask'] = int(daemon_options['umask'])
        
        become_daemon(our_home_dir = daemon_options["workdir"], **daemon_kwargs)
        
        if daemon_options["pidfile"]:
            fp = open(daemon_options["pidfile"], "w")
            fp.write("%d\n" % os.getpid())
            fp.close()

        try:
            from djangornado.conf import settings
            from djangornado.conf import urlpatterns
            application = tornado.web.Application(urlpatterns.urlmap, **settings)
            http_server = tornado.httpserver.HTTPServer(application)
            if daemon_options["method"] == "prefork":
                http_server.bind(int(daemon_options.get("port", 8000)), daemon_options.get("host", "127.0.0.1"))
                http_server.start(int(daemon_options.get("pnum", 1)))
            else:
                http_server.listen(int(daemon_options.get("port", 8000)), daemon_options.get("host", "127.0.0.1"))
            tornado.ioloop.IOLoop.instance().start()
        except Exception, e:
            sys.stderr.write("Error: %s \n" % str(e))
            os._exit(1)
        
    def usage(self, subcommand):
        return self.DAEMON_HELP