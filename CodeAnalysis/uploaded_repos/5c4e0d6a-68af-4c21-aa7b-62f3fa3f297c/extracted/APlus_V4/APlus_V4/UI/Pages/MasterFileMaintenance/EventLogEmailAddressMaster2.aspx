<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="EventLogEmailAddressMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.EventLogEmailAddressMaster2"
    Title="EventLog Email Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label1" runat="server" CssClass="Label_Left_8PT" Text="Email Address:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEmailAddress" ReadOnly="False" MaxLength="100" CssClass="Textbox_Entry"
                    runat="server" Width="500px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqEmail" runat="server" ErrorMessage="Enter Email Address"
                    ControlToValidate="txtEmailAddress" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:RegularExpressionValidator ID="reqValidEmail" runat="server" ErrorMessage="Iinvalid Email Address"
                    ControlToValidate="txtEmailAddress" Display="None" ValidationExpression="\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*"
                    CssClass="Label_Left_8PT"></asp:RegularExpressionValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:CheckBox ID="chkEmailInactivate" runat="server" Text="Email Inactive" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
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
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
