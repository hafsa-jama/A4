import phylib;
import sqlite3
import os
import random
import math

################################################################################
# constants 

BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS;
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER;

HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS;
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH;
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH;

SIM_RATE = phylib.PHYLIB_SIM_RATE;
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON;

DRAG = phylib.PHYLIB_DRAG;
MAX_TIME = phylib.PHYLIB_MAX_TIME;

MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS;

FRAME_INTERVAL = 0.01;

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";
FOOTER = """</svg>\n""";

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
    ];

################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass;


################################################################################
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall;
    
    # svg method
    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (
        self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number])

        
################################################################################
class RollingBall (phylib.phylib_object):
    # constructor method
    def __init__(self, number, pos, vel, acc):
        # creates a phylib_object for a hole
        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_ROLLING_BALL,
                                      number,
                                      pos, vel, acc,
                                      0.0, 0.0)
       
        # converts the phylib_object into a rolling ball class                             
        self.__class__ = RollingBall;
    
    # svg method 
    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (
        self.obj.rolling_ball.pos.x,  self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number])

################################################################################
class Hole (phylib.phylib_object):
    # constructor method
    def __init__(self, pos):
        # converts the phylib_object into a Hole class
        phylib.phylib_object.__init__( self, 
                                           phylib.PHYLIB_HOLE,
                                           None,  
                                           pos, None, None, 
                                           0.0, 0.0)
        
        # converts the phylib_object into a Hole class
        self.__class__ = Hole
    
    # svg method 
    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (
        self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS)

################################################################################
class HCushion(phylib.phylib_object):
    # constructor method
    def __init__(self, y):
        self.pos = phylib.phylib_coord(0, y)
        
        # Initializes the superclass
        phylib.phylib_object.__init__(self,
                                      phylib.PHYLIB_HCUSHION,
                                      y,
                                      None, None, None,
                                      0.0, 0.0)
        
        self.__class__ = HCushion; 

    # svg method
    def svg(self):
        if self.obj.hcushion.y == 0:
            y = -25  
        else: 
            y = 2700
        return f'<rect width="1400" height="25" x="-25" y="{y}" fill="darkgreen" />\n'
      
################################################################################
class VCushion(phylib.phylib_object):
    # constructor method 
    def __init__ (self, x):
        self.pos = phylib.phylib_coord(x, 0)
        # creates a generic phylib_object for a vertical cushion
        phylib.phylib_object.__init__(self,
                                      phylib.PHYLIB_VCUSHION,
                                      x,
                                      None, None, None,
                                      0.0, 0.0)

        # converts the phylib_object into a VCushion class
        self.__class__ = VCushion

    def svg(self):
        if self.obj.vcushion.x == 0:
            x = -25 
        else: 
            x = 1350
        return f'<rect width="25" height="2750" x="{x}" y="-25" fill="darkgreen" />\n'

################################################################################
class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self;

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;
    
    def svg(self):
        content = [HEADER]
        for obj in self: # iterates over table
            if obj: # ib object is not none 
                output = obj.svg() # calls svg method
                content.append(output) # appends result to list
            
        content.append(FOOTER)
        return "".join(content) # puts it together into one string

    def roll( self, t ):
        new = Table();
        for ball in self:
            if isinstance( ball, RollingBall ):
            # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number,
                                        Coordinate(0,0),
                                        Coordinate(0,0),
                                        Coordinate(0,0) );
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t );
                # add ball to table
                new += new_ball;
            if isinstance( ball, StillBall ):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number,
                                      Coordinate( ball.obj.still_ball.pos.x,
                                      ball.obj.still_ball.pos.y ) );
                # add ball to table
                new += new_ball;
            # return table
        return new;

    def cueBall(self):
        for ball in self:
            if ball.type == phylib.PHYLIB_STILL_BALL and ball.obj.still_ball.number == 0:
                return ball
        return None  # if no cue ball is found

    def setup_pool_table(self):
   
        # generates a small random offset so we can vary the positions slightly
        def get_random_nudge():
            return random.uniform(-1.5, 1.5)

        # create a new table instance to populate with balls
        new_table = Table()

        # here are total # of balls
        total_balls = 15

        # arrangement of balls in rows at the start of the game
        ball_rows = [5, 4, 3, 2, 1]

        # iterate through each row in the table
        for i, row_length in enumerate(ball_rows):
            for j in range(row_length):
                # here we switch between starting pos for even/odd rows
                if i % 2 == 0:
                    x_position = TABLE_WIDTH / 2.0 - (row_length - 1) * (BALL_DIAMETER + 4.0) / 2 + j * (BALL_DIAMETER + 4.0) + get_random_nudge()
                else:
                    x_position = TABLE_WIDTH / 2.0 - j * (BALL_DIAMETER + 4.0) + (row_length - 1) * (BALL_DIAMETER + 4.0) / 2 + get_random_nudge()
                
                y_position = TABLE_WIDTH / 2.0 + i * math.sqrt(3.0) / 2.0 * (BALL_DIAMETER + 4.0) + get_random_nudge()

                # here we create a new StillBall at a calculated position
                position = Coordinate(x_position, y_position)
                colored_ball = StillBall(total_balls, position)
                new_table += colored_ball
                total_balls -= 1

        # add the cue ball
        cue_ball_position = Coordinate(TABLE_WIDTH / 2.0 + random.uniform(-3.0, 3.0), TABLE_LENGTH - TABLE_WIDTH / 2.0)
        cue_ball_velocity = Coordinate(0.0, -1000.0)  # Initial velocity of the cue ball, assuming it's hit straight on
        cue_ball_acceleration = Coordinate(0.0, 150.0)  # Assuming some initial acceleration
        cue_ball = StillBall(0, cue_ball_position)  # Using 0 as the id for the cue ball
        new_table += cue_ball

        return new_table

        
class Database:
    
    # create and open a database connection to a file 
    def __init__(self, reset=False):
        if reset == True and os.path.exists("phylib.db"):
            os.remove("phylib.db")
        self.connection = sqlite3.connect("phylib.db")

    def createDB(self):
        current = self.connection.cursor()
        # create Ball table
        current.execute('''CREATE TABLE IF NOT EXISTS Ball (
                        BALLID INTEGER PRIMARY KEY AUTOINCREMENT,
                        BALLNO INTEGER NOT NULL,
                        XPOS FLOAT NOT NULL,
                        YPOS FLOAT NOT NULL,
                        XVEL FLOAT,
                        YVEL FLOAT)''')
    
        # Create TTable 
        current.execute('''CREATE TABLE IF NOT EXISTS TTable (
                        TABLEID INTEGER PRIMARY KEY AUTOINCREMENT,
                        TIME FLOAT NOT NULL)''')

        # Create BallTable
        current.execute('''CREATE TABLE IF NOT EXISTS BallTable (
                            BALLID INTEGER NOT NULL,
                            TABLEID INTEGER NOT NULL,
                            FOREIGN KEY (BALLID) REFERENCES Ball(BALLID),
                            FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID))''')
    
        # create TableShot 
        current.execute('''CREATE TABLE IF NOT EXISTS TableShot(
                            TABLEID INTEGER NOT NULL,
                            SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
                            FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID))''')

        # create Game 
        current.execute('''CREATE TABLE IF NOT EXISTS Game (
                            GAMEID INTEGER PRIMARY KEY AUTOINCREMENT,
                            GAMENAME VARCHAR(64) NOT NULL)''')

        # creates Player
        current.execute('''CREATE TABLE IF NOT EXISTS Player (
                            PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT,
                            GAMEID INTEGER,
                            PLAYERNAME VARCHAR(64) NOT NULL,
                            FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
                        )''')

        # creates Shot
        current.execute ('''CREATE TABLE IF NOT EXISTS Shot (
                            SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
                            PLAYERID INTEGER NOT NULL,
                            GAMEID INTEGER NOT NULL,
                            FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID),
                            FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
                            )''')


        # commit changes and close the connection
        current.close()
        self.connection.commit()

    def readTable(self, tableID):
        adjustedTableID = tableID + 1
        cursor = self.connection.cursor()

        try:
            # checks to see if the table ID exists in the database
            cursor.execute("SELECT COUNT(TABLEID) FROM BallTable WHERE TABLEID = ?", (adjustedTableID,))
            if cursor.fetchone()[0] == 0:
                return None # table ID does not exist
            
            # retrieves the ball information 
            balls = cursor.execute("""
                SELECT Ball.BALLID, BALLNO, XPOS, YPOS, XVEL, YVEL
                FROM BallTable
                INNER JOIN Ball ON BallTable.BALLID = Ball.BALLID
                WHERE BallTable.TABLEID = ?
            """, (adjustedTableID,)).fetchall()

            # retrieves time 
            cursor.execute("SELECT TIME FROM TTable WHERE TABLEID = ?", (adjustedTableID,))
            timeResult = cursor.fetchone()

            if not timeResult:
                return None # time not found 
            
            tableTime = timeResult[0]
            table = Table()
            table.time = tableTime
    
            # iterates through all the balls
            for ballData in balls:
                ballID, ballNo, xpos, ypos, xvel, yvel = ballData

                # if the ball is not moving - it is still
                if xvel is None and yvel is None:
                    ballObject = StillBall(ballNo, Coordinate(xpos, ypos))
                else:
                    # the ball is moving (rolling)
                    xvel = xvel or 0
                    yvel = yvel or 0
                    velocity = Coordinate(xvel, yvel)
                    velvelspeed = phylib.phylib_length(velocity)
                    drag_x, drag_y = (-xvel / velvelspeed * DRAG, -yvel / velvelspeed * DRAG) if velvelspeed != 0 else (0, 0)
                    ballObject = RollingBall(ballNo, Coordinate(xpos, ypos), velocity, Coordinate(drag_x, drag_y))

                table += ballObject # adds ball object to table

        finally:
            cursor.close() # closes connection

        # commits any changes made and returns table
        self.connection.commit()
        return table

    def writeTable(self, table):
        # starts a new connection
        current = self.connection.cursor()
        
        # inserts a new table state with its corresponding time into TTable
        current.execute("INSERT INTO TTable VALUES(NULL, ?);", (table.time,))
        
        # retrieves the ID of the new ball that was inserted
        tableID = current.lastrowid

        # iterate through each ball in table
        for object in table:

            # if the ball is a rolling ball 
            if isinstance(object, RollingBall):
                current.execute("""
                    INSERT INTO Ball
                    VALUES(NULL, ?, ?, ?, ?, ?);
                    """, (object.obj.rolling_ball.number, object.obj.rolling_ball.pos.x, object.obj.rolling_ball.pos.y, object.obj.rolling_ball.vel.x, object.obj.rolling_ball.vel.y))
                # retrieve the ID of the newly inserted ball
                ballID = current.lastrowid

                # links the newly inserted ball to BallTable
                current.execute("""
                    INSERT INTO BallTable
                    VALUES(?, ?);
                    """, (ballID, tableID))

            # if it is a still ball
            elif isinstance(object, StillBall):
                current.execute("""
                    INSERT INTO Ball
                    VALUES(NULL, ?, ?, ?, NULL, NULL);
                    """, (object.obj.still_ball.number, object.obj.still_ball.pos.x, object.obj.still_ball.pos.y))
                # retrieves the ID of the newly inserted ball
                ballID = current.lastrowid

                # links the newly inserted ball to BallTable
                current.execute("""
                    INSERT INTO BallTable
                    VALUES(?, ?);
                    """, (ballID, tableID))

        # closes and commits any changes
        current.close()
        self.connection.commit()
        
        return tableID

    def close (self):
        self.connection.commit()
        self.connection.close()

    def getGame(self, gameID):

        # opens a connection to the database
        cursor = self.connection.cursor()
        
        # fetches game name and player names based on gameID
        cursor.execute("""
            SELECT g.GAMENAME, p1.PLAYERNAME AS player1Name, p2.PLAYERNAME AS player2Name
            FROM Game g
            JOIN Player p1 ON g.GAMEID = p1.GAMEID
            JOIN Player p2 ON g.GAMEID = p2.GAMEID AND p1.PLAYERID < p2.PLAYERID
            WHERE g.GAMEID = ?
            """, (gameID,))
        
        gameDetails = cursor.fetchone()

        cursor.close()  # closes the cursor 

        # checks to see if the query returned a result
        if gameDetails is not None:
            gameName, player1Name, player2Name = gameDetails
            return gameName, player1Name, player2Name
        else:
            return None # no game is found

    def setGame(self, gameName, player1Name, player2Name):
        current = self.connection.cursor()
    
        # insert game
        current.execute("""
                        INSERT INTO Game (GAMENAME)
                        VALUES (?);
                        """, (gameName,))
        
        # gets the last row id inserted
        gameId = current.lastrowid
    
        # inserts player1
        current.execute("""
                        INSERT INTO Player (GAMEID, PLAYERNAME)
                        VALUES (?, ?);
                        """, (gameId, player1Name,))
    
        # inserts player2
        current.execute("""
                        INSERT INTO Player (GAMEID, PLAYERNAME)
                        VALUES (?, ?);
                        """, (gameId, player2Name,))
    
        
        self.connection.commit()
        current.close()    
        return gameId

    def newShot(self, playerName, table, xvel, yvel, gameId):
        current = self.connection.cursor()
    
        # gets the player id from player name
        current.execute("""
                            SELECT PLAYERID, GAMEID FROM Player
                            WHERE PLAYERNAME = ? AND GAMEID = ?;
                            """, (playerName, gameId))
        playerGame = current.fetchall()
    
        if not playerGame:
            current.close()
            return None

        # insert our shot now that we have player and game id
        current.execute("""
                        INSERT INTO Shot (PLAYERID, GAMEID)
                         VALUES (?, ?);
                        """, (playerGame[0][0], playerGame[0][1]))
        
        shotId = current.lastrowid  # get the ID of the newly inserted shot
        
        self.connection.commit()
        current.close()
    
        return shotId

    def TShot(self, tableID, shotID):
        current = self.connection.cursor()
        current.execute("""
                        INSERT OR IGNORE INTO TableShot
                        VALUES(?, ?);
                        """, (tableID, shotID))
        self.connection.commit()
        current.close()

class Game:
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        # validates input types 
        if not isinstance(gameID, (int, type(None))):
            raise TypeError("Game ID must either be an integer or None.")
        if gameID is None and not all(isinstance(name, str) for name in [gameName, player1Name, player2Name]):
            raise TypeError("Player names must all be strings.")

        # validates input combinations
        if gameID is not None and any([gameName, player1Name, player2Name]):
            raise TypeError("Error. Invalid combination of arguments")
        if gameID is None and any(name is None for name in [gameName, player1Name, player2Name]):
            raise TypeError("Error. Invalid combination of arguments")

        self.db = Database()
        self.db.createDB()

        if gameID is not None:
            gameData = self.db.getGame(gameID)
            if gameData is not None:
                self.gameID = gameID
                self.gameName, self.player1Name, self.player2Name = gameData
            else:
                raise ValueError(f"No game found with ID {gameID}")
        else:
            if None not in [gameName, player1Name, player2Name]:
                self.gameID = self.db.setGame(gameName, player1Name, player2Name)
                self.gameName = gameName
                self.player1Name = player1Name
                self.player2Name = player2Name
            else:
                raise ValueError("New game requires game name and player names")
    
    def shoot(self, gameName, playerName, table, xvel, yvel):

        db = Database() # initalizes an instance of database
        shotID = self.db.newShot(playerName, table, xvel, yvel, self.gameID)  # Log the shot in the database

        cue_ball = table.cueBall()  # find the cue ball object on the table

        if cue_ball is None:
            print("Making cue ball again.")
            # If the cue ball does not exist, recreate it at the center
            xpos = TABLE_WIDTH / 2.0 + random.uniform(-3.0, 3.0)
            ypos = TABLE_LENGTH - TABLE_WIDTH / 2.0
            pos = Coordinate(xpos, ypos)
            rb = RollingBall(0, pos, Coordinate(0.0, 0.0), Coordinate(0.0, 0.0))  # Use RollingBall or StillBall depending on your game's logic
            table += rb
            print("Cue ball returned to center.")
        else:
            # If the cue ball exists, retrieve its position
            xpos = cue_ball.obj.still_ball.pos.x
            ypos = cue_ball.obj.still_ball.pos.y

        # update the cue ball's state to a rolling ball with the given velocity
        cue_ball.type = phylib.PHYLIB_ROLLING_BALL
        
        cue_ball.obj.rolling_ball.number = 0
        
        cue_ball.obj.rolling_ball.pos.x = xpos
        cue_ball.obj.rolling_ball.pos.y = ypos
        
        cue_ball.obj.rolling_ball.vel.x = xvel
        cue_ball.obj.rolling_ball.vel.y = yvel

        # initial acceleration is zero
        xacc = 0
        yacc = 0
        
        cue_ball.obj.rolling_ball.acc.x = xacc
        cue_ball.obj.rolling_ball.acc.y = yacc

        # calculate the acceleration based on velocity and drag
        velspeed = phylib.phylib_length(Coordinate(xvel, yvel))
        if velspeed > VEL_EPSILON:
            xacc = (-(xvel) / velspeed) * DRAG
            yacc = (-(yvel) / velspeed) * DRAG

        list_svg = []  # list to store SVG representations of the table states
        segment = table  # start with the current table as the first segment

        while True:
            time = table.time  # initialize time for the current segment
            segment = table.segment()  # get the next segment from the table

            if segment:
                segment_duration = segment.time - time
                frames = int(segment_duration / FRAME_INTERVAL)  # Calculate the number of frames for this segment

                for frame_index in range(frames):
                    elapsed_time = frame_index * FRAME_INTERVAL
                    newTable = table.roll(elapsed_time)  # Calculate new table state
                    newTable.time = table.time + elapsed_time

                    # save the state of the table at this frame to the database
                    tableID = db.writeTable(newTable) + 1
                    db.TShot(tableID, shotID)
                    list_svg.append(newTable.svg())
            else:
                break  # exit the loop if no more segments are found

            table = segment  # move to the next segment

        # cue_ball_updated = table.cueBall()  # Retrieve the cue ball object from the table again
        # if cue_ball_updated:
        #     updated_xpos = cue_ball_updated.obj.rolling_ball.pos.x
        #     updated_ypos = cue_ball_updated.obj.rolling_ball.pos.y
        #     print(f"Cue ball updated position: x = {updated_xpos}, y = {updated_ypos}")
        # else:
        #     print("Cue ball not found on the table after the shot.")

        return list_svg, table
