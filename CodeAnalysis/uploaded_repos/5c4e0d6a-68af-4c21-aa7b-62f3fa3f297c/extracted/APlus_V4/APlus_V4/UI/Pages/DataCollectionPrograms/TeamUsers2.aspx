<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamUsers2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamUsers2"
    Title="Team Users" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 81px; height: 26px">
                <asp:Label ID="lblTeam" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 26px">
                <asp:TextBox ID="txtTeam" runat="server" Width="216px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px; height: 26px">
                <asp:Label ID="lblUserID" runat="server" Text="User:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 26px">
                <asp:DropDownList ID="ddlUserID" runat="server" Width="236px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtUserID" runat="server" Width="208px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUser" runat="server" Display="None" ControlToValidate="ddlUserID"
                    ErrorMessage="Select User" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                &nbsp;<asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry"
                    Width="194px" AutoPostBack="True">
                </asp:DropDownList>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
