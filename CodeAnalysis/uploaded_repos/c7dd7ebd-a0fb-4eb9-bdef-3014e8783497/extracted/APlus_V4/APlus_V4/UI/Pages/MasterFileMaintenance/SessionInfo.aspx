<%@ Page Language="VB" AutoEventWireup="false" CodeFile="SessionInfo.aspx.vb" Inherits="WebApp.APlus.UI.Pages.SessionInfo" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>Session Information</title>

    <script type="text/javascript" language="JavaScript" src="../../../Scripts/CommonFunctions.js"></script>

    <link href="../../../Styles/ApplicationMasterStyles.css" type="text/css" rel="stylesheet" />
</head>
<body onkeydown="javascript:DisableFunctionKeys(window.event);">
    <form id="Form1" method="post" autocomplete="on" runat="server">
    <asp:Table Width="100%" runat="server" ID="tblSession" BorderWidth="3" BorderStyle="Double"
        BorderColor="#336666" BackColor="White" CellPadding="1" CellSpacing="0" GridLines="Both">
        <asp:TableRow ForeColor="White" BackColor="#336666" Font-Bold="True">
            <asp:TableCell Text="Key"></asp:TableCell>
            <asp:TableCell Text="Value"></asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    </form>
</body>
</html>
