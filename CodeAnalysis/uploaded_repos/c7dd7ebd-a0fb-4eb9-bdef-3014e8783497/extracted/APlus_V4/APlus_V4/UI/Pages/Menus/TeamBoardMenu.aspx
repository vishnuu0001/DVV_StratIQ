<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamBoardMenu.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamBoardMenu"
    Title="Team Board Menu" %>

<%@ Register Src="../../UserControls/MenuControl.ascx" TagName="MenuControl" TagPrefix="uc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery-ui-1.8.6.custom.min.js"></script>

    <script type="text/javascript" language="javascript">
        function TrapKeysForMenu(event) {
            if (event.keyCode == 13)
            { document.all.btnOK.click(); return true; }
            else if ((event.keyCode >= 48 && event.keyCode <= 57)
				|| (event.keyCode == 8)
				|| (event.keyCode == 46)
				|| (event.keyCode == 9)
				|| (event.keyCode >= 96 && event.keyCode <= 105)
				|| (event.keyCode >= 37 && event.keyCode <= 40)
				|| (event.keyCode == 16)
				|| (event.keyCode >= 65 && event.keyCode <= 90))

            { event.returnValue = true; return true; }
            else { event.returnValue = false; event.cancel = true; event.keyCode = 0; return false; }
        }
    </script>

    <asp:Table ID="TeamBoardTable1" Width="100%" CellPadding="0" CellSpacing="0" runat="server">
    </asp:Table>
    <div id="Lower" style="position: relative">
        <uc1:MenuControl ID="Menucontrol1" runat="server"></uc1:MenuControl>
        <asp:Image ImageUrl="~/images/trashcan-full-icon.png" ID="trashcan" runat="server"
            Height="48px" Width="48px" Style="position: absolute; right: 10px; top: 50px;" />
        <asp:HiddenField ID="actionInfo" runat="server" />
    </div>

    <script type="text/javascript">
        $(document).ready(function() {
            $("body").css("overflow-x", "hidden");
            // drag and drop
            $("#ctl00_ContentPlaceHolder1_TeamBoardTable1 a")
                .draggable({ disabled: <%= DragDisabled %>, revert: true, zIndex: 99, helper: 'clone'});

            $("#ctl00_ContentPlaceHolder1_TeamBoardTable1 span")
                .draggable({ disabled: <%= DragDisabled %>, revert: true, zIndex: 99, helper: 'clone'});

            $("#ctl00_ContentPlaceHolder1_trashcan").droppable({
                tolerance: "touch",
                drop: function(ev, ui) {
                    var promptResponse = confirm('<%= DeleteConfirmString %>');
                    if (promptResponse == false)
                        return;
                    var actionInfo = document.getElementById('ctl00_ContentPlaceHolder1_actionInfo');
                    var valueToDelete = $(ui.draggable)[0].attributes['LinkId'].value;
                    actionInfo.value = 'DELETE|' + valueToDelete;
                    __doPostBack();
                }
            });

            $("#ctl00_ContentPlaceHolder1_TeamBoardTable1 td").droppable({
                tolerance: "touch",
                drop: function(ev, ui) {
                    try {
                        // parse values
                        var linkIdFull = $(ui.draggable)[0].attributes['LinkId'].value;
                        var linkArray = linkIdFull.split("|");
                        var itemId = linkArray[0];
                        var itemRow = linkArray[1];
                        var itemCol = linkArray[2];

                        var cellInfoFull = $(this)[0].attributes('CellPosition').value;
                        cellInfoArray = cellInfoFull.split("|");
                        var cellRow = cellInfoArray[0];
                        var cellCol = cellInfoArray[1];

                        // detect drag within cell, disallow
                        if (itemRow == cellRow && itemCol == cellCol) {
                            return;
                        }
                        var promptResponse = confirm('<%= MoveConfirmString %>');
                        if (promptResponse == false)
                            return;
                        var actionInfo = document.getElementById('ctl00_ContentPlaceHolder1_actionInfo');
                        actionInfo.value = "MOVE|" + itemId + "|" + cellRow + "|" + cellCol;
                        __doPostBack();
                    }
                    catch (Error) {
                    }
                }
            });
        });
    </script>

</asp:Content>
