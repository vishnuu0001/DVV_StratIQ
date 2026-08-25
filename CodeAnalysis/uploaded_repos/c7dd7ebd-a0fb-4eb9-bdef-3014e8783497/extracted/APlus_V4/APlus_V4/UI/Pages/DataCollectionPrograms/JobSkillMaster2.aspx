<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="JobSkillMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.JobSkillMaster2"
    Title="Job Skill Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="ApplicationControls" TagName="Training" Src="../../UserControls/TrainingMatrixLegend.ascx" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label7" runat="server" Text="Job:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtJob" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="313px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label2" runat="server" Text="Skill Category:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSkillCategory" runat="server" Width="313" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:RequiredFieldValidator ID="reqSkillCategory" runat="server" ControlToValidate="ddlSkillCategory"
                    ErrorMessage="Select Skill Category" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:TextBox ID="txtSkillCategory" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="313px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label1" runat="server" Text="Skill:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSkill" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="392px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSkill" runat="server" ControlToValidate="txtSkill"
                    ErrorMessage="Enter Skill" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label6" runat="server" Text="Assessment Criteria:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandCriteria" runat="server" CssClass="Textbox_Entry" MaxLength="1000"
                    Width="392px" TextMode="MultiLine" Rows="1"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label3" runat="server" Text="Sequence:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSequence" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="23px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSequence" runat="server" ControlToValidate="txtSequence"
                    ErrorMessage="Enter Sequence" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label4" runat="server" Text="Required Rating:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRequiredRating" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="23px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqRequired" runat="server" ControlToValidate="txtRequiredRating"
                    ErrorMessage="Enter Required Rating" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label5" runat="server" Text="Desired Rating:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDesiredRating" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="23px"></asp:TextBox><asp:RequiredFieldValidator ID="reqDesired" runat="server"
                        ControlToValidate="txtDesiredRating" ErrorMessage="Enter Desired Rating" Display="None"
                        CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <ApplicationControls:Training ID="TrainingMatrixLegend1" runat="server" />
    <br />
    <asp:Label ID="lblDelete" runat="server" Visible="False" Text="Removing this Job Skill will delete all User Skill Ratings that may be associates with this Job Skill"
        CssClass="Label_Left_8PT"></asp:Label><br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnAttachments2" runat="server" CssClass="Button_Variable" Text="Document Links">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnAttachments" runat="server" CssClass="Button_Variable" Text="Document Links">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
