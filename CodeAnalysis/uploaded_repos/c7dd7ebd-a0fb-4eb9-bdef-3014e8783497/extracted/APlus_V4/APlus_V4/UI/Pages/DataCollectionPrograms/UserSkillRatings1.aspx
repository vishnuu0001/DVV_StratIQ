<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserSkillRatings1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserSkillRatings1"
    Title="User Skill Ratings" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register TagPrefix="ApplicationControls" TagName="Training" Src="../../UserControls/TrainingMatrixLegend.ascx" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table>
        <tr>
            <td>
                <asp:Table ID="tblSkills" runat="server" CellPadding="0" CellSpacing="0">
                </asp:Table>
            </td>
        </tr>
        <tr>
            <td>
                <asp:CheckBox ID="ckCriteria" runat="server" Text="Show Assessment Criteria" AutoPostBack="True"
                    CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:CheckBox ID="ckShowValues" runat="server" AutoPostBack="True" Text="Show Required / Desired Values"
                    CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:CheckBox ID="ckRatingScale" runat="server" Text="Show Differences to Required / Desired"
                    AutoPostBack="True" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:CheckBox ID="ckAttachments" runat="server" AutoPostBack="True" Text="Show Skill Attachments"
                    CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
    </table>
    <ApplicationControls:Training ID="TrainingMatrixLegend1" runat="server" />
    <br />
    <table style="width: 324px">
        <tr>
            <td class="style2">
                <asp:HyperLink ID="hlAssessmentForm" runat="server" NavigateUrl="UserSkillRatings3.aspx"
                    Target="_blank" CssClass="Link_Default" Text="Assessment Form"></asp:HyperLink>
            </td>
            <td>
                <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="UserSkillRatings4.aspx"
                    CssClass="Link_Default" Text="Printer Friendly Version"></asp:HyperLink>
            </td>
        </tr>
    </table>
    <br />
    <table id="Table3">
        <tr>
            <td class="style2">
                <asp:Button ID="btnExit" runat="server" Text="Exit" CssClass="Button_Default" CausesValidation="False">
                </asp:Button>
            </td>
            <td>
                <asp:Button ID="btnAddUser" runat="server" CausesValidation="False" CssClass="Button_Variable"
                    Text="Add / Remove Users"></asp:Button>
            </td>
        </tr>
    </table>
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        #Table3
        {
            width: 324px;
        }
        .style2
        {
            width: 150px;
        }
    </style>
</asp:Content>
