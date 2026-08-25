<%@ Page Language="VB" AutoEventWireup="false" CodeFile="Feedback.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Feedback" %>

<%@ Register TagPrefix="cc1" Namespace="WebApp.APlus.UI.CustomControls" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <link href="../../../Styles/ApplicationMasterStyles.css" type="text/css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="../../../Scripts/CommonFunctions.js"></script>
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.min.js"></script>
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <title>Feedback</title>
    <base target="_self" />
</head>
<body>
    <form id="form1" runat="server">
    <table class="Table_Default" id="Table1" style="width: 340px; height: 205px">
        <tr>
            <td>
                <asp:Label ID="Label1" runat="server" Text="Feedback:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td>
                <asp:TextBox ID="txtExpandFeedback" runat="server" TextMode="MultiLine" Height="180px"
                    Width="340px" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:RequiredFieldValidator ID="reqFeedback" runat="server" ControlToValidate="txtExpandFeedback"
        EnableClientScript="true" ErrorMessage="Enter Feedback" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
    <table class="Table_Default" id="tblSend">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnSend" runat="server" Text="Send" CssClass="Button_Default" />
            </td>
            <td style="width: 110px">
                <asp:Button ID="btnExit" runat="server" Text="Exit" CausesValidation="False" CssClass="Button_Default"
                    OnClientClick="window.close();" />
            </td>
            <td>
                <asp:CheckBoxList ID="chklstEmail" runat="server" Height="24px" Width="159px" RepeatLayout="Flow"
                    CssClass="Checkbox_Default">
                </asp:CheckBoxList>
            </td>
        </tr>
    </table>
    <cc1:ApplicationErrorControl ID="ErrorControl" runat="server">
    </cc1:ApplicationErrorControl>
    <asp:ValidationSummary ID="valErrors" runat="server" ShowSummary="False" ShowMessageBox="False"
        DisplayMode="List" CssClass="Label_Left_8PT"></asp:ValidationSummary>
    <asp:Panel ID="pnlSuccess" runat="server" EnableViewState="False" Visible="False">
        <asp:Image ID="Image1" runat="server" ImageUrl="~/images/mail_earth.gif" />
        <asp:Label ID="lblSuccess" runat="server" EnableViewState="False" ForeColor="ForestGreen"
            CssClass="Label_Left_8PT"></asp:Label>
    </asp:Panel>
    </form>
</body>
</html>
