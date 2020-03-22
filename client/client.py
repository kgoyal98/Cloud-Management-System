import threading
from enum import Enum
import logging
import socket
import time
import numpy as np
import sys
import libvirt

accept_vm_port = 5000
server_port = 5001
receive_result_port = 5002
delta = 5
servers = {}
servers_lock = threading.Lock()
cpu_thresh = 90.0

class VMState(Enum):
	IDLE = 1
	BUSY = 2
	BOOTING = 3
	SHUT_OFF = 4


class ClientState(Enum):
	CONSTANT = 1
	RELAX = 2
	BOOTING = 3
	ERROR = 4


client_state = ClientState.RELAX
cpu_load = 0.0


class VM(object):
	def __init__(self, name=None, ip=None, state=None):
		self.name = name
		self.ip = ip
		self.state = state
		

class AcceptVM(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
		
	def run(self):
		global servers, servers_lock, client_state
		host = '0.0.0.0'
		skt = socket.socket()
		skt.bind((host, self.port))
		skt.listen(10)
		while True:
			conn, address = skt.accept()
			ip = str(address[0])
			name = conn.recv(1024).decode()
			logging.info(f"New VM {name} accepted at ip {ip}")
			servers_lock.acquire()
			vm = VM(name=name, ip=ip, state=VMState.IDLE)
			servers[ip] = vm
			servers_lock.release()
			conn.close()
			client_state = ClientState.RELAX
			logging.debug('Client state: relaxed')


class ReceiveResult(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
		
	def run(self):
		global servers, servers_lock
		host = '0.0.0.0'
		skt = socket.socket()
		skt.bind((host, self.port))
		skt.listen(10)
		while True:
			conn, address = skt.accept()
			ip = str(address[0])
			data = conn.recv(1024).decode()
			logging.info(f"Received response {data} from {servers[ip].name}")
			servers_lock.acquire()
			servers[ip].state = VMState.IDLE
			servers_lock.release()

			conn.close()


class SendWork(threading.Thread):
	def __init__(self, server_port, delta):
		threading.Thread.__init__(self)
		self.server_port = server_port
		self.delta = delta
		
	def run(self):
		global servers, servers_lock
		i = 1
		while True:
			word = 'word' + str(i)
			done = False
			logging.debug('Searching for idle server...')
			while not done:
				# logging.info(f'servers {servers}')
				servers_lock.acquire()
				for ip, vm in servers.items():
					if vm.state == VMState.IDLE:
						server_ip = ip
						port = self.server_port
						skt = socket.socket()
						skt.connect((server_ip, port))
						skt.send(word.encode())
						servers[ip].state = VMState.BUSY
						logging.info(f"Sent work to {vm.name}: {word}")
						skt.close()
						done = True
						break
				servers_lock.release()
				# if not done:
				# 	logging.debug('No available server')
				# time.sleep(1)
			time.sleep(delta)
			i+=1
		

def get_response(dom, port, message):
	host = dom.interfaceAddresses(0)['vnet0']['addrs'][0]['addr']
	client_socket = socket.socket()
	client_socket.connect((host, port))
	client_socket.send(message.encode())
	data = client_socket.recv(1024).decode()
	logging.info(f'Response from {dom.name} server:\n{message}: {data}')
	client_socket.close()




class VMManager(threading.Thread):
	def __init__(self, cpu_thresh, url):
		threading.Thread.__init__(self)
		self.cpu_thresh = cpu_thresh
		self.url = url
	

	def get_cpu_time(self, vm):
		conn = libvirt.open(self.url)
		dom = conn.lookupByName(vm.name)
		cpu_stats = dom.getCPUStats(True)
		conn.close()
		return cpu_stats[0]['cpu_time']


	def boot_new_server(self):
		conn = libvirt.open(self.url)
		doms = conn.listDefinedDomains()
		if doms == []:
			logging.debug('No defined domains')
		else:
			dom = conn.lookupByName(doms[0])
			dom.create()
			logging.debug(f'Created domain {doms[0]}')
		
		conn.close()


	def shut_one_server(self):
		global servers, servers_lock
		conn = libvirt.open(self.url)
		doms = conn.listDefinedDomains()
		servers_lock.acquire()
		for ip, vm in servers.items():
			if vm.state == VMState.IDLE:
				dom = conn.lookupByName(vm.name)
				r = dom.shutdown()
				if r == 0:
					logging.info(f'Shutdown domain {vm.name}')
					servers[ip].state = VMState.SHUT_OFF
				else:
					logging.error(f'Error in shutdown domain {dom.name}')
				servers_lock.release()
				return
		servers_lock.release()
		logging.error(f'No idle domain to shut')

	def run(self):
		global servers, servers_lock, client_state
		while True:
			start = {}
			t = time.time()
			servers_lock.acquire()
			for ip, vm in servers.items():
				if vm.state == VMState.BUSY or vm.state == VMState.IDLE:
					start[ip] = self.get_cpu_time(vm)
			servers_lock.release()
			time.sleep(30)
			loads = []
			servers_lock.acquire()
			for ip, vm in servers.items():
				if vm.state == VMState.BUSY or vm.state == VMState.IDLE:
					if ip not in start:
						start[ip] = 0
					vm_load = (self.get_cpu_time(vm) - start[ip]) / (time.time() - t) / 1e9 * 100
					logging.debug(f'CPU load for {vm.name}: {int(vm_load)}%')
					loads.append(vm_load)
			servers_lock.release()
			average_load = 0
			if loads:
				average_load = np.mean(loads)
			else:
				logging.debug(f'No running VM')

			file = open("load.txt", "w+")
			file.write(str(average_load))
			file.close()
			logging.info(f'average CPU load: {int(average_load)}%')
			if average_load > self.cpu_thresh and client_state == ClientState.CONSTANT:
				logging.info(f'Detected high load, starting new server...')
				self.boot_new_server()
				client_state = ClientState.BOOTING
				logging.debug('Client state: booting')
			else:
				n = len(loads)
				left = (self.cpu_thresh - average_load) * n
				if left > cpu_thresh and client_state == ClientState.CONSTANT:
					logging.info('Detected low load')
					self.shut_one_server()
					client_state = ClientState.RELAX
					logging.debug('Client state: relax')

			if client_state == ClientState.RELAX:
				client_state = ClientState.CONSTANT
				logging.debug('Client state: constant')




if __name__ == '__main__':
	# conn = libvirt.open('qemu:///system')
	# if conn == None:
	# 	print('Failed to open connection to qemu:///system', file=sys.stderr)
	# while True:
	# 	for dom in conn.listAllDomains():
	# 		ip = dom.interfaceAddresses(0)['vnet0']['addrs'][0]['addr']
	# 		servers[ip] = VM(name=dom.name, ip=ip, domain=dom, connection=conn)

	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s', filename='log',
                        filemode='a')
	# servers['192.168.122.207'] = VM(ip='192.168.122.207', state=VMState.IDLE)
	accept_vm = AcceptVM(accept_vm_port)
	worker = SendWork(server_port, delta)
	receive_result = ReceiveResult(receive_result_port)
	vm_manager = VMManager(cpu_thresh, url='qemu:///system')

	worker.start()
	accept_vm.start()
	receive_result.start()
	vm_manager.start()

	while True:
		delta = float(input())
		worker.delta = delta

	conn.close()