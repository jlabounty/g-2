import zmq
import sys


def main():
    if len(sys.argv) < 2:
        print("need to provide ip address! send_mesasge [ip] [message]")
        sys.exit(0)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.RCVTIMEO, 1000)
    socket.connect("tcp://%s:6669" % sys.argv[1])
    print("sending message!")
    mstr = ''.join('%s ' % arg for arg in sys.argv[2:]).strip()
    print(mstr)
    socket.send_string(mstr)
    print("waiting for reply...")
    try:
        print("got reply " + socket.recv().decode('utf-8'))
    except zmq.error.Again:
        print("timeout")


if __name__ == "__main__":
    main()
