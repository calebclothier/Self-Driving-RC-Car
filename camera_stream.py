import io
import socket
import struct
import time
import picamera

class Client():
    
    def connect(self):
        # Connect a client socket to the Macbook-based server
        self.client_socket = socket.socket()
        self.client_socket.connect(('192.168.1.15', 8000))

    def stream(self, stream_length):
        # Make a file-like object out of the connection
        connection = self.client_socket.makefile('wb')
        try:
            self.camera = picamera.PiCamera()
            self.camera.resolution = (320, 240)
            # Start a preview and let camera warm up
            self.camera.start_preview()
            time.sleep(2)

            self.start = time.time()
            self.stream = io.BytesIO()
            for foo in self.camera.capture_continuous(self.stream, 'jpeg'):
                # Write the length of the capture to the stream
                # and flush to make sure it gets sent
                connection.write(struct.pack('<L', self.stream.tell()))
                connection.flush()
                # Rewind the stream and send image data through
                self.stream.seek(0)
                connection.write(self.stream.read())
                # End stream after 30 seconds
                if time.time() - self.start > stream_length:
                    break
                # Reset stream for next capture
                self.stream.seek(0)
                self.stream.truncate()
            # Write a length of 0 to the stream to signal we're done
            connection.write(struct.pack('<L', 0))
        finally:
            connection.close()
            self.client_socket.close()

client = Client()
client.connect()
client.stream(60)
