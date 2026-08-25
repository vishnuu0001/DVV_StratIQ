<%@ Page Language="vb" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="~/UI/Pages/DataCollectionPrograms/UserSkillRatings4.aspx.vb"
    Inherits="WebApp.APlus.UI.Pages.UserSkillRatings4" Title="Training Matrix" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register TagPrefix="ApplicationControls" TagName="Training" Src="../../UserControls/TrainingMatrixLegend.ascx" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="server"
    Visible="true">
    <table class="UserSkillRatings_table">
        <tr>
            <td class="UserSkillRatings_col1">
                <asp:Image runat="server" ID="Image2" ImageUrl="~/images/company_logo.png"></asp:Image>
            </td>
            <td class="UserSkillRatings_col2">
                <asp:Label ID="lblJob" runat="server" Font-Bold="True" BackColor="White" Font-Size="Large"
                    Text="No Job Selected" Font-Names="Tahoma, Verdana, 'Times New Roman'"></asp:Label>
            </td>
            <td class="UserSkillRatings_col3">
                <asp:Image runat="server" ID="Image1" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </td>
        </tr>
    </table>
    <br />
    <asp:Table ID="tblSkills" runat="server" CellPadding="0" CellSpacing="0">
    </asp:Table>
    <br />
    <ApplicationControls:Training ID="TrainingMatrixLegend1" runat="server" />
    <br />
    <asp:Panel ID="Panel1" runat="server" HorizontalAlign="Left">
        <asp:Label ID="lblPrintDate" runat="server" CssClass="Label_Left_8PT"></asp:Label>
    </asp:Panel>
</asp:Content>
