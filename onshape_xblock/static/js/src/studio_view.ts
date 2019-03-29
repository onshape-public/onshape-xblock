import * as $ from "jquery";
import * as React from "react";
import * as ReactDOM from "react-dom";
import Form from "react-jsonschema-form";

var $checkList;
var formListItemHtml;
var $form;

$(function ($) {

    const $editButton = $(".edit-button");

    //If this is running on the stack, look for the edit button, otherwise if in the sdk, jump straight to the function:
    if ($editButton.length) {
        $editButton.click(() => setTimeout(() => setDOM(), 8000));
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

    console.log("I'm in the setDOM function");

    const schema = {
        title: "Todo",
        type: "object",
        required: ["title"],
        properties: {
            title: {type: "string", title: "Title", default: "A new task"},
            done: {type: "boolean", title: "Done?", default: false}
        }
    };

    loadForm(schema);
}

function loadForm(schema) {
    var log = function log(type) {
        return console.log.bind(console, type);
    };

    ReactDOM.render(React.createElement(Form, {
        schema: schema,
        onChange: onFormChange,
        onSubmit: log("submitted"),
        onError: log("errors")
    }), $form[0]);
}

function onFormChange(data) {
    $checkList.text(JSON.stringify(data.formData.this_array));
}