import {Category,CategoryLogger,CategoryServiceFactory,CategoryConfiguration,LogLevel} from "typescript-logging";
import * as URLParse from "url-parse";
// Importing the jquery that has the hooks already defined
const $: any = (<any> window).$;

CategoryServiceFactory.setDefaultConfiguration(new CategoryConfiguration(LogLevel.Info));
export const log = new Category("service");

function MyXBlockAside(runtime: any, element: any, block_element: any, init_args: object) {
    return new OnshapeBlock(runtime, element, init_args);
}

function entry_point(runtime: any, element: any, init_args: object) {
    log.info("Entry point for the Onshape XBlock");
    return new OnshapeBlock(runtime, element, init_args);
}

$(function ($: any) {
    log.info("At the ready point");
});

export class OnshapeBlock {

    private static waitingButtonHtml = "<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span>\n" +
            "  <span class=\"sr-only\">Loading...</span>";

    protected runtime: any;
    protected element: any;

    protected attempts_made: number;
    protected max_attempts: number;
    protected current_score: number;
    protected max_points: number;
    protected response_list: Array<any>;
    protected submitted: boolean;
    protected submitted_url: String;
    protected is_final_submission: boolean;
    protected need_to_authenticate: boolean;

    protected $status_message: any;
    protected $check_button: JQuery<HTMLElement>;
    protected $status: any;
    protected $response_list: JQuery<HTMLElement>;
    protected $attempt_counter: JQuery<HTMLElement>;
    protected $final_submit_button: JQuery<HTMLElement>;
    protected $total_points_counter: JQuery<HTMLElement>;
    protected $onshape_url: any;
    protected $spinner: JQuery<HTMLElement>;

    constructor(runtime: any, element: any, init_args: any) {

        this.runtime = runtime;
        this.element = element;

        this.attempts_made = init_args.attempts_made;
        this.max_attempts = init_args.max_attempts;
        this.current_score = init_args.current_score;
        this.max_points = init_args.max_points;
        this.response_list = [];
        this.submitted = init_args.submitted;
        this.submitted_url = init_args.submitted_url;
        this.is_final_submission = false;
        this.need_to_authenticate = init_args.need_to_authenticate;

        // A message indicating that some have failed.
        this.$status_message = $('#status_message', element);
        // Check button
        this.$check_button = $('#check_button', element);
        // A check if all responses pass - otherwise a fail with the failures listed.
        this.$status = $('#status', element);
        // A list of responses - either passed or failed with the relevant message
        this.$response_list = $('#response_list', element);
        // Ex: (3/3 Attempts Made)
        this.$attempt_counter = $('#attempt_counter', element);
        this.$final_submit_button = $('#final_submit_button', element);
        // Ex: (5/8 points)
        this.$total_points_counter = $('#total_points_counter', element);
        this.$onshape_url = $('#onshape_url', element);
        this.$spinner = $('#spinner', element);

        //First check if this is an OAuth response.
        this.checkIfOauth();

        //HANDLERS - below are the handler calls for various actions.

        // CHECK THE ONSHAPE ELEMENT
        this.$check_button.click(() => this.checkAnswer());

        // FINAL SUBMISSION
        this.$final_submit_button.click(() => {
            this.is_final_submission=true;
            this.checkAnswer();
        });
        // GET HELP WITH THIS XBLOCK
        $('#activetable-help-button', element).click(() => this.toggleHelp);
    }

    checkIfOauth() {
        // Only assume this is an OAuth redirect if the block still needs authentication AND contains the code parameter
        if (window.location.href.includes("code") && this.need_to_authenticate) {
            var handlerUrl = this.runtime.handlerUrl(this.element, 'finish_oauth_authorization');
            const authUrl = window.location.href;
            $.ajax({
                type: "POST",
                url: handlerUrl,
                data: JSON.stringify({authorization_code_url: authUrl}),
                success: () => {
                    log.info("Logged in with OAuth using authorization url: " + authUrl);
                    this.continueCallAfterOAuth();
                }
            });
        }
    }

    continueCallAfterOAuth() {
        const url = new URLParse(window.location.href);
        this.submitted_url= new URLParse(window.location.href, '', true).query.state;
        log.info("Finish call after OAUth (in continueCallAfterOAuth)")
        this.checkAnswer();
    }

    // Update the feedback for the user. If multiple checks, this will display all the check messages of the checks
    // that didn't pass.
    updateResponseMessages() {

        // The correct flag is flipped when any response is marked as incorrect
        var correct_flag = true;
        this.$response_list.empty();

        for (var x in this.response_list) {
            var response = this.response_list[x];

            // The user answered correctly
            if (response.passed && correct_flag) {
                this.$status.removeClass('incorrect').addClass('correct');
                this.$status.text('correct');
                this.$status_message.text('Great job! All checks passed!');
            }
            // The user answered incorrectly
            else if (!response.passed) {
                this.$status.removeClass('correct').addClass('incorrect');
                this.$status.text('incorrect');
                this.$status_message.text("The following checks don't pass:")
                this.$response_list.append("<li>"+response.message+"</li>")
                correct_flag = false
            }
        }


    }

    // This updates the score message for the user.
    UpdateScore() {
        if (this.submitted) {
            this.$check_button.hide();
            this.$final_submit_button.hide();
            this.$attempt_counter.text("Your Onshape Element has been submitted");
            this.$onshape_url.replaceWith("<a href="+ this.submitted_url +">"+ this.submitted_url + "</a>")
        }
        var feedback_msg;
        this.$total_points_counter.text('(' + this.current_score + '/' + this.max_points + ' Points)');
        this.updateCheckButton();
    }

    updateCheckButton() {
        if (this.max_attempts > 0 && !this.submitted) {
            var attempts_msg = '('+ this.attempts_made + '/' + this.max_attempts + ' Checks Used)';
            this.$attempt_counter.text(attempts_msg);

            if (this.attempts_made == this.max_attempts - 1) {
                this.$check_button.text('Final Check');
            }
            else if (this.attempts_made >= this.max_attempts) {
                this.$check_button.hide();
            }

        }
    }


    calculateCurrentScore() {
        var score = 0;
        for (let x in this.response_list) {
            let response = this.response_list[x];
            score = score + response.points;
        }
        this.current_score = score;
        return score;
    }

    // To be called when the check button is clicked
    checkAnswer(){
        log.info("Checking the answer");
        this.makeButtonsWait();
        let url = this.$onshape_url.val();
        this.callHandler({url : this.handlerUrl("check_answers"), data:{url: url, is_final_submission: this.is_final_submission}, onSuccess: (data: any, status: any, error: any) => this.updateFeedback(data, status, error)});
    }

    toggleHelp() {
        var $help_text = $('#activetable-help-text');
        $help_text.toggle();
        let visible: boolean = $help_text.is(':visible');
        $(this).text(visible ? '-help' : '+help');
        $(this).attr('aria-expanded', ':visible');
    }

    //data is passed in as the response from the call to check_answers
    updateFeedback(data: any, status: any, error: any) {
        this.bringButtonsBack();
        // Catch errors from contacting the server
        if (status==="error"){
            this.$status_message.text(error);
            this.$status_message.color("red");
        }
        // Catch evaluation errors
        else if (data.error !== ""){
            if (data.need_to_authenticate && data.error === "OAuthNotAuthenticated") {
                this.followOAuth(data.oauthUrl);
                this.$status_message.text("Please follow the popup in order to authenticate EdX for your Onshape account then submit your answer again.");

            } else {
                this.$status_message.text(data.error);
            }
        }
        else{
            this.updateFlags(data);
            this.updateResponseMessages();
            this.UpdateScore();
        }
    }

    updateFlags(data: any){
        this.response_list = data.response_list;
        this.current_score = this.calculateCurrentScore();
        this.attempts_made = data.attempts_made;
        this.submitted = data.submitted;
        this.submitted_url = data.submitted_url;
        this.need_to_authenticate = data.need_to_authenticate;
    }

    followOAuth(url: string){
        window.location.href = url;
    }


    // Call the python check_answers function when the user clicks
    handlerUrl(handlerName: string) {
        return this.runtime.handlerUrl(this.element, handlerName);
    }

    // Call the specified url with the user-specified document url.
    callHandler(opts: any) {
        log.info("Calling the backend with opts: " + opts);

        const url = opts["url"];
        let data = opts["data"];
        let onSuccess = opts["onSuccess"];
        let onFailure = opts["onFailure"];

        if (onFailure === undefined) {
            onFailure = this.errorPrinter
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

    errorPrinter(e: string){
        console.log(e);
    }

    makeButtonsWait(){
        console.log("buttons should be waiting");
        this.$check_button.text("");
        this.$check_button.prepend( OnshapeBlock.waitingButtonHtml );
        this.$check_button.attr("disabled","");

        this.$final_submit_button.text("");
        this.$final_submit_button.prepend( OnshapeBlock.waitingButtonHtml );
        this.$final_submit_button.attr("disabled","");

    }

    bringButtonsBack(){
        console.log("buttons should be back!");

        this.$check_button.text("Check Answer");
        this.$check_button.removeAttr("disabled");

        this.$final_submit_button.text("Submit Current Answer");
        this.$final_submit_button.removeAttr("disabled");
    }
}

(<any>window).entry_point = entry_point;
