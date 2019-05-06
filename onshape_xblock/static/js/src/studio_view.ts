import * as $ from "jquery";
import * as React from "react";
import * as ReactDOM from "react-dom";
import Form from "react-jsonschema-form";
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

let $checkList : any;
let formListItemHtml;
let $form : any;

$(function ($) {

    const $editButton = $(".edit-button");

    //If this is running on the stack, look for the edit button, otherwise if in the sdk, jump straight to the function:
    if ($editButton.length) {
        setTimeout(() => setDOM(), 8000);
    } else {
        setDOM();
    }

});

function setDOM() {
    window.requestAnimationFrame(() => _setDom());
}

function _setDom() {
        $checkList = $("#xb-field-edit-check_list");
    formListItemHtml = '<li className="field comp-setting-entry metadata_entry " data-field-name="check_list_form" >';

    $checkList.before(formListItemHtml);
    $form = $('li[data-field-name="check_list_form"]');

    $checkList.attr("readonly", "");

    console.log("The DOM is set accordingly with the react json form.");

    loadForm((<any>window).check_list_form);
}

function loadForm(schema: any) {
    var log = function log(type: any) {
        return console.log.bind(console, type);
    };

    ReactDOM.render(React.createElement(Form, {
        schema: schema,
        onChange: onFormChange,
        onSubmit: log("submitted"),
        onError: log("errors")
    }), $form[0]);
}

function onFormChange(data: any) {
    $checkList.text(JSON.stringify(data.formData.this_array));
}
