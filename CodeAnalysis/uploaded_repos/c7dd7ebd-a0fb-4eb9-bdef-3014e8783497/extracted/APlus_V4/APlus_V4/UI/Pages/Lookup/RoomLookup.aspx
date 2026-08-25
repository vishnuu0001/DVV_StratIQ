<%@ Page Language="VB" AutoEventWireup="false" CodeFile="RoomLookup.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RoomLookup" %>

<%@ Register TagPrefix="cc1" Namespace="WebApp.APlus.UI.CustomControls" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head id="Head1" runat="server">
    <link href="../../../Styles/ApplicationMasterStyles.css" type="text/css" rel="stylesheet" />

    <script type="text/javascript" language="javascript" src="../../../Scripts/CommonFunctions.js"></script>

    <title>Room Lookup</title>
    <base target="_self" />
</head>
<body>
    <form id="form1" runat="server">
    <table id="Table1">
        <tr>
            <td>
                &nbsp;
            </td>
            <td>
                &nbsp;
            </td>
        </tr>
        <tr>
            <td style="vertical-align: top" valign="top">
                <asp:Label ID="Label1" runat="server" Text="Room:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlRoomList" runat="server" Width="232px" CssClass="DropdownList_Entry"
                    Height="56px">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td>
                &nbsp;
            </td>
            <td>
                &nbsp;
            </td>
        </tr>
    </table>
    <table id="tblFunctionKeys" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" CausesValidation="False">
                </asp:Button>
            </td>
            <td>
                <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel">
                </asp:Button>
            </td>
        </tr>
    </table>
    </form>
</body>
</html>
