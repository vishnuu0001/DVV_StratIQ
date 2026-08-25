<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserSkillRatings2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserSkillRatings2"
    Title="User Skill Ratings" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc2" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register TagPrefix="ApplicationControls" TagName="Training" Src="../../UserControls/TrainingMatrixLegend.ascx" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default">
        <tr>
            <td align="left" style="width: 100px">
                <asp:Label ID="lblUser" runat="server" Font-Bold="True" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 110px">
                <asp:Label ID="Label1" runat="server" CssClass="Label_Left_8PT" Text="New Evaluation Date:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEvaluationDate" runat="server" CssClass="Textbox_Entry" Width="96px"
                    MaxLength="12"></asp:TextBox>
                <cc2:CalendarExtender ID="txtEvaluationDate_CalendarExtender" runat="server" PopupButtonID="imgEvaluationDate"
                    TargetControlID="txtEvaluationDate" CssClass="APlus_Calendar">
                </cc2:CalendarExtender>
                <asp:ImageButton ID="imgEvaluationDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqValueDateTime" runat="server" Display="None" ControlToValidate="txtEvaluationDate"
                    ErrorMessage="Enter a Value Date" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <asp:Table ID="tblSkills" CellSpacing="0" CellPadding="0" runat="server">
    </asp:Table>
    <br />
    <asp:CheckBox ID="ckCriteria" runat="server" AutoPostBack="True" Text="Show Assessment Criteria"
        Checked="True" CssClass="Checkbox_Default"></asp:CheckBox><br />
    <asp:CheckBox ID="ckShowValues" runat="server" Text="Show Required / Desired Values"
        AutoPostBack="True" CssClass="Checkbox_Default"></asp:CheckBox><br />
    <ApplicationControls:Training ID="TrainingMatrixLegend1" runat="server" />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
