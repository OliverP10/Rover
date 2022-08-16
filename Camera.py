import logging
from threading import Thread

class Camera:
    thread: Thread

    def __init__(self) -> None:
        self.thread: Thread = Thread(target=self.start,args=()).start()

    def start(self) -> None:
        logger = logging.getLogger(__name__)

        # Web streaming example
        # Source code from the official PiCamera package
        # http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

        import io
        import picamera
        import socketserver
        from threading import Condition
        from http import server


        class StreamingOutput(object):
            def __init__(self):
                self.frame = None
                self.buffer = io.BytesIO()
                self.condition = Condition()

            def write(self, buf):
                if buf.startswith(b'\xff\xd8'):
                    # New frame, copy the existing buffer's content and notify all
                    # clients it's available
                    self.buffer.truncate()
                    with self.condition:
                        self.frame = self.buffer.getvalue()
                        self.condition.notify_all()
                    self.buffer.seek(0)
                return self.buffer.write(buf)

        class StreamingHandler(server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/stream.mjpg':
                    self.send_response(200)
                    self.send_header('Age', 0)
                    self.send_header('Cache-Control', 'no-cache, private')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
                    self.end_headers()
                    try:
                        while True:
                            with output.condition:
                                output.condition.wait()
                                frame = output.frame
                            self.wfile.write(b'--FRAME\r\n')
                            self.send_header('Content-Type', 'image/jpeg')
                            self.send_header('Content-Length', len(frame))
                            self.end_headers()
                            self.wfile.write(frame)
                            self.wfile.write(b'\r\n')
                    except Exception as e:
                        logger.info(
                            'Removed streaming client %s: %s',
                            self.client_address, str(e))
                else:
                    self.send_error(404)
                    self.end_headers()

        class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
            allow_reuse_address = True
            daemon_threads = True

        with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
            output = StreamingOutput()
            #Uncomment the next line to change your Pi's Camera rotation (in degrees)
            camera.rotation =180
            camera.start_recording(output, format='mjpeg')
            try:
                address = ('', 8000)
                server = StreamingServer(address, StreamingHandler)
                server.serve_forever()
                logger.info("Camera started")
            finally:
                camera.stop_recording()