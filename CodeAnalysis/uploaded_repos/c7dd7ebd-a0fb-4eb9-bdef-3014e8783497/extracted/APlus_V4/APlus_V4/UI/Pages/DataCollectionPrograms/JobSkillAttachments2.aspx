<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="JobSkillAttachments2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.JobSkillAttachments2"
    Title="Job Skill Documents" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label2" runat="server" Text="Skill Category:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSkillCategory" Width="313px" runat="server" CssClass="Textbox_Display"
                    MaxLength="50" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label1" runat="server" Text="Skill:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSkill" Width="313px" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label6" runat="server" Text="Document:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAttachment" runat="server" Width="392px" MaxLength="100" CssClass="Textbox_Entry"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAttachment" runat="server" ControlToValidate="txtAttachment"
                    ErrorMessage="Enter Document Name" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label3" runat="server" Text="URL:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandURL" Width="392px" MaxLength="250" CssClass="Textbox_Entry"
                    runat="server" TextMode="MultiLine"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqURL" runat="server" ControlToValidate="txtExpandURL"
                    ErrorMessage="Enter URL" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
