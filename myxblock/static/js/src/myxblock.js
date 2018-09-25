/* Javascript for MyXBlock. */
function MyXBlockAside(runtime, element, block_element, init_args) {
    return new MyXBlock(runtime, element, init_args);
}

function MyXBlock(runtime, element, init_args) {
    var checkHandlerUrl = runtime.handlerUrl(element, 'check_answers');
    var saveHandlerUrl = runtime.handlerUrl(element, 'save_answers');

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
                "Your part's volume of " + data.partVolume + " is incorrect. The volume should be between " + data.minVolume + " and " + data.maxVolume
            );
        }
    }

    function updateFeedback(data) {
        var feedback_msg;
        if (data.score === null) {
            feedback_msg = '(' + data.maximum_score + ' points possible)';
        } else {
            feedback_msg = '(' + data.score + '/' + data.maximum_score + ' points)';
        }
        if (data.max_attempts) {
            feedback_msg = 'You have used ' + data.attempts + ' of ' + data.max_attempts +
                ' submissions ' + feedback_msg;
            if (data.attempts == data.max_attempts - 1) {
                $('.action .check .check-label', element).text('Final check');
            }
            else if (data.attempts >= data.max_attempts) {
                $('.action .check, .action .save', element).hide();
            }
        }
        $('.submission-feedback', element).text(feedback_msg);
    }

    function updateStatus(data) {
        updateStatusMessage(data);
        updateFeedback(data);
    }

    function callHandler(url) {
        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify({documentUrl: $('input.myxblock-documentUrl').val()}),
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
    $('.action .save', element).click(function (e) { callHandler(saveHandlerUrl); });
    updateStatus(init_args);

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
