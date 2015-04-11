import logging
import socket
import threading

logger = logging.getLogger(__name__)


_MESSAGE_TERMINATOR = '\n\n'
_READ_BLOCK_SIZE = 4096


class MessengerThread(threading.Thread):
    """Receive and enqueue messages."""

    def __init__(self, messages_queue):
        # Prepare server socket
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('127.0.0.1', 0))
        self.socket.listen(1)
        assigned_port = self.socket.getsockname()[1]

        import ipdb; ipdb.set_trace()
        logger.info("Now listening on port %d", assigned_port)
        self._buffer = b''
        self.messages_queue = messages_queue
        super(MessengerThread, self).__init__()

    def _get_message(self):
        while _MESSAGE_TERMINATOR not in self._buffer:
            data = self.socket.recv(_READ_BLOCK_SIZE)
            if not data:
                return None
            self._buffer += data
        message_text, self._buffer = self._buffer.split(_MESSAGE_TERMINATOR, 1)
        logger.debug("Message received: %r [socket=%d]", message_text, self.socket.fileno())
        return Message.parse(message_text)

    def run(self):
        logger.info("Starting thread [socket=%d]", self.socket.fileno())
        while True:
            message = self._get_message()
            if message:
	            self.messages_queue.put(message)

