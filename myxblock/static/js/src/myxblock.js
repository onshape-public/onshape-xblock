/* Javascript for MyXBlock. */
function MyXBlockAside(runtime, element, block_element, init_args) {
    return new MyXBlock(runtime, element, init_args);
}

function MyXBlock(runtime, element, init_args) {
    // Call the python check_answers function when the user clicks
    var checkHandlerUrl = runtime.handlerUrl(element, 'check_answers');

    // Update the feedback for the user. If multiple checks, this will display all the check messages of the checks
    // that didn't pass.
    function updateResponseMessages(responses) {
        var $status = $('.status', element);
        var $status_message = $('.status-message', element);
        var $check_list = $('.check-list', element);
        // The correct flag is flipped when any response is marked as incorrect
        var correct_flag = true
        $check_list.empty();


        for (x in responses) {
            var response = responses[x]


            // The user has not yet answered the question
            if (response.correct==undefined){
                $status.removeClass('incorrect correct');
                $status.text('unanswered');
                $status_message.text('Please put the element url within the document url editable text box.');
            }
            // The user answered correctly
            else if (response.correct && correct_flag) {
                $status.removeClass('incorrect').addClass('correct');
                $status.text('correct');
                $status_message.text('Great job! All checks passed!');
            }
            // The user answered incorrectly
            else {
                $status.removeClass('correct').addClass('incorrect');
                $status.text('incorrect');
                $status_message.text("The following checks don't pass:")
                $check_list.append("<li>"+response.message+"</li>")
                correct_flag = false
            }
        }


    }

    // This updates the score message for the user.
    function UpdateScore(data) {
        var feedback_msg;
        if (data.score === null) {
            feedback_msg = '(' + data.max_score + ' points possible)';
        } else {
            feedback_msg = '(' + data.score + '/' + data.max_score + ' points)';
        }
        if (data.max_attempts) {

            feedback_msg = 'You have used ' + data.attempts + ' of ' + data.max_attempts +
                ' submissions. Your current answer is worth: ' + feedback_msg;

            if (data.attempts == data.max_attempts - 1) {
                $('.action .check .check-label', element).text('Final check');
            }
            else if (data.attempts >= data.max_attempts) {
                $('.action .check', element).hide();
            }
        }
        $('.submission-feedback', element).text(feedback_msg);
    }

    //data is passed in as the response from the call to check_answers
    function updateStatus(data, status, error) {
        var $status_message = $('.status-message', element);
        // Catch errors from the server
        if (status=="error"){
            $status_message.text(error)
        }
        else if ('error' in data){
            $status_message.text(data.error)
        }
        // Catch Onshape errors
        else{
            responses = data.responses
            updateResponseMessages(responses);
            UpdateScore(data);
        }
    }

    // Call the specified url with the user-specified document url.
    function callHandler(url) {
        data = {"url": $('input.myxblock-documentUrl').val()}
        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify(data),
            success: updateStatus,
            error: updateStatus
        });
    }

    function toggleHelp(e) {
        var $help_text = $('#activetable-help-text', element), visible;
        $help_text.toggle();
        visible = $help_text.is(':visible');
        $(this).text(visible ? '-help' : '+help');
        $(this).attr('aria-expanded', visible);
    }

    //Executes the method defined with the parameters defined.
    function executeMethod(method_definition, data){
        if (getAllFunctions().includes(method_definition.method_name)){
            eval(data.method_definition.method_name+"(data);")
        }
    }
    //Get all the functions defined in the window
    function getAllFunctions(){
        var allfunctions=[];
          for ( var i in window) {
        if((typeof window[i]).toString()=="function"){
            allfunctions.push(window[i].name);
          }
       }
    }

    $('#activetable-help-button', element).click(toggleHelp);
    $('.action .check', element).click(function (e) { callHandler(checkHandlerUrl); });
    updateStatus(init_args);

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
