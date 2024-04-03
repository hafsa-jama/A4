// Check the current page upon window load
$(window).on('load', function() {
    if (window.location.pathname.includes("animate.html")) {
        console.log("The current page is animate.html");
        // Place actions specific to animate.html here
    } else {
        console.log("The current page is not animate.html");
    }
});

// Document ready function for handling interactions
$(document).ready(function() {
    let isDrawing = false; // Indicates if the user is currently drawing a line
    let cueBallPosition = { x: 0, y: 0 }; // Stores the center position of the cue ball

    let currentSVGIndex = 0; // Index for the current SVG being displayed
    const totalSVGs = $('#svgContainer svg').length; // Total number of SVGs in the container

    // Initial SVG display setup
    $('#svgContainer svg').hide().first().show();

    // Animation function to cycle through SVGs
    const animationInterval = setInterval(function() {
        currentSVGIndex++;
        if (currentSVGIndex >= totalSVGs) {
            clearInterval(animationInterval); // Stop the animation at the last SVG
            return;
        }
        $('#svgContainer svg').hide().eq(currentSVGIndex).show(); // Display the current SVG
    }, 100);

    // Event handler for mouse down action
    $(document).mousedown(function(event) {
        isDrawing = true;
        $('#line').show();
        updateLinePosition(event);
    });

    // Event handler for mouse up action
    $(document).mouseup(function(event) {
        if (isDrawing) {
            isDrawing = false;
            $('#line').hide(); // Hide the drawing line

            const { mouseX, mouseY } = getScaledMousePosition(event);
            const { velocityX, velocityY } = calculateVelocity(mouseX, mouseY);

            console.log(`x velocity: ${velocityX}, y velocity: ${velocityY}`);

            // Send the calculated velocity to the server
            sendVelocityToServer(velocityX, velocityY);

            // Check for animate.html content and navigate if available
            navigateToAnimateHtmlIfNeeded();
        }
    });

    // Event handler for mouse move action
    $(document).mousemove(function(event) {
        if (isDrawing) {
            updateLinePosition(event);
        }
    });

    // function to draw or update the line based on mouse movement
    function updateLinePosition(event) {
        const { mouseX, mouseY } = getScaledMousePosition(event);
        cueBallPosition = getCueBallPosition();

        // Set attributes for the line from cue ball to current mouse position
        $('#line').attr({
            'x1': cueBallPosition.x,
            'y1': cueBallPosition.y,
            'x2': mouseX,
            'y2': mouseY
        });
    }

    // function to get scaled mouse position
    function getScaledMousePosition(event) {
        return {
            mouseX: event.pageX * 2 - 25,
            mouseY: event.pageY * 2 - 25
        };
    }

    // function to calculate the initial velocity based on mouse position
    function calculateVelocity(mouseX, mouseY) {
        const dx = mouseX - cueBallPosition.x;
        const dy = mouseY - cueBallPosition.y;
        const scaleFactor = 10;
        return {
            velocityX: dx * scaleFactor,
            velocityY: dy * scaleFactor
        };
    }

    // function to send the calculated velocity to the server
    function sendVelocityToServer(velocityX, velocityY) {
        $.ajax({
            type: "POST",
            url: '/send',
            contentType: "application/json",
            data: JSON.stringify({ velocity_x: velocityX, velocity_y: velocityY }),
            success: () => console.log("Velocity sent successfully")
        });
    }

    // function to check and navigate to animate.html if available
    function navigateToAnimateHtmlIfNeeded() {
        $.ajax({
            type: "GET",
            url: 'animate.html',
            success: function(data) {
                if (data.trim().length > 0) {
                    console.log("Navigating to animate.html");
                    window.location.href = 'animate.html';
                } else {
                    console.log("animate.html is empty");
                }
            },
            error: function(xhr, status, error) {
                console.error("Error fetching animate.html:", error);
            }
        });
    }

    // function to get the current position of the cue ball
    function getCueBallPosition() {
        const cueBall = $('circle[fill="WHITE"]');
        return {
            x: parseFloat(cueBall.attr('cx')),
            y: parseFloat(cueBall.attr('cy'))
        };
    }
});
