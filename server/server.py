import socket
import hashlib
import logging


client_ip = '192.168.122.1'
client_port = 5002
server_ready_port = 5000
server_port = 5001


def calculate_collision_string(data):
    h = lambda x: hashlib.sha256(x.encode('utf-8')).hexdigest()
    x =  h(data)
    i=0
    while True:
        if h(str(i))[:6] == x[:6]:
            break
        i+=1
    return str(i)


def loop_for_t(data, t=5):
    import time
    start = time.time()
    i=0
    while True:
        i+=1
        if (time.time() - start) > t:
            break
    return str(i)


class Program(object):
    def __init__(self, receive_port, client_ip, client_port, server_ready_port, function):
        self.receive_port = receive_port
        self.client_ip = client_ip
        self.client_port = client_port
        self.server_ready_port = server_ready_port
        self.function = function

        self.receive_socket = socket.socket()
        self.receive_socket.bind(('0.0.0.0', self.receive_port))
        
    def notify_client(self):
        skt = socket.socket()
        skt.connect((self.client_ip, self.server_ready_port))
        skt.send(socket.gethostname().encode())
        logging.info(f'Notified client of the new server')
        skt.close()

    def receive_work(self):
        self.receive_socket.listen(1)
        logging.info(f'Listening for work')
        conn, address = self.receive_socket.accept()
        ip = address[0]
        data = conn.recv(1024).decode()
        logging.info(f'Received work from {ip}: {data}')
        conn.close()
        return data

    def send_result(self, result):
        self.send_socket = socket.socket()
        self.send_socket.connect((self.client_ip, self.client_port))
        self.send_socket.send(result.encode())
        logging.info(f'Sent to client ip {client_ip} result {result}')
        self.send_socket.close()

    def run(self):
        self.notify_client()
        while True:
            work = self.receive_work()
            result = self.function(work)
            self.send_result(result)

    def close(self):
        self.receive_socket.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', filename='/home/kunal/log',
                        filemode='a')
    p = Program(server_port, client_ip, client_port, server_ready_port, loop_for_t)
    p.run()