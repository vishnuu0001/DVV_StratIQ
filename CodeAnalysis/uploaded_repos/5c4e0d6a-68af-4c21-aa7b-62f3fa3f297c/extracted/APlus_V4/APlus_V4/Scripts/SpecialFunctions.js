function AllFunctionKeysDisabled(event){if((event.keyCode>=112 && event.keyCode<=123)|| (event.keyCode==91)||(event.altKey && event.keyCode==115)||(event.keyCode==18)||(event.keyCode==93)||(event.keyCode==19)){event.cancelBubble=true; event.keyCode=0; event.returnValue=false; event.cancel=true; return false;}}
function IsBarCode(event){if((event.keyCode>=112 && event.keyCode<=113)||(event.keyCode>=115 && event.keyCode<=123)||(event.keyCode==17)||(event.keyCode==91)||(event.keyCode==18)||(event.keyCode==93)||(event.keyCode==19)){event.cancelBubble=true; event.keyCode=0; event.returnValue=false; event.cancel=true; return false;}else return true;}
function TrackKeyCount(currentcontrol,nextcontrol,maxkeycount,event)
{if(IsBarCode(event))
	{if(currentcontrol.keyCount==null) currentcontrol.keyCount=0;
		if((event.keyCode==8)||(event.keyCode==46))
		  currentcontrol.keyCount=currentcontrol.keyCount-1;
		else
		currentcontrol.keyCount=currentcontrol.keyCount+1;
		if(currentcontrol.keyCount==maxkeycount)
		{if(nextcontrol!=null) {nextcontrol.focus();}}}}					  
function ShiftFocus(currentcontrol,nextcontrol){alert(currentcontrol.value.length);}	
function TrackKeyCount1(currentcontrol,nextcontrol,maxkeycount,event){
	var sMask = "01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    var KeyTyped = String.fromCharCode(event.keyCode);
	var targ = currentcontrol;
    keyCount = targ.value.length;
    if (event.keyCode< 15)
    {return true;}
     else if (sMask.indexOf(KeyTyped.toString()) == -1) {return false;}
    keyEntered = KeyTyped;
    keyCount++;  
    if(keyCount==maxkeycount)
    {targ.value+=KeyTyped; event.cancelBubble=true; event.keyCode=0; event.returnValue=false; event.cancel=true; nextcontrol.focus();}}					  
function ForceOKClick(obj,len) {
	if((window.event.keyCode>=112 && event.keyCode<=123) 
		|| (window.event.keyCode==91) 
		|| (window.event.altKey && event.keyCode==115)
		|| (window.event.keyCode==18) 
		|| (window.event.keyCode==93)
		|| (window.event.keyCode==19)
		|| (window.event.keyCode==27)
		|| (window.event.keyCode==13)
		|| ((window.event.keyCode==9) || (window.event.keyCode==16) || (window.event.shiftKey && window.event.keyCode==9))
		|| (event.keyCode==8) 
		|| (event.keyCode==46) 
		|| (window.event.keyCode>=37 && window.event.keyCode<=40))
	{window.event.cancelBubble=true; window.event.keyCode=0; window.event.returnValue=false; window.event.cancel=true; return false;}
	if(obj.value.length ==len) document.all.btnOK.click();}
function openModalWindow() {window.showModalDialog("../Labeling/ReprintRoll.aspx","newWin","dialogHeight:400px; dialogWidth:700px; status=no; resizable=no; help: No;");}
function ErrorMessage(){
	if(document.Form1.txtError.value=='Error') 
	{alert("\n_____________________________________________\n\n" + 
	       "\	An ERROR has occured.\n"   +
		   "\n_____________________________________________\n\n" +  
		   "\     Please contact your local IT Helpdesk or\n"   +
		   "\                  your responsible Supervisor.");}}
		   
var blnSubmitted=false;
function btnOK_Click()
{if (typeof(SetInitialFocus) == 'function') SetInitialFocus();
	if(typeof(Page_ClientValidate)=='function'){
		if(typeof(Page_Validators)!='undefined')
			{if(Page_ClientValidate()){if(!blnSubmitted) {blnSubmitted=true;document.Form1.style.cursor='wait';return true;} else{return false;}}}	
			else {if(!blnSubmitted){blnSubmitted=true; document.Form1.style.cursor='wait';return true;} else{return false;}}}}