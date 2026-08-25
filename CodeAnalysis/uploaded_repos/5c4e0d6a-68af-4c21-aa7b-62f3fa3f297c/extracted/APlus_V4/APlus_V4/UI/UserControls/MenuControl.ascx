<%@ Control Language="vb" AutoEventWireup="false" CodeFile="MenuControl.ascx.vb"
    Inherits="WebApp.APlus.UI.UserControls.MenuControl" TargetSchema="http://schemas.microsoft.com/intellisense/ie5" %>

<script type="text/javascript" language="javascript">
    function fnTrapKD(btn, event) {
        if (document.all) {
            if ((event.keyCode == 13) || (event.keyCode == 27))
            { btn.click(); event.returnValue = false; event.cancel = true; event.returnValue = false; event.keyCode = 0; }
        }
    }
</script>

<asp:Table ID="tblContainer" runat="server">
</asp:Table>
<br />
<asp:Table runat="server" ID="tblOption" CellSpacing="1" CellPadding="1" BorderWidth="0">
    <asp:TableRow>
        <asp:TableCell>
            <asp:Label ID="lblOption" runat="server" CssClass="Label_Left_8PT">Option:</asp:Label>
        </asp:TableCell>
        <asp:TableCell Width="50">
            <asp:TextBox ID="txtOption" TabIndex="-1" runat="server" EnableViewState="False"
                Width="40px" MaxLength="5" CssClass="Textbox_Entry"></asp:TextBox>
        </asp:TableCell>
        <asp:TableCell>
            <asp:Button ID="btnOK" TabIndex="-1" runat="server" EnableViewState="False" CssClass="Button_Default"
                Text="OK"></asp:Button>
        </asp:TableCell>
    </asp:TableRow>
</asp:Table>
