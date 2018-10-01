/* Javascript for MyXBlock. */
function MyXBlockAside(runtime, element, block_element, init_args) {
    return new MyXBlock(runtime, element, init_args);
}

function MyXBlock(runtime, element, init_args) {
    var checkHandlerUrl = runtime.handlerUrl(element, 'check_answers');

    function updateStatusMessage(data) {
        var $status = $('.status', element);
        var $status_message = $('.status-message', element);

        if (!data.partVolume) {
            $status.removeClass('incorrect correct');
            $status.text('unanswered');
            $status_message.text('');
        }
        else if (data.score > 0) {
            $status.removeClass('incorrect').addClass('correct');
            $status.text('correct');
            $status_message.text('Great job!');
        } else {
            $status.removeClass('correct').addClass('incorrect');
            $status.text('incorrect');
            $status_message.text(
                "Your part's of " + data.partVolume + " is incorrect. The volume should be between " + data.d.v.min + " and " + data.d.v.max
            );
        }
    }

    // Default update feedback function that can hide the check button.
    function updateFeedback(data) {
        var feedback_msg;
        if (data.score === null) {
            feedback_msg = '(' + data.v.max_score + ' points possible)';
        } else {
            feedback_msg = '(' + data.v.min + '/' + data.v.max + ' points)';
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
        $('.submission-feedback', element).text(feedback_msg);
    }

    function updateStatus(data) {
        updateStatusMessage(data);
        // Choose the feedback method desired
        eval(data.appearance.feedback_method+"(data);")
    }

    function callHandler(url) {
        data = {"documentUrl": $('input.myxblock-documentUrl').val()}
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

    $('#activetable-help-button', element).click(toggleHelp);
    $('.action .check', element).click(function (e) { callHandler(checkHandlerUrl); });
    updateStatus(init_args);

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
