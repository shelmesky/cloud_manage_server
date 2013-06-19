from gevent import socket

def check_tcp(ip,port):
    HOST = ip
    PORT = port
    ADDR = (HOST,PORT)
    tcpsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcpsock.settimeout(1)
    try:
        tcpsock.connect(ADDR)
    except:
        return False
    else:
        return True
    finally:
        tcpsock.close()

if __name__ == '__main__':
    check_tcp('8.8.8.8',80)