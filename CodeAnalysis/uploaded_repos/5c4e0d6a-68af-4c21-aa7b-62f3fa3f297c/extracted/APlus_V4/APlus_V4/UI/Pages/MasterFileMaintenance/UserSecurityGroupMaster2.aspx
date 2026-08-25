<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserSecurityGroupMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserSecurityGroupMaster2"
    Title="User Security Group Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 79px">
                <asp:Label ID="Label1" runat="server" Text="User Name:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlUserID" runat="server" CssClass="DropdownList_Entry" Width="240px">
                </asp:DropDownList>
                <asp:TextBox ID="txtUserID" runat="server" MaxLength="15" CssClass="Textbox_Display"
                    ReadOnly="True" Width="240px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUser" runat="server" ErrorMessage="Select User"
                    ControlToValidate="ddlUserID" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 79px">
                <asp:Label ID="Label2" runat="server" Text="Security Group:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSecurityGroup" runat="server" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSecurityGroup" runat="server" MaxLength="10" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSecurityGroup" runat="server" ErrorMessage="Select Security Group"
                    ControlToValidate="ddlSecurityGroup" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
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
                <td align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory" runat="server" InitialStateExpanded="False"
        TableName="UserSecurityGroupMaster" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
