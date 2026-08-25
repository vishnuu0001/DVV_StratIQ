<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SecurityGroupProgramMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.SecurityGroupProgramMaster2"
    Title="User Security Group Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td>
                <asp:Label ID="Label1" runat="server" Text="Security Group:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSecurityGroup" runat="server" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSecurityGroup" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label2" runat="server" Text="Program:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlProgram" runat="server" CssClass="DropdownList_Entry" Width="320px">
                </asp:DropDownList>
                <asp:TextBox ID="txtProgram" runat="server" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True" Width="500px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label3" runat="server" Text="Allow Add:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowAdd" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label4" runat="server" Text="Allow Edit:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowEdit" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label5" runat="server" Text="Allow Delete:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowDelete" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
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
