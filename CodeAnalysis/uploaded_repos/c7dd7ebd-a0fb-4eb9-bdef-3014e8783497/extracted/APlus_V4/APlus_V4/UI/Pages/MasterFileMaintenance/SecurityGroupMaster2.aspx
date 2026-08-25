<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SecurityGroupMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.SecurityGroupMaster2"
    Title="Security Group Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="Table1" class="Table_Default">
        <tr>
            <td style="width: 90px">
                <asp:Label ID="Label1" runat="server" Text="Security Group ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSecurityGroupID" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    ReadOnly="True" Width="85px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 90px">
                <asp:Label ID="Label2" runat="server" Text="Security Group:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSecurityGroup" runat="server" Width="160px" MaxLength="10" CssClass="Textbox_Entry_UpperCase"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqSecurityGroup" runat="server" Display="None" ControlToValidate="txtSecurityGroup"
                    ErrorMessage="Enter a Security Group" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
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
    <uc1:TransactionHistory ID="TransactionHistory" runat="server" InitialStateExpanded="False"
        TableName="SecurityGroupMaster" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
