/* Javascript for MyXBlock. */
function MyXBlockAside(runtime, element, block_element, init_args) {
    return new MyXBlock(runtime, element, init_args);
}

function MyXBlock(runtime, element, init_args) {
    // Call the python check_answers function when the user clicks
    var checkHandlerUrl = runtime.handlerUrl(element, 'check_answers');

    // Update the feedback for the user.
    function updateResponseMessages(responses) {
        var $status = $('.status', element);
        var $status_message = $('.status-message', element);

        // The user has not yet answered the question
        if (responses) {
            $status.removeClass('incorrect correct');
            $status.text('unanswered');
            $status_message.text('Please put the element url within the document url editable text box.');
        }
        // The user answered correctly
        else if (responses.score > 0) {
            $status.removeClass('incorrect').addClass('correct');
            $status.text('correct');
            $status_message.text('Great job!');
        }
        // The user answered incorrectly
        else {
            $status.removeClass('correct').addClass('incorrect');
            $status.text('incorrect');
            $status_message.text(
                responses.responses[0].message
            );
        }
    }

    // Default update feedback function that can hide the check button. This takes a bunch of responses and provides
    //a feedback message corresponding to each response.
    function updateFeedback(data) {
        var feedback_msg;
        if (data.score === null) {
            feedback_msg = '(' + data.v.max_score + ' points possible)';
        } else {
            feedback_msg = '(' + data.score + '/' + data.v.max_score + ' points)';
        }
        if (data.v.max_attempts) {
            feedback_msg = 'You have used ' + data.appearance.attempts + ' of ' + data.appearance.max_attempts +
                ' submissions ' + feedback_msg;
            if (data.attempts == data.v.max_attempts - 1) {
                $('.action .check .check-label', element).text('Final check');
            }
            else if (data.attempts >= data.v.max_attempts) {
                $('.action .check', element).hide();
            }
        }
        $('.submission-feedback', element).text("hi there!");
    }

    //data is passed in as the response from the call to check_answers
    function updateStatus(data) {
        updateResponseMessages(data);
        // Choose the feedback method desired
        eval(data.appearance.feedback_method+"(data);")
    }

    // Call the specified url with the user-specified document url.
    function callHandler(url) {
        data = {"url": $('input.myxblock-documentUrl').val()}
        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify(data),
            success: updateStatus,
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
