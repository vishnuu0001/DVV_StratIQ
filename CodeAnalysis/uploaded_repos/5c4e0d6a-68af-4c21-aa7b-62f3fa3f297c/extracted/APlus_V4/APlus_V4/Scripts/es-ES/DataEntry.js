function Tab(NField, PField, event, Numbers) {
    if ((event.ctrlKey && event.keyCode == 67) || (event.ctrlKey && event.keyCode == 86)) {
        event.returnValue = true; return false;}
    if (event.keyCode == 9) { if (NField != null) { NextField(NField); } else if (NField == null) { return false; } }
    if (event.shiftKey && event.keyCode == 9) { if (PField != null) { NextField(PField); } else if (PField == null) { return false; } }
    if (event.keyCode == 13) { return true; }
    if (Numbers == 'Yes') { AllowOnlyNumbers(event); }
    else if (Numbers == 'Neg') { AllowNegativeNumbers(event); }
    else if (Numbers == 'Int') { AllowOnlyIntegers(event); }
    else if (Numbers == 'NegInt') { AllowOnlyNegIntegers(event); }
    else return false;
}
function NextField(obj) { if (obj != null) { obj.focus(); } else if (obj == null) { return false; } }
function AllowIntegers(event) {
    if ((event.shiftKey && event.keyCode >= 48 && event.keyCode <= 57))
    { event.returnValue = false; return false; }
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode == 8) || (event.keyCode == 46) || (event.keyCode == 9) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode >= 37 && event.keyCode <= 40))
    { event.returnValue = true; return true; }
    else { event.returnValue = false; return false; } 
}
function AllowNumbers(event) {
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode == 8) || (event.keyCode == 46) || (event.keyCode == 9) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode == 190) || (event.keyCode == 110) || (event.keyCode >= 37 && event.keyCode <= 40))
    { event.returnValue = true; return true; }
    else { event.returnValue = false; return false; } 
}
function DisAllowNumbers(event) {
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode == 190) || (event.keyCode == 110))
    { event.returnValue = false; return false; }
    else { event.returnValue = true; return true; } 
}
function DoNotAllowNumbers(event) {
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode == 190) || (event.keyCode == 110) || (event.keyCode >= 37 && event.keyCode <= 40))
    { event.returnValue = false; return false; }
    else { event.returnValue = true; return true; } 
}
function AllowIntegers(event) {
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode == 8) || (event.keyCode == 46) || (event.keyCode == 9) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode >= 37 && event.keyCode <= 40))
    { event.returnValue = true; return true; }
    else { event.returnValue = false; return false; } 
}
function AllowOnlyNumbers(event) {
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode == 8) || (event.keyCode == 46) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode == 188) || (event.keyCode >= 37 && event.keyCode <= 40))
    { event.returnValue = true; return true; }
    else { event.returnValue = false; return false; } 
}
function AllowOnlyIntegers(event) {
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode == 8) || (event.keyCode == 46) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode >= 37 && event.keyCode <= 40))
    { event.returnValue = true; return true; }
    else { event.returnValue = false; return false; } 
}
function AllowNegativeNumbers(event) {
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode == 8) || (event.keyCode == 46) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode == 188) || (event.keyCode >= 37 && event.keyCode <= 40) || (event.keyCode == 109) || (event.keyCode == 189))
    { event.returnValue = true; return true; }
    else { event.returnValue = false; return false; } 
}
function AllowOnlyNegIntegers(event) {
    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode == 8) || (event.keyCode == 46) || (event.keyCode >= 96 && event.keyCode <= 105) || (event.keyCode == 109) || (event.keyCode == 189) || (event.keyCode >= 37 && event.keyCode <= 40))
    { event.returnValue = true; return true; }
    else { event.returnValue = false; return false; } 
}

var field_length = 0;
function TabNext(obj, event, len, next_field) { if (event == "down") { field_length = obj.value.length; } else if (event == "up") { if (obj.value.length != field_length) { field_length = obj.value.length; if ((field_length == len) && (window.event.keyCode != 9)) { next_field.focus(); } } } }
function NextFieldOnTab(field, event) { if (event.keyCode == 9) { if (field != null) { NextField(field); } else if (field == null) { return false; } } else return false; }
function NextFieldOnKeyDownUP(DownField, event, UpField, Numbers, RightField, LeftField) {
    if (event.keyCode == 9) { event.returnValue = false; return false; }
    if (event.keyCode == 40) { if (DownField != null) { NextField(DownField); } else if (DownField == null) { return false; } }
    if (event.keyCode == 38) { if (UpField != null) { NextField(UpField); } else if (UpField == null) { return false; } }
    if (event.keyCode == 39) { if (RightField != null) { NextField(RightField); } else if (RightField == null) { return false; } }
    if (event.keyCode == 37) { if (LeftField != null) { NextField(LeftField); } else if (LeftField == null) { return false; } }
    if (Numbers == 'Yes') { AllowOnlyNumbers(event); }
    else return false;
}
function NextFieldOnKeyDownUPTab(DownField, event, UpField, Numbers) {
    if ((event.keyCode == 40) || (event.keyCode == 9)) { if (DownField != null) { NextField(DownField); } else if (DownField == null) { return false; } }
    if ((event.keyCode == 38) || (event.shiftKey && event.keyCode == 9)) { if (UpField != null) { NextField(UpField); } else if (UpField == null) { return false; } }
    if (Numbers == 'Yes') { AllowOnlyNumbers(event); }
    else return false;
}