import sys
if __name__ == '__main__':
	server_addr = sys.argv[1]
	resolv_file = '/etc/resolv.conf'
	data = ''
	with open(resolv_file, 'r+') as caddyFile:
		for line in caddyFile.readlines():
			if line.startswith('nameserver '):
				line = 'nameserver ' + server_addr 
			data += line
	with open(resolv_file, 'w') as caddyFile:
		caddyFile.writelines(data)