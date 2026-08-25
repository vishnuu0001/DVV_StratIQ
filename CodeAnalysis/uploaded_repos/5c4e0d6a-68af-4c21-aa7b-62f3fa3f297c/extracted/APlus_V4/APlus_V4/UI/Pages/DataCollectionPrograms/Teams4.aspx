<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="Teams4.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Teams4"
    Title="My Teams" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="Table1" width="100%">
        <tr>
            <td width="20%" style="text-align: left">
                <asp:Image ID="Image2" runat="server" ImageUrl="~/Images/company_logo.png"></asp:Image>
            </td>
            <td width="60%" style="text-align: center">
                <table id="Table2" width="100%">
                    <tr>
                        <td align="center">
                            <asp:Label ID="lblTeamsListing" runat="server" Text="Teams Listing" Font-Bold="True" Font-Size="Large"></asp:Label>
                        </td>
                    </tr>
                </table>
            </td>
            <td width="20%" style="text-align: right">
                <asp:Image ID="Image1" runat="server" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </td>
        </tr>
    </table>
    <asp:Table ID="tblTeams" runat="server" Width="100%" GridLines="None" CellPadding="1"
        CellSpacing="1" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
    </asp:Table>
</asp:Content>
