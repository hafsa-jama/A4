#include "phylib.h"

/* Creates a new still ball */
phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos) 
{
    // allocates memory for new object 
    phylib_object *newObject = (phylib_object *)malloc(sizeof(phylib_object));
    
    // returns null if memory allocation fails
    if (newObject == NULL) {
        return NULL;
    }

    // set the type of the object
    newObject->type = PHYLIB_STILL_BALL;

    // initalize the still ball part of the union 
    newObject->obj.still_ball.number = number;
    newObject->obj.still_ball.pos.x = pos->x;
    newObject->obj.still_ball.pos.y = pos->y;

    // return the pointer to the new obkect
    return newObject;
}

/* Creates a new rolling ball*/
phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc )
{
    // if any input pointers are NULL 
    if (pos == NULL || vel == NULL || acc == NULL) {
        return NULL;  
    }

    // allocates memory for new rolling ball
    phylib_object *newObject = (phylib_object *)malloc(sizeof(phylib_object));
    if (newObject == NULL) {
        return NULL;
    }

    // set the type of the object
    newObject->type = PHYLIB_ROLLING_BALL;

    // initalize the rolling ball part values 
    newObject->obj.rolling_ball.number = number;
    newObject->obj.rolling_ball.pos.x = pos->x;
    newObject->obj.rolling_ball.pos.y = pos->y;

    newObject->obj.rolling_ball.vel.x = vel->x;
    newObject->obj.rolling_ball.vel.y = vel->y;

    newObject->obj.rolling_ball.acc.x = acc->x;
    newObject->obj.rolling_ball.acc.y = acc->y;

    return newObject;
}

/* Initalize a hole */
phylib_object *phylib_new_hole(phylib_coord *pos)
{
    // allocates memory for new hole
    phylib_object *newObject = (phylib_object *)malloc(sizeof(phylib_object));
    if (newObject == NULL) {
        return NULL;
    }

    // set the type of object
    newObject->type = PHYLIB_HOLE;

    newObject->obj.hole.pos.x = pos->x;
    newObject->obj.hole.pos.y = pos->y;

    return newObject;
}

/* Horizontal Cushion */
phylib_object *phylib_new_hcushion(double y)
{
     // allocates memory for new horizontal cushion
    phylib_object *newObject = (phylib_object *)malloc(sizeof(phylib_object));
    if (newObject == NULL) {
        return NULL;
    }

    newObject->type = PHYLIB_HCUSHION;
    
    newObject->obj.hcushion.y = y;

    return newObject;
}

phylib_object *phylib_new_vcushion(double x)
{
     // allocates memory for new vertical cushion
    phylib_object *newObject = (phylib_object *)malloc(sizeof(phylib_object));
    if (newObject == NULL) {
        return NULL;
    }

    // set the type of object
    newObject->type = PHYLIB_VCUSHION;
    
    newObject->obj.vcushion.x = x;

    return newObject;

}

/* Creates a new pool table*/
phylib_table *phylib_new_table(void)
{
    // allocates memory for new table
    phylib_table *newTable = (phylib_table *)malloc(sizeof(phylib_table));
    if (newTable == NULL) {
        return NULL;
    }

    newTable->time = 0.0; // sets time to 0.0

    // safety measure to ensure all object pointers are initally empty
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        newTable->object[i] = NULL;
    }

    // horizontal and vertical cushions
    newTable->object[0] = phylib_new_hcushion(0.0); // top horizontal cushion
    newTable->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH); // bottom horizontal cushion
    newTable->object[2] = phylib_new_vcushion(0.0); // left vertical cushion
    newTable->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH); // right vertical cushion

    newTable->object[4] = phylib_new_hole(&(phylib_coord){0.0, 0.0}); // top-left corner
    newTable->object[5] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_LENGTH / 2.0}); // middle left hole
    newTable->object[6] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_LENGTH}); // bottom-left corner
    newTable->object[7] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, 0.0}); // top-right corner
    newTable->object[8] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH / 2.0}); // middle right hole
    newTable->object[9] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH}); // bottom-right corner

    return newTable;
    
}


/* Creates new object and copies over contents */
void phylib_copy_object(phylib_object **dest, phylib_object **src)
{
    // checks if the source is pointing to NULL
    if (*src == NULL) {
        *dest = NULL; 
        return;
    }

    // allocates memory for a new object
    *dest = (phylib_object *)malloc(sizeof(phylib_object));
    
    // copies over the contents of the object from the location pointed to by src
    memcpy(*dest, *src, sizeof(phylib_object));
}

/* Creates a copy of an exisiting table */
phylib_table *phylib_copy_table(phylib_table *table) 
{
    
     // allocates memory for new table
    phylib_table *newTable = malloc(sizeof(phylib_table));
    if (newTable == NULL) {
        return NULL;
    }

    // copy table properties
    newTable->time = table->time;

    // initialize all object pointers to NULL
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        newTable->object[i] = NULL;
    }

    // copy each object in the table
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        phylib_copy_object(&(newTable->object[i]),&(table->object[i]));
       
    }

    return newTable;
}

void phylib_add_object(phylib_table *table, phylib_object *object)
{
    // iterates through each object until there is a NULL pointer
     for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] == NULL) {
            table->object[i] = object;  // assigns pointer to address of object
            break; // function does nothing
        }
    }
    
}

// frees the table
void phylib_free_table(phylib_table *table)
{
    // frees each object in the table
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] != NULL) {
            free(table->object[i]);
            table->object[i] = NULL;
        }
    }

    free (table); // free the whole table
}

/* Returns the difference between c1 and c2 */
phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2) 
{
    phylib_coord result;
    result.x = (c1.x - c2.x);
    result.y = (c1.y - c2.y);

    return result;
}

/* Calculates length of the vector/coordinate */
double phylib_length(phylib_coord c) {
    return sqrt((c.x * c.x) + (c.y * c.y));
}

/* Computers products between two vectors */
double phylib_dot_product(phylib_coord a, phylib_coord b)
{
    double result;
    result = (a.x * b.x) + (a.y * b.y); // dot product
    return result; 
}

/* Calculates distance between two objects */
double phylib_distance(phylib_object *obj1, phylib_object *obj2)
{
    // checks for null pointers
    if (obj1 == NULL || obj2 == NULL) {
        return -1.0; 
    }

    // checks if the first object is PHYLIB_ROLLING_BALL
    if (obj1->type != PHYLIB_ROLLING_BALL) {
        return -1.0;
    }

    // scenario 1: if obj2 is a rolling or still ball
    if (obj2->type == PHYLIB_ROLLING_BALL || obj2->type == PHYLIB_STILL_BALL) {
        double dx, dy;

        if (obj2->type == PHYLIB_ROLLING_BALL) {
            dx = obj2->obj.rolling_ball.pos.x - obj1->obj.rolling_ball.pos.x;
            dy = obj2->obj.rolling_ball.pos.y - obj1->obj.rolling_ball.pos.y;
        } else { // PHYLIB_STILL_BALL
            dx = obj2->obj.still_ball.pos.x - obj1->obj.rolling_ball.pos.x;
            dy = obj2->obj.still_ball.pos.y - obj1->obj.rolling_ball.pos.y;
        }

       // calculate distance and subtract one PHYLIB_BALL_DIAMETER
        return sqrt(dx * dx + dy * dy) - PHYLIB_BALL_DIAMETER;
    }

    // scenario 2: if obj2 is a hole
    else if (obj2->type == PHYLIB_HOLE){

        double dx = obj2->obj.hole.pos.x - obj1->obj.rolling_ball.pos.x;
        double dy = obj2->obj.hole.pos.y - obj1->obj.rolling_ball.pos.y;

        // calculate distance and subtract PHYLIB_HOLE_RADIUS
        return sqrt(dx * dx + dy * dy) - PHYLIB_HOLE_RADIUS;

    }

    // scenario 3: if obj2 is a horizontal or vertical cushion
    else if (obj2->type == PHYLIB_HCUSHION || obj2->type == PHYLIB_VCUSHION) {
        double distance;
        if (obj2->type == PHYLIB_HCUSHION) {
            // horizontal cushion
            double dy = fabs(obj1->obj.rolling_ball.pos.y - obj2->obj.hcushion.y);
            distance = dy - PHYLIB_BALL_RADIUS;
        } else {
            // vertical cushion
            double dx = fabs(obj1->obj.rolling_ball.pos.x - obj2->obj.vcushion.x);
            distance = dx - PHYLIB_BALL_RADIUS;
        }

        return distance;
    }

    // if obj2 is not any valid type
    else {
        return -1.0;
    }
} 

void phylib_roll(phylib_object *new, phylib_object *old, double time)
{
    // checks if both the new and old objects are rolling balls
    if (new->type != PHYLIB_ROLLING_BALL || old->type != PHYLIB_ROLLING_BALL) {
        return;
    } else {

        // record the old values first
        phylib_coord oldVel;
        oldVel.x = old->obj.rolling_ball.vel.x;
        oldVel.y = old->obj.rolling_ball.vel.y;
        phylib_coord oldPos;
        oldPos.x = old->obj.rolling_ball.pos.x;
        oldPos.y = old->obj.rolling_ball.pos.y;
        phylib_coord oldAcc;
        oldAcc.x = old->obj.rolling_ball.acc.x;
        oldAcc.y = old->obj.rolling_ball.acc.y;

        // calculate new velocity
        new->obj.rolling_ball.vel.x = oldVel.x + oldAcc.x * time;
        new->obj.rolling_ball.vel.y = oldVel.y + oldAcc.y * time;
        
        // calculate new position
        new->obj.rolling_ball.pos.x = oldPos.x + oldVel.x * time + 0.5 * oldAcc.x * time * time;
        new->obj.rolling_ball.pos.y = oldPos.y + oldVel.y * time + 0.5 * oldAcc.y * time * time;

        // check for sign change in x-velocity
        if (oldVel.x * new->obj.rolling_ball.vel.x < 0) {
            new->obj.rolling_ball.vel.x = 0; // sets vel to 0
            new->obj.rolling_ball.acc.x = 0; // sets acc to 0
        }

        // check for sign change in y-velocity
        if (oldVel.y * new->obj.rolling_ball.vel.y < 0) {
            new->obj.rolling_ball.vel.y = 0; // sets vel to 0
            new->obj.rolling_ball.acc.y = 0; // sets acc to 0
        }
    }
}

// Function that checks if rolling ball has stopped
unsigned char phylib_stopped(phylib_object *object)
{
    // x and y components of velocity
    double xvel = object->obj.rolling_ball.vel.x;
    double yvel = object->obj.rolling_ball.vel.y;

    // calculates the speed of ball - magnitude of velocity vector
    double speedBall = sqrt(xvel * xvel + yvel * yvel);

    // checks if speed is less than PHYLIB_VEL_EPSILON
    if (speedBall < PHYLIB_VEL_EPSILON) {
        // converts it to still ball
        object->type = PHYLIB_STILL_BALL;

        // transfer number and positions from rolling to still ball
        object->obj.still_ball.number = object->obj.rolling_ball.number;
        object->obj.still_ball.pos.x = object->obj.rolling_ball.pos.x;
        object->obj.still_ball.pos.y = object->obj.rolling_ball.pos.y;
        
        return 1;
    } else {
        return 0; // indicates ball was not converted
    }
}

void phylib_bounce(phylib_object **a, phylib_object **b) {
    // checks for NULL pointers
    if (*a == NULL || *b == NULL) {
      //  printf("One of the objects is NULL. No collision processed.\n");
        return;
    }

    // initalize variable names
    phylib_object *rollingBall = *a;
    phylib_object *otherObject = *b;

    // bounce off cushions
    if (otherObject->type == PHYLIB_HCUSHION) {
        rollingBall->obj.rolling_ball.vel.y *= -1;
        rollingBall->obj.rolling_ball.acc.y *= -1;
    } 
    
    else if (otherObject->type == PHYLIB_VCUSHION) {
        rollingBall->obj.rolling_ball.vel.x *= -1;
        rollingBall->obj.rolling_ball.acc.x *= -1;
    }

    // handle ball falling into a hole
    if (otherObject->type == PHYLIB_HOLE) {
        free(*a);
        *a = NULL;
    }

    // converts a still ball to rolling upon collision
    if (otherObject->type == PHYLIB_STILL_BALL) {
        otherObject->type = PHYLIB_ROLLING_BALL;
        otherObject->obj.rolling_ball.number = otherObject->obj.still_ball.number;
        otherObject->obj.rolling_ball.pos = otherObject->obj.still_ball.pos;
        otherObject->obj.rolling_ball.vel = (phylib_coord){0, 0};
        otherObject->obj.rolling_ball.acc = (phylib_coord){0, 0};
    }

    // collision between two rolling balls
    if (otherObject->type == PHYLIB_ROLLING_BALL) {

        phylib_coord r_ab = phylib_sub(rollingBall->obj.rolling_ball.pos, otherObject->obj.rolling_ball.pos);
        phylib_coord v_rel = phylib_sub(rollingBall->obj.rolling_ball.vel, otherObject->obj.rolling_ball.vel);

        // normalized relative position vector
        phylib_coord n = {r_ab.x / phylib_length(r_ab), r_ab.y / phylib_length(r_ab)};
        double v_rel_n = phylib_dot_product(v_rel, n);

        // update velocities after collision
        rollingBall->obj.rolling_ball.vel.x -= v_rel_n * n.x;
        rollingBall->obj.rolling_ball.vel.y -= v_rel_n * n.y;
        otherObject->obj.rolling_ball.vel.x += v_rel_n * n.x;
        otherObject->obj.rolling_ball.vel.y += v_rel_n * n.y;

        // update accelerations based on new velocities
        double rollingBallSpeed = phylib_length(rollingBall->obj.rolling_ball.vel);
        double otherObjectSpeed = phylib_length(otherObject->obj.rolling_ball.vel);

        if (rollingBallSpeed > PHYLIB_VEL_EPSILON) {
            rollingBall->obj.rolling_ball.acc.x = (-rollingBall->obj.rolling_ball.vel.x / rollingBallSpeed) * PHYLIB_DRAG;
            rollingBall->obj.rolling_ball.acc.y = (-rollingBall->obj.rolling_ball.vel.y / rollingBallSpeed) * PHYLIB_DRAG;
        }

        if (otherObjectSpeed > PHYLIB_VEL_EPSILON) {
            otherObject->obj.rolling_ball.acc.x = (-otherObject->obj.rolling_ball.vel.x / otherObjectSpeed) * PHYLIB_DRAG;
            otherObject->obj.rolling_ball.acc.y = (-otherObject->obj.rolling_ball.vel.y / otherObjectSpeed) * PHYLIB_DRAG;
        }

    }
}

// returns the number of rolling balls on the table
unsigned char phylib_rolling(phylib_table *t)
{
    unsigned char count = 0; // Initialize a counter

    // Check if the table pointer is null
    if (t == NULL) {
        return 0;
    }
    

    // Initialize a for loop to iterate through each object in the table
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        // Checks if object exists
        if (t->object[i] != NULL) {
         //   printf("Object %d exists. ", i); // Debugging statement

            // Check if it's a rolling ball
            if (t->object[i]->type == PHYLIB_ROLLING_BALL) {
                count++;
            } else {
            }
        } 
    }


    return count; // Returns total number of balls
}

phylib_table *phylib_segment(phylib_table * table) {
    
    double time = PHYLIB_SIM_RATE; // initalizes time to simulation rate
    
    // returns null if there are no rolling balls
    if (phylib_rolling(table) == 0) {
        return NULL;
    }
  
    // calls copyTable in order to copy a table
    phylib_table *copiedTable = phylib_copy_table(table);

    // simulates until max time is reached
    while (PHYLIB_MAX_TIME > time) {
        
        // updates all rolling balls on table
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
            if (copiedTable->object[i] != NULL && copiedTable->object[i]->type == PHYLIB_ROLLING_BALL){
                phylib_roll(copiedTable->object[i], table->object[i], time);
            }
        }   

            for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++) {
                if (copiedTable->object[j] != NULL && copiedTable->object[j]->type == PHYLIB_ROLLING_BALL){
                // calls stopped function to see if the rolling ball stopped 
                    if (phylib_stopped(copiedTable->object[j]) == 1){
                        copiedTable->time = copiedTable->time + time;
                        return copiedTable;
                    }
    
                    for (int k = 0; k < PHYLIB_MAX_OBJECTS; k++){
                        // loops end in case the space between balls is less than 0
                        if (copiedTable->object[k] != NULL && j != k && (0.0 > phylib_distance(copiedTable->object[j], copiedTable->object[k]))) {
                            
                            // calls bounce before returning copy of table
                            phylib_bounce(&copiedTable->object[j], &copiedTable->object[k]);
                            copiedTable->time = copiedTable->time + time;
                            return copiedTable;
                        } 
                    }   
                }
      
            }

                // increments time by PHYLIB_SIM_RATE
                time += PHYLIB_SIM_RATE;
        } 

        // updates the copy's time and returns it
        copiedTable->time = copiedTable->time + time;
        return copiedTable;
}

char *phylib_object_string(phylib_object *object)
{
    static char string[80];
    if (object==NULL)
    {
        sprintf( string, "NULL;" );
        return string;
    }

    switch (object->type)
    {
        case PHYLIB_STILL_BALL:
            sprintf(string,
                    "STILL_BALL (%d,%6.1lf,%6.1lf)",
                    object->obj.still_ball.number,
                    object->obj.still_ball.pos.x,
                    object->obj.still_ball.pos.y );
        break;

        case PHYLIB_ROLLING_BALL:
            sprintf(string,
                    "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
                    object->obj.rolling_ball.number,
                    object->obj.rolling_ball.pos.x,
                    object->obj.rolling_ball.pos.y,
                    object->obj.rolling_ball.vel.x,
                    object->obj.rolling_ball.vel.y,
                    object->obj.rolling_ball.acc.x,
                    object->obj.rolling_ball.acc.y );
        break;

        case PHYLIB_HOLE:
            sprintf( string,
                    "HOLE (%6.1lf,%6.1lf)",
                    object->obj.hole.pos.x,
                    object->obj.hole.pos.y );
        break;

        case PHYLIB_HCUSHION:
            sprintf(string,
                    "HCUSHION (%6.1lf)",
                    object->obj.hcushion.y );
        break;

        case PHYLIB_VCUSHION:
            sprintf(string,
                    "VCUSHION (%6.1lf)",
                    object->obj.vcushion.x );
            break;
    }
        return string;
}

