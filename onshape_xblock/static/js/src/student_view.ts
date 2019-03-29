/* Javascript for Onshape_xblock. */
import * as $ from "jquery";
function MyXBlockAside(runtime, element, block_element, init_args) {
    return new OnshapeBlock(runtime, element, init_args);
}

function OnshapeBlock(runtime, element, init_args) {

    var attempts_made = init_args.attempts_made;
    var max_attempts = init_args.max_attempts;
    var current_score = init_args.current_score;
    var max_points = init_args.max_points;
    var response_list = [];
    var submitted = init_args.submitted;
    var submitted_url = init_args.submitted_url;
    var final_submission = false;

    // A message indicating that some have failed.
    var $status_message = $('#status_message', element);
    // Check button
    var $check_button = $('#check_button', element);
    // A check if all responses pass - otherwise a fail with the failures listed.
    var $status = $('#status', element);
    // A list of responses - either passed or failed with the relevant message
    var $response_list = $('#response_list', element);
    // Ex: (3/3 Attempts Made)
    var $attempt_counter = $('#attempt_counter', element);
    var $final_submit_button = $('#final_submit_button', element);
    // Ex: (5/8 points)
    var $total_points_counter = $('#total_points_counter', element);
    var $onshape_url = $('#onshape_url', element);
    var $spinner = $('#spinner', element);


    // Update the feedback for the user. If multiple checks, this will display all the check messages of the checks
    // that didn't pass.
    function updateResponseMessages() {

        // The correct flag is flipped when any response is marked as incorrect
        var correct_flag = true;
        $response_list.empty();

        //const html = "<p>TESTING</p>"
        //$response_list.append("<li>"+html+"</li>")


        for (x in response_list) {
            var response = response_list[x];

            // The user answered correctly
            if (response.passed && correct_flag) {
                $status.removeClass('incorrect').addClass('correct');
                $status.text('correct');
                $status_message.text('Great job! All checks passed!');
            }
            // The user answered incorrectly
            else if (!response.passed) {
                $status.removeClass('correct').addClass('incorrect');
                $status.text('incorrect');
                $status_message.text("The following checks don't pass:")
                $response_list.append("<li>"+response.message+"</li>")
                correct_flag = false
            }
        }


    }

    // This updates the score message for the user.
    function UpdateScore() {
        if (submitted) {
            $check_button.hide();
            $final_submit_button.hide();
            $attempt_counter.text("Your Onshape Element has been submitted")
            $onshape_url.replaceWith("<a href="+ submitted_url +">"+ submitted_url + "</a>")
        }
        var feedback_msg;
        $total_points_counter.text('(' + current_score + '/' + max_points + ' Points)');
        updateCheckButton();
    }

    function updateCheckButton() {
        if (max_attempts > 0 && !submitted) {
            attempts_msg = '('+ attempts_made + '/' + max_attempts + ' Checks Used)';
            $attempt_counter.text(attempts_msg);

            if (attempts_made == max_attempts - 1) {
                $check_button.text('Final Check');
            }
            else if (attempts_made >= max_attempts) {
                $check_button.hide();
            }

        }
    }


    function calculateCurrentScore(responseList) {
        var score = 0;
        for (x in responseList) {
            response = responseList[x];
            score = score + response.points;
        }
        return score;
    }

    //HANDLERS - below are the handler calls for various actions.

    // CHECK THE ONSHAPE ELEMENT
    $check_button.click(checkAnswer);
    // To be called when the check button is clicked
    function checkAnswer(){
        makeButtonsWait();
        url = $onshape_url[0].value;
        callHandler({url : handlerUrl("check_answers"), data:{url: url, final_submission: final_submission}, onSuccess: updateFeedback});
    }

    // FINAL SUBMISSION
    $final_submit_button.click(() => {
        final_submission=true;
        checkAnswer();
    })

    // GET HELP WITH THIS XBLOCK
    $('#activetable-help-button', element).click(toggleHelp);
    function toggleHelp(e) {
        var $help_text = $('#activetable-help-text', element), visible;
        $help_text.toggle();
        visible = $help_text.is(':visible');
        $(this).text(visible ? '-help' : '+help');
        $(this).attr('aria-expanded', visible);
    }

    //data is passed in as the response from the call to check_answers
    function updateFeedback(data, status, error) {
        bringButtonsBack();
        // Catch errors from the server
        if (status==="error"){
            $status_message.text(error)
            $status_message.color("red")
        }
        else if (data.error !== ""){
            $status_message.text(data.error)
        }
        else{
            updateFlags(data);
            updateResponseMessages();

            UpdateScore();
        }
    }

    function updateFlags(data){
        response_list = data.response_list;
        current_score = calculateCurrentScore(response_list);
        attempts_made = data.attempts_made;
        submitted = data.submitted
        submitted_url = data.submitted_url
    }

    // ----------------------- UTILITY FUNCTIONS BELOW --------------------------

    // Call the python check_answers function when the user clicks
    function handlerUrl(handlerName) {
        return runtime.handlerUrl(element, handlerName);
    }

    // Call the specified url with the user-specified document url.
    function callHandler(opts) {

        const url = opts["url"];
        let data = opts["data"];
        let onSuccess = opts["onSuccess"];
        let onFailure = opts["onFailure"];

        if (onFailure === undefined) {
            onFailure = errorPrinter
        }
        if (data === undefined) {
             $.ajax({
                type: "GET",
                url: url,
                success: onSuccess,
                error: onFailure
            });
        }
        if (data) {
             $.ajax({
                type: "POST",
                url: url,
                data: JSON.stringify(data),
                success: onSuccess,
                error: onFailure
            });
        }

    }

    function errorPrinter(e){
        console.log(e);
    }

    const waitingButtonHtml = "<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span>\n" +
            "  <span class=\"sr-only\">Loading...</span>"

    function makeButtonsWait(){
        console.log("buttons should be waiting");
        $check_button.text("");
        $check_button.prepend( waitingButtonHtml );
        $check_button.attr("disabled","");

        $final_submit_button.text("");
        $final_submit_button.prepend( waitingButtonHtml );
        $final_submit_button.attr("disabled","");

    }

    function bringButtonsBack(){
        console.log("buttons should be back!");

        $check_button.text("Check Answer");
        $check_button.removeAttr("disabled");

        $final_submit_button.text("Submit Current Answer");
        $final_submit_button.removeAttr("disabled");
    }

    $(function ($) {
        UpdateScore();
    });
}
