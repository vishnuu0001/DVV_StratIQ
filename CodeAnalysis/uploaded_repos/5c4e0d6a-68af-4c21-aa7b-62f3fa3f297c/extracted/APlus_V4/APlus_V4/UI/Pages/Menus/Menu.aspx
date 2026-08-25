<%@ Page Language="vb" AutoEventWireup="false" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    CodeFile="Menu.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Menu" Title="Menu" %>

<%@ Register Src="../../UserControls/MenuControl.ascx" TagName="MenuControl" TagPrefix="uc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ContentPlaceHolderID="ContentPlaceHolder1" runat="server" Visible="true">

    <uc1:MenuControl ID="MenuControl1" runat="server" />

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

</asp:Content>
