import sys; 
import os;
import cgi;
import math;
import Physics;
import mimetypes;
import json;

# web server parts
from http.server import HTTPServer, BaseHTTPRequestHandler;

# imports classes from Physics Module
from Physics import *

# used to parse the URL and extract form data for GET requests
from urllib.parse import urlparse, parse_qsl;

# HTTP server that includes a connection to the database
class EnhancedHTTPServer(HTTPServer):
    # initializes the server with an address, request handler class, and database connection
    def __init__(self, server_address, RequestHandlerClass, db):
        super().__init__(server_address, RequestHandlerClass)  # initializes the parent class
        self.db = db  # here we store the database connection in the server instance


class myHTTPRequestHandler (BaseHTTPRequestHandler):

    # method that sets up the handler
    def setup(self):
        super().setup()
        self.db = self.server.db # stores the dabatase connection

    def db(self):
        return self.server.db

    def do_GET(self):
        """Handles GET requests from clients, serving specific files based on the request URL."""
        # Parse the URL to extract the path and potentially any query data
        parsed = urlparse(self.path)
         # Serve static files with a generic handler
        if parsed.path.startswith('/'):
            # Construct the file path
            filepath = '.' + self.path  # Assuming files are served from the current directory
            if os.path.isfile(filepath):
                # Determine the file's MIME type and serve it
                mimetype, _ = mimetypes.guess_type(filepath)
                try:
                    with open(filepath, 'rb') as file:
                        content = file.read()
                        self.send_response(200)
                        self.send_header('Content-type', mimetype or 'application/octet-stream')
                        self.send_header('Content-length', len(content))
                        self.end_headers()
                        self.wfile.write(content)
                        return
                except FileNotFoundError:
                    pass  # File was not found; handle below with a 404 response
        # Serve the HTML page if the request path is '/shoot.html'
        elif parsed.path == '/display.html':
            # Attempt to open and read the specified HTML file
            try:
                with open('.' + self.path, 'rb') as fp:  # Open the file in binary mode to read
                    content = fp.read()
                    # Send a 200 OK response along with headers for content type and length
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.send_header("Content-length", len(content))
                    self.end_headers()
                    # Write the file content to the response body
                    self.wfile.write(content)
            except FileNotFoundError:
                # If the file is not found, send a 404 response
                self.send_error(404, "File not found")

        # Serve SVG files matching a specific naming pattern '/table-*.svg'
        elif self.path.startswith("/table-") and self.path.endswith(".svg"):
            # Construct the file path by removing the leading slash
            filename = self.path[1:]
            
            # Check if the file exists and serve it if so
            try:
                with open(filename, 'rb') as file:  # Open the file in binary mode to read
                    content = file.read()
                    # Send a 200 OK response with SVG content type and length headers
                    self.send_response(200)
                    self.send_header('Content-type', 'image/svg+xml')
                    self.send_header('Content-length', len(content))
                    self.end_headers()
                    # Write the SVG content to the response body
                    self.wfile.write(content)
            except FileNotFoundError:
                # If the SVG file is not found, send a 404 response
                self.send_error(404, "File not found")
        else:
            # For any other requests not matching the above criteria, send a 404 Not Found response
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: %s not found" % self.path, "utf-8"))


    def do_POST(self):
        # handle post request
        # parse the URL to get the path and form data
        parsed  = urlparse(self.path);

        if parsed.path == '/display.html':

            # recieves form data supplied from shoot.html page
            form = cgi.FieldStorage( fp=self.rfile,
                                     headers=self.headers,
                                     environ = { 'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': 
                                                   self.headers['Content-Type'],
                                               } 
                                   );
            

            # deletes all of the existing table-?.svg files
            for filename in os.listdir():
                if filename.startswith("table-") and filename.endswith(".svg"):
                    os.remove(filename)  # removes all of the matching files

            # makes the table and initalize the board
            table = Physics.Table()

            # calculates the acceleration 
            pos_sb = Physics.Coordinate(float(form['sb_x'].value), float(form['sb_y'].value))
            sb = Physics.StillBall(1, pos_sb)

            pos_rb = Physics.Coordinate(float(form['rb_x'].value), float(form['rb_y'].value))
            vel_rb = Physics.Coordinate(float(form['rb_dx'].value), float(form['rb_dy'].value))

            ball_speed = math.sqrt(vel_rb.x ** 2 + vel_rb.y ** 2)

            if ball_speed > Physics.VEL_EPSILON:
                acc_rb = Physics.Coordinate((vel_rb.x) / ball_speed * Physics.DRAG, (vel_rb.y) / ball_speed * Physics.DRAG)

            rb = Physics.RollingBall(0, pos_rb, vel_rb, acc_rb)

            # adds the balls to the table
            table += sb
            table += rb

            # saves all of the table-?.svg files
            file_index = 0
            while table:
                with open("table-{}.svg".format(file_index), "w") as file:
                    # writes the SVG representation of the table to the file
                    file.write(table.svg())
                    # inside the loop set the value of table to be the return value of calling the segment method of table
                    table = table.segment()
                    # increment file index
                    file_index += 1
                

            # makes the HTML response page
            content = generate_html_response(form)

            # send response
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len( content ) );
            self.end_headers();
            self.wfile.write( bytes( content, "utf-8" ) );

        if parsed.path == '/simulate-shot':

            global initial_svg_content

            # here we extract content length from header and read POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data_str = post_data.decode('utf-8')

            # checks if the POST data is not empty and starts with string 
            if post_data_str and (post_data_str.startswith('{') or post_data_str.startswith('[')):
                # parses JSON data from POST request.
                data = json.loads(post_data)

                # here we extract velocityX and velocityY from parsed data
                velocityX = data['velocityX']
                velocityY = data['velocityY']
                print(f"Velocity X: {velocityX}, Velocity Y: {velocityY}")  # Log velocities for debugging.

                # creates a new table instance and initalize the board
                table = Table()
                cueBall = StillBall(0, Coordinate(0, 0))
                table += cueBall

                game_instance = Game(gameName="ExampleGame", player1Name="Player1", player2Name="Player2")
                game_instance.shoot("ExampleGame", "Player1", table, velocityX, velocityY)

                # Write SVG tables to files for serving
                for i, svg_table in enumerate(game_instance):
                    with open(f'table-{i}.svg', 'w') as f:
                        f.write(svg_table)

                # Respond with success message.
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({'message': 'Shot simulated successfully'})
                self.wfile.write(response.encode('utf-8'))

                # Respond back with the SVG representation, or potentially save it and respond with a link or status
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))

            else:                
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(bytes("400: Bad Request. Invalid JSON.", "utf-8"))
 
if __name__ == "__main__":

    db = Database()
    db.createDB()  
    db.setGame("SampleGame", "P1", "P2")

    table = Table()
    db.writeTable(table)

    server_address = ('localhost',int(sys.argv[1]))
    httpd = EnhancedHTTPServer(server_address, myHTTPRequestHandler, db)
    print( "Server listing in port:  ", {server_address[1]});
    httpd.serve_forever();
