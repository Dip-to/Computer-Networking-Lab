from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

class S(BaseHTTPRequestHandler):
    def _set_response(val):
        val.send_response(200)
        val.send_header('Content-type', 'text/html')
        val.end_headers()

    def do_GET(val):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(val.path), str(val.headers))
        file_path = val.path[1:]  
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

        except FileNotFoundError:
            logging.error("File not found: %s", file_path)
            val.send_error(404, "File not found")
            return
        nam=f.name.encode("utf-8")
        val._set_response()
        val.wfile.write(file_content)

    def do_POST(val):
        content_length = int(val.headers['Content-Length']) 
        post_data = val.rfile.read(content_length) 
        print("hello", val.responses)
        with open('output.in', 'wb') as local_file:
            for chunk in post_data.iter_content(chunk_size=content_length):
                local_file.write(chunk)
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(val.path), str(val.headers), post_data.decode('utf-8'))

        val._set_response()
        val.wfile.write("POST request for {}".format(val.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()