import socket
import hashlib
import threading
import logging
import time


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


def notify_client(client_ip, server_ready_port):
    skt = socket.socket()
    skt.connect((client_ip, server_ready_port))
    skt.send(socket.gethostname().encode())
    logging.info(f'Notified client of the new server')
    skt.close()


class Worker(threading.Thread):

    def __init__(self, receive_port, client_ip, client_port, function):
        threading.Thread.__init__(self)
        self.receive_port = receive_port
        self.client_ip = client_ip
        self.client_port = client_port
        self.function = function

    def send_result(self, result):
        send_socket = socket.socket()
        send_socket.connect((self.client_ip, self.client_port))
        send_socket.send(result.encode())
        logging.info(f'Sent to client ip {client_ip} result {result}')
        send_socket.close()

    def run(self):
        receive_socket = socket.socket()
        receive_socket.bind(('0.0.0.0', self.receive_port))
        receive_socket.listen(1)
        while True:
            logging.info(f'Listening for work')
            conn, address = receive_socket.accept()
            ip = address[0]
            work = conn.recv(1024).decode()
            logging.info(f'Received work from {ip}: {work}')
            conn.close()
            result = self.function(work)
            self.send_result(result)
        receive_socket.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', filename='log',
                        filemode='a')
    worker = Worker(server_port, client_ip, client_port, calculate_collision_string)
    worker.start()
    time.sleep(1)
    notify_client(client_ip, server_ready_port)
