#!/usr/bin/env python
import sys
import subprocess
import os

def get_prio(pid):
    text = subprocess.check_output('chrt -p %s' % pid, shell=True)
    line1, line2 = text.split('\n')[:2]
    policy = line1.split(': ')[1]
    prio = line2.split(': ')[1]
    return '%s %s' % (policy, prio)

def get_cmdline(pid):
    with file('/proc/%s/comm' % pid) as f:
        return f.readlines()[0][:-1]

def dopid(prefix, pid, action, chrt_args):
    pid = int(pid)
    prev_prio = get_prio(pid)
    if action == 'get':
        print prefix + '%s: %s' % (pid, prev_prio)
        
    cmd = 'chrt -p -a %s %s' % (chrt_args, pid)
    if action == 'set' or action == 'try':
        print prefix + cmd
    if action == 'set':
        try:
            subprocess.check_output(cmd, shell=True)
        except Exception as e:
            print prefix + 'error: %s' % e

def main():
    action = sys.argv[1]
    pgrep = sys.argv[2]
    if action == 'set' or action == 'try':
        chrt_args = ' '.join(sys.argv[3:])
    else:
        chrt_args = ''
    
    ppids = subprocess.check_output('pgrep %s' % pgrep, shell=True).split('\n')[:-1]
    for ppid in ppids:
        cmdline = get_cmdline(ppid)
        dopid('%s  ' % cmdline, ppid, action, chrt_args)
        for cpid in os.listdir('/proc/%s/task' % ppid):
            if ppid != cpid:
                dopid('     ', cpid, action, chrt_args)

if __name__ == '__main__':
    main()
