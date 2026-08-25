<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="JobMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.JobMaster2"
    Title="Job Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="ApplicationControls" TagName="Training" Src="../../UserControls/TrainingMatrixLegend.ascx" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table>
        <tr>
            <td valign="top">
                <asp:Label ID="lblJob" runat="server" Text="Job:" CssClass="Label_Left_8PT"></asp:Label><br />
                <asp:TextBox ID="txtJob" Width="313px" ReadOnly="True" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
            </td>
            <td valign="top">
                <asp:Label ID="Label2" runat="server" Text="Rating Type:" CssClass="Label_Left_8PT"></asp:Label><br />
                <asp:DropDownList ID="ddlRatingType" runat="server" CssClass="DropdownList_Entry"
                    Width="160px" Visible="False">
                </asp:DropDownList>
                <asp:TextBox ID="txtRatingType" runat="server" CssClass="Textbox_Display" Width="161px"
                    MaxLength="50" ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqRatingType" runat="server" Display="None" ErrorMessage="Select Rating Type"
                    ControlToValidate="ddlRatingType" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
            <td valign="top">
                <asp:Label ID="lblTeam" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label><br />
                <asp:DropDownList ID="ddlTeam" runat="server" Width="313" CssClass="DropdownList_Entry"
                    Visible="False">
                </asp:DropDownList>
                <asp:TextBox ID="txtTeam" Width="313px" ReadOnly="True" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
            </td>
            <td valign="bottom" align="right">
                <asp:Button ID="btnEdit" runat="server" CssClass="Button_Default" Text="Edit Job"
                    Visible="False"></asp:Button>
            </td>
        </tr>
    </table>
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
                    Checked="True" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:CheckBox ID="ckShowValues" runat="server" AutoPostBack="True" Text="Show Required / Desired Values"
                    Checked="True" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:CheckBox ID="ckAttachments" runat="server" AutoPostBack="True" Text="Show Skill Attachments"
                    Checked="True" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
    </table>
    <ApplicationControls:Training ID="TrainingMatrixLegend" runat="server"></ApplicationControls:Training>
    <br />
    <asp:HyperLink ID="hlAssessmentForm" runat="server" NavigateUrl="UserSkillRatings3.aspx"
        Target="_blank" Text="Assessment Form"></asp:HyperLink><br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnJobSkills" runat="server" CssClass="Button_Variable" Text="Job Skills"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
