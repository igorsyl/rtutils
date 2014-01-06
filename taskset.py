#!/usr/bin/env python
import sys
import subprocess
import os

def get_affinity(pid):
    text = subprocess.check_output('taskset -c -p %s' % pid, shell=True)
    line1, line2 = text.split('\n')[:2]
    return line1.split(': ')[1]

def get_cmdline(pid):
    try:
        with file('/proc/%s/comm' % pid) as f:
            return f.readlines()[0][:-1]
    except IOError:
        pass

def dopid(prefix, pid, action, taskset_args):
    pid = int(pid)
    prev_prio = get_affinity(pid)
    if action == 'get':
        print prefix + '%s: %s' % (pid, prev_prio)
        
    cmd = 'taskset -a -c -p %s %s' % (taskset_args, pid)
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
        taskset_args = ' '.join(sys.argv[3:])
    else:
        taskset_args = ''
    
    if pgrep == 'all':
        ppids = [p.strip() for p in subprocess.check_output('ps -eo pid', shell=True).split('\n')[1:]]
    else:
        ppids = subprocess.check_output('pgrep %s' % pgrep, shell=True).split('\n')[:-1]

    for ppid in ppids:
        cmdline = get_cmdline(ppid)
        if not cmdline: continue
        dopid('%s  ' % cmdline, ppid, action, taskset_args)
        for cpid in os.listdir('/proc/%s/task' % ppid):
            if ppid != cpid:
                dopid('     ', cpid, action, taskset_args)

if __name__ == '__main__':
    main()
