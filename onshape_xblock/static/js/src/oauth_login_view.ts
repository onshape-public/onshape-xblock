import {log} from "./student_view";
var $ = (<any>window).$;

class OAuthBlock {

    private runtime: any;
    private element: any;
    private init_args: any;

    static makeOauthBlock(runtime: any, element: any, init_args: object){
        let myOauth = new OAuthBlock(runtime, element, init_args);
        setTimeout(() => myOauth.send_url(), 3);
        return myOauth;
    }

    constructor (runtime: any, element: any, init_args: object) {
        log.info("At the entry point for the oauth login view.");
        this.runtime = runtime;
        this.element = element;
        this.init_args = init_args;
    }

    send_url(){
        var handlerUrl = this.runtime.handlerUrl(this.element, 'finish_oauth_authorization');
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({authorization_code_url: window.location.href}),
            success: () => window.close()
        });
    }

}

(<any>window).makeOauthBlock = OAuthBlock.makeOauthBlock;
(<any>window).studentId = "student_1";