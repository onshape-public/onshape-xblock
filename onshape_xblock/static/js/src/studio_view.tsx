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
        setTimeout(() => setDOM(), 0);
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

    loadForm((window as any).check_list_form);
}

function onFormChange(data: any) {
    $checkList.text(JSON.stringify(data.formData.check_array));
}

function loadForm(schema: any) {

    ReactDOM.render((  <Form schema={schema}
        onChange={onFormChange}>
        <div>
          <button type="submit" hidden={true}>Submit</button>
        </div>
      </Form>
    ), $form[0])
}