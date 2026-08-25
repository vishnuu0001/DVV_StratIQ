<%@ Page Language="VB" AutoEventWireup="false" CodeFile="WebReportPrintPreview.aspx.vb"
    Inherits="WebApp.APlus.UI.Pages.WebReportPrintPreview" %>

<%@ Register Assembly="Microsoft.ReportViewer.WebForms, Version=10.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a"
    Namespace="Microsoft.Reporting.WebForms" TagPrefix="rsweb" %>
<html xmlns="http://www.w3.org/1999/xhtml">
<head id="Head1" runat="server">
    <link href="../../../Styles/ApplicationMasterStyles.css" type="text/css" rel="stylesheet" />
    <title>Report Viewer</title>
</head>
<body style="margin: 5px 5px 10px 5px">
    <form id="form1" runat="server">
    <asp:ScriptManager ID="ScriptManager1" runat="server" EnableScriptGlobalization="True">
    </asp:ScriptManager>
    <table style="width: 100%; height: 100%">
        <tr>
            <td style="vertical-align: top; height: 100%">
                <rsweb:ReportViewer ID="ReportViewer1" runat="server" Style="width: 100%; height: 100%;">
                </rsweb:ReportViewer>
            </td>
        </tr>
        <tr>
            <td style="height: 25">
                <asp:Button ID="btnExit" runat="server" CausesValidation="False" Text="Exit" CssClass="Button_Default">
                </asp:Button>
            </td>
        </tr>
    </table>
    </form>
</body>
</html>
