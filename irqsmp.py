#!/usr/bin/env python
import re
import sys
import re

def main():
	action = sys.argv[1]
	if action == 'get':
		re_name = sys.argv[2] if len(sys.argv) > 2 else '.*'
	if action == 'set' or action == 'try':
		re_name = sys.argv[2]
		if re_name == 'all': re_name = '.*'
		smp_affinity = sys.argv[3]

	irq_lines = open('/proc/interrupts').readlines()
	name_idx = len(irq_lines[0])
	for irq_line in irq_lines:
		name = irq_line[name_idx:-1].split(' ')[-1]
		irq_number_match = re.match(' *(\d+):.*', irq_line)
		irq_name_match = re.findall(re_name, name)
		if irq_number_match and irq_name_match:
			irq_number = int(irq_number_match.groups()[0])
			irq_name = name
			smp_file = '/proc/irq/%s/smp_affinity' % irq_number
			smp_list_file = '/proc/irq/%s/smp_affinity_list' % irq_number
			prev_affinity = open(smp_file, 'r').readline()[:-1]
			prev_affinity_list = open(smp_list_file, 'r').readline()[:-1]
			if action == 'get':
				print '%s %s: %s (%s)' % (irq_name, irq_number, prev_affinity, prev_affinity_list)
			if action == 'set' or action == 'try':
				print '%s %s: %s -> %s' % (irq_name, irq_number, prev_affinity, smp_affinity)
			if action == 'set':
				try:
					out = open(smp_file, 'w')
					out.write(smp_affinity)
					out.close()
				except Exception as e:
					print 'error: %s' % e

if __name__ == '__main__':
	main()
