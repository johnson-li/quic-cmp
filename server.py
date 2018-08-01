import os
import subprocess
import signal
import sys
import socket
import time
import re
import json

# webTop500 = open('alexaTop500.txt', 'r')
webTop500 = open('webTest.txt', 'r')

log = open('log.txt', 'wb')
network_test = open('network_test.txt', 'wb')

host = '10.166.0.2'
server = []
iperf_data = []

websites_path = '/home/johnsonli1993/websites/'

client_ip = {}
with open('./client_external_ip.json', 'r') as json_file:
    client_ip = json.load(json_file)

# clientHost_list = ['35.228.241.175']
clientHost_list = client_ip.values()
clientPort = 8698

def parse(netstat_output):
    data = {}
    lines = netstat_output.split('\n')
    heap = []
    entry = data
    heap.append((-1, entry))
    for line in lines:
        if not line:
            continue
        if line.endswith(':'):
            prefix = len(re.findall('^ *', line)[0])
            if not heap or prefix > heap[-1][0]:
                entry[line[prefix:-1]] = {}
                entry = entry[line[prefix:-1]]
                heap.append((prefix, entry))
            else:
                while heap and prefix <= heap[-1][0]:
                    heap.pop()
                    entry = heap[-1][1]
                entry[line[prefix:-1]] = {}
                entry = entry[line[prefix:-1]]
                heap.append((prefix, entry))
        else:
            prefix = len(re.findall('^ *', line)[0])
            while prefix <= heap[-1][0]:
                heap.pop()
                entry = heap[-1][1]
            match = re.match(' +(\d+)(.*)', line)
            if match:
                entry[match.group(2).strip()] = match.group(1)
            else:
                match = re.match(' +(.+): (\d+)', line)
                if match:
                    entry[match.group(1).strip()] = match.group(2)
                else:
                    print("Unrecognized line: " + line)
    return data

if __name__ == '__main__':

    n = len(clientHost_list)
    for i in range(n):
        clientHost = clientHost_list[i]
        clientAddr = (clientHost, clientPort)
        port = 8650 + i
        server.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        server[i].bind((host, port))
        server[i].connect(clientAddr)
        print('Test bandwidth to: %s' % clientHost)
        iperf_data.append(json.loads(subprocess.check_output(['iperf3', '-Jc', clientHost])))
        print('Bandwidth: %s' % iperf_data[-1]['end']['sum_sent']['bits_per_second'])

    for web in webTop500.readlines():
        data = ''
        print web
        log.write(web)
        log.write('\n')
        with open('Caddyfile', 'r+') as caddyFile:
            for line in caddyFile.readlines():
                if line.startswith('root /'):
                    line = 'root ' + websites_path + web
                data += line
        with open('Caddyfile', 'w') as caddyFile:
            caddyFile.writelines(data)

        commands = [['sudo', './caddy', '-quic'], ['sudo', './caddy'], ['sudo', './caddy', '-http2=false']]

        for command in commands:
            network_status_pre = parse(os.popen('netstat -s').read())
            p = subprocess.Popen(command)
            pid = p.pid
            print pid
            for i in range(n):
                port = 8650 + i
                server[i].send('Server ready:' + web + ' ' + command[-1])
                data = server[i].recv(1024)
                if data == 'client completed!':
                    network_status_after = parse(os.popen('netstat -s').read())
                    network_test.write(clientHost_list[i] + ' ' + web + ' ' + command[-1] + ':\n')
                    print('tcp transmited: %d' % (float(network_status_after['Tcp']['segments send out']) - float(network_status_pre['Tcp']['segments send out'])))
                    network_test.write('tcp transmited: %d \n' % (float(network_status_after['Tcp']['segments send out']) - float(network_status_pre['Tcp']['segments send out'])))
                    print('tcp retransmited: %d' % (float(network_status_after['Tcp']['segments retransmited']) - float(network_status_pre['Tcp']['segments retransmited'])))
                    network_test.write('tcp transmited: %d \n' % (float(network_status_after['Tcp']['segments send out']) - float(network_status_pre['Tcp']['segments send out'])))
                    #os.kill(pid, signal.SIGINT)
                    os.system('sudo pkill caddy')
                try:
                    command='''kill $(netstat -nlp | grep :'''+str(port)+''' | awk '{print $7}' | awk -F"/" '{ print $1 }')'''
                    os.system(command)
                except Exception as e:
                    print e
                    log.write(e)

