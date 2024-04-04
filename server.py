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

instance_table = Physics.Table() # creates an instance of table
svg_creation = instance_table.setup_pool_table() # sets up the pool table

# define global variable for players names and game name 
player1_name = ''
player2_name = ''
game_name = ''
current_player = ''

# here we have an HTTP server that includes a connection to the database
class EnhancedHTTPServer(HTTPServer):
    # initializes the server with an address, request handler class, and database connection
    def __init__(self, server_address, RequestHandlerClass, db):
        super().__init__(server_address, RequestHandlerClass)  # initializes the parent class
        self.db = db  # here we store the database connection in the server instance

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        parsed = urlparse(self.path)

        if parsed.path.startswith('/'):
            filepath = '.' + self.path  # Assuming files are served from the current directory
            if os.path.isfile(filepath):
                # here we determine the file's MIME type and serve it
                mimetype, _ = mimetypes.guess_type(filepath)
                try:
                    with open(filepath, 'rb') as file:
                        content = file.read().decode('utf-8')
                    
                    svg_content = svg_creation.svg()
                    # Replace the placeholder for SVG content with the actual SVG string
                    content = content.replace('<!-- SVG_CONTENT -->', svg_content)

                    # here we add the current player's name to the content
                    if current_player is player1_name:
                        current = player2_name
                    elif current_player == player2_name:
                        current = player1_name
                    else:
                        current = player1_name

                    content += f"currentPlayerName = '{current}'"

                    self.send_response(200)
                    self.send_header('Content-type', mimetype or 'application/octet-stream')
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                except FileNotFoundError:
                    self.send_error(404, 'File Not Found: %s' % self.path)
                
        elif parsed.path.endswith(".js"):
            try:
                with open('.' + self.path, 'rb') as file:
                    content = file.read()
                self.send_response(200)
                self.send_header("Content-type", "application/javascript")
                self.send_header("Content-length", len(content))
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404, 'File Not Found: %s' % self.path)

        elif parsed.path.startswith('/table-') and parsed.path.endswith('.svg'):
            # Serve SVG files
            table_file = parsed.path[1:]
            #print(table_file)
            if os.path.exists(table_file):
                with open(table_file, 'rb') as file:
                    content = file.read()
                    #print("CONTENT: ", str(content))
                self.send_response(200)
                self.send_header('Content-type', 'image/svg+xml')
                self.end_headers()
                self.wfile.write(content);
                
            else:
                self.send_error(404, 'File Not Found: %s' % self.path)


        else:
            # generate 404 for GET requests that aren't the 3 files above
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) );


    def do_POST(self):
        
        # define global variables to hold player names and the game name
        global player1_name, player2_name, game_name, svg_creation, html_content

        # parse the URL to get data
        parsed_url = urlparse(self.path)

        # handling '/send' path for processing game actions
        if parsed_url.path == '/send':
            print("Processing /send request")

            # we retirve player names and game name from global variables
            player1Name = player1_name
            player2Name = player2_name
            gameName = game_name

            self.set_player_and_ball(player1Name, player2Name)
            
            # read POST data and convert it from JSON to Python dictionary
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = json.loads(post_data)

            # extract velocity data from parsed POST data
            velocity_x = parsed_data['velocity_x']
            velocity_y = parsed_data['velocity_y']
            print(f"Received velocity data: x = {velocity_x}, y = {velocity_y}")

            # initialize HTML content with game's layout
            html_content = "<html><head><title>Pool Game</title><link rel='stylesheet' href='style.css'>"
            html_content += "<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js'></script><script src='cueshot.js'></script></head><body>"

            # create game instance with retrieved player names and game name
            game = Physics.Game(gameName=gameName, player1Name=player1Name, player2Name=player2Name)
            
            # call the shoot function with velocity data and update the SVG representation
            svg_tables, table = game.shoot(gameName, player1Name, svg_creation, velocity_x, velocity_y)

            # update global SVG creation content
            svg_creation = table
            html_content += """<div id="svgContainer" style="position: relative;">"""

            # concatenate and embed SVG data into the HTML content
            svg_data = ''.join(svg_tables)
            html_content += f"""<input type="hidden" id="svgData" value="{svg_data}">"""
            html_content += "</div></body></html>"

            # finalize HTML content and navigate to the animation page
            self.handle_animation_request()
            print("HTML content written and navigation initiated")

        # handles '/formresponse' path for setting game setup data
        elif parsed_url.path == '/formresponse':
            print("Processing /formresponse request")

            # read and parse POST data to setup game
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = json.loads(post_data)

            # extract and store player names and game name from POST data
            player1_name = parsed_data.get('player1_name', '')
            player2_name = parsed_data.get('player2_name', '')
            game_name = parsed_data.get('game_name', '')

            print(f"Player 1 Name: {player1_name}")
            print(f"Player 2 Name: {player2_name}")
            print(f"Game Name: {game_name}")

            # respond with success message
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Success"}).encode('utf-8'))

        else:
            # handle unknown POST requests with a 404 error
            self.send_error(404, f"Could not find {self.path}")
            print(f"Request for {self.path} could not be processed")


    def handle_animation_request(self):

        global html_content

        # write the HTML content to the animate.html file
        file_path = 'animate.html'
        with open(file_path, 'w') as file:
            file.write(html_content)
        print(f"Content written to {file_path}")

        # respond to the client, indicating where to find the animation
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/animate.html')
        self.end_headers()
        self.wfile.write(f'<html><head><meta http-equiv="Refresh" content="0; url=/animate.html"></head></html>'.encode('utf-8'))


    def generate_and_serve_svg_string(self):
        svg_string = ""
        table_id = 0
        db = Physics.Database() # initalize connection to database

        try:
            # here we loop through all tables in the database and append their SVG rep
            while True:
                table = db.readTable(table_id)
                if not table:
                    break  # exit the loop if no more tables are found
                svg_string += table.svg()
                table_id += 1
        finally:
            db.close()  # ensure the database is closed even if an error occurs

        if svg_string:
            # successfully generated SVG content; serve it to the client
            self.serve_content(svg_string, content_type="image/svg+xml")
        else:
            # no SVG content found; send a 404 response
            self.send_error_response(404, "SVG content not found")

    def delete_existing_svg_files(self):
        directory = os.getcwd() # gets current working directory
        for file in os.listdir(directory):
            if file.startswith("table-") and file.endswith(".svg"):
                os.remove(os.path.join(directory, file))

    def serve_content(self, content, content_type="text/html", status_code=200):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(content)))
        self.end_headers()
        self.wfile.write(content.encode())

    # assigns players low and high
    def set_player_and_ball(self, player1_name, player2_name):
        global current_player, ball_set
        if current_player is None or current_player == player2_name:
            current_player = player1_name
            ball_set = "low"
        else:
            current_player = player2_name
            ball_set = "high"

    def send_error_response(self, code, message):
        """
        Sends an HTML error response with the specified status code and message.
        """
        error_html = f"""
        <html>
            <head>
                <title>Error {code}: {self.responses[code][0]}</title>
            </head>
            <body style="display: flex; flex-direction: column; align-items: center;
                        justify-content: center; height: 100vh; background-color: midnightblue;
                        color: white;">
                <h1>Error {code}: {self.responses[code][0]}</h1>
                <p>{message}</p>
            </body>
        </html>
        """
        self.serve_content(error_html, content_type="text/html", status_code=code)


if __name__ == "__main__":
   
    db = Database(True) # creates an instance of database
    db.createDB() # creates the database
     
    httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
    print( "Server listing in port:  ", int(sys.argv[1]));
    httpd.serve_forever();
