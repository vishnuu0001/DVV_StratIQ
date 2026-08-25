<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="UserSkillRatings3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserSkillRatings3"
    Title="Training Matrix" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<%@ Register TagPrefix="ApplicationControls" TagName="Training" Src="../../UserControls/TrainingMatrixLegend.ascx" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="Table1" width="100%" class="UserSkillRatings_table">
        <tr>
            <td class="UserSkillRatings_col1">
                <asp:Image ID="Image2" runat="server" ImageUrl="~/images/company_logo.png"></asp:Image>
            </td>
            <td class="UserSkillRatings_col2">
                <asp:Label ID="lblJob" runat="server" BackColor="White" Font-Bold="True" CssClass="Label_Left_10PT" Text="No Job Selected"></asp:Label>
            </td>
            <td class="UserSkillRatings_col3">
                <asp:Image ID="Image1" runat="server" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </td>
        </tr>
    </table>
    <br />
    <asp:Table ID="tblHeading" CellPadding="0" Width="100%" runat="server">
        <asp:TableRow Height="20">
            <asp:TableCell Width="112" BorderColor="black" BorderStyle="Solid" BorderWidth="1">
                <asp:Label ID="Label1" runat="server" CssClass="Label_Left_8PT" BackColor="White" Text="Employee Name:"></asp:Label>
            </asp:TableCell>
            <asp:TableCell Width="500" BorderColor="black" BorderStyle="Solid" BorderWidth="1">
                <asp:Label ID="Label5" runat="server" CssClass="Label_Left_8PT" BackColor="White"></asp:Label>
            </asp:TableCell>
            <asp:TableCell Width="36" BorderColor="black" BorderStyle="Solid" BorderWidth="1">
                <asp:Label ID="Label3" runat="server" CssClass="Label_Left_8PT" BackColor="White" Text="ID#"></asp:Label>
            </asp:TableCell>
            <asp:TableCell Width="150" BorderColor="black" BorderStyle="Solid" BorderWidth="1">
                <asp:Label ID="Label6" runat="server" CssClass="Label_Left_8PT" BackColor="White"></asp:Label>
            </asp:TableCell>
        </asp:TableRow>
        <asp:TableRow Height="20">
            <asp:TableCell Width="112" BorderColor="black" BorderStyle="Solid" BorderWidth="1">
                <asp:Label ID="Label2" runat="server" CssClass="Label_Left_8PT" BackColor="White" Text="Current Position:"></asp:Label>
            </asp:TableCell>
            <asp:TableCell Width="500" BorderColor="black" BorderStyle="Solid" BorderWidth="1">
                <asp:Label ID="Label7" runat="server" CssClass="Label_Left_8PT" BackColor="White"></asp:Label>
            </asp:TableCell>
            <asp:TableCell Width="36" BorderColor="black" BorderStyle="Solid" BorderWidth="1">
                <asp:Label ID="Label4" runat="server" CssClass="Label_Left_8PT" BackColor="White" Text="Date:"></asp:Label>
            </asp:TableCell>
            <asp:TableCell Width="150" BorderColor="black" BorderStyle="Solid" BorderWidth="1">
                <asp:Label ID="Label8" runat="server" CssClass="Label_Left_8PT" BackColor="White"></asp:Label>
            </asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    <br />
    <ApplicationControls:Training ID="TrainingMatrixLegend1" runat="server" />
    <br />
    <asp:Table ID="tblSkills" runat="server" CellPadding="0" CellSpacing="0">
    </asp:Table>
    <br />
    <br />
    <asp:Panel ID="Panel1" runat="server" HorizontalAlign="Left" >
        <asp:Label ID="lblPrintDate" runat="server" CssClass="Label_Left_8PT"></asp:Label>
    </asp:Panel>
</asp:Content>
