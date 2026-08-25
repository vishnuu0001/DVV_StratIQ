<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="CalendarEvents3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.CalendarEvents3"
    Title="Calendar Event" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/CommonFunctions.js"></script>
    <table width="100%" runat="server" id="Table1" class="Table_Default">
        <tr>
            <td style="width: 20%; text-align: left;">
                <asp:Image ID="Image1" runat="server" ImageUrl="~/Images/header_logo.gif"></asp:Image>
            </td>
            <td style="text-align: center; width: 60%">
                <asp:Label ID="Label1" runat="server" CssClass="EnvironmentMessage" Text="Calendar Event"></asp:Label>
            </td>
            <td style="text-align: right; width: 20%">
                <asp:Image ID="Image4" runat="server" ImageUrl="~/images/ApplicationLogo.jpg"></asp:Image>
            </td>
        </tr>
    </table>
    <table id="Table3" runat="server" style="width: 584px; height: 140px" class="Table_Default">
        <tr>
            <td style="width: 133px; height: 15px">
                <asp:Label ID="Label2" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 15px">
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="232px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="Label3" runat="server" Text="Event Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEventType" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="232px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Event:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEvent" runat="server" CssClass="Textbox_Display" MaxLength="15"
                    Width="175px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="lblAttribute1" runat="server" Text="Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDate" runat="server" CssClass="Textbox_Display" MaxLength="12"
                    Width="150px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="Label4" runat="server" Text="Time:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTime" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="100px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="lblRoute" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDescription" runat="server" CssClass="Textbox_Display" MaxLength="100"
                    Width="325px" TextMode="MultiLine" Rows="1"></asp:TextBox>
            </td>
        </tr>
    </table>
    <p>
    </p>
    <asp:Panel ID="Panel1" runat="server" HorizontalAlign="Left">
        <asp:Label ID="lblPrintDate" runat="server"></asp:Label>
    </asp:Panel>
</asp:Content>
