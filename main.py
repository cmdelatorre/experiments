import Queue

from arduino_sensors import *

TIMEOUT = 5


def main():
    messages = Queue.Queue()
    # Start listener
    t = MessengerThread(messages)
    t.start()

    run = True
    while run:
        try:
            msg = messages.get(block=True, timeout=TIMEOUT)
            print(msg)
        except Queue.Empty:
            print("Timeout")
            run = False


if __name__ == '__main__':
    main()
