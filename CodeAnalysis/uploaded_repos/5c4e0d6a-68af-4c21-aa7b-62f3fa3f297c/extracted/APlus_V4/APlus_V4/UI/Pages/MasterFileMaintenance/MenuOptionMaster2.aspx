<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MenuOptionMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MenuOptionMaster2"
    Title="Menu Option Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label1" runat="server" Text="Menu:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlMenu" runat="server" Width="325px" CssClass="DropdownList_Entry"
                    AutoPostBack="True">
                </asp:DropDownList>
                <asp:TextBox ID="txtMenu" Width="315px" ReadOnly="True" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqMenu" runat="server" ControlToValidate="ddlMenu"
                    ErrorMessage="Select a Menu" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label3" runat="server" Text="Option:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOption" Width="23px" MaxLength="2" CssClass="Textbox_Entry" runat="server"></asp:TextBox>
                <asp:CustomValidator ID="CustomValidator1" runat="server" ControlToValidate="txtOption"
                    ErrorMessage="Invalid Option" Display="None" CssClass="Label_Left_8PT"></asp:CustomValidator><asp:RequiredFieldValidator
                        ID="reqOption" runat="server" ControlToValidate="txtOption" ErrorMessage="Option cannot be blank"
                        Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label4" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDescription" Width="300px" MaxLength="50" CssClass="Textbox_Entry"
                    runat="server"></asp:TextBox><asp:RequiredFieldValidator ID="rqdDescription" runat="server"
                        ControlToValidate="txtDescription" ErrorMessage="Description cannot be blank"
                        Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label5" runat="server" Text="Program:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlProgram" runat="server" Width="500px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtProgram" Width="500px" ReadOnly="True" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
            </td>
            <td>
                or
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                Link URL:
            </td>
            <td>
                <asp:TextBox ID="txtLinkURL" runat="server" CssClass="Textbox_Entry" MaxLength="200"
                    Width="499px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label2" runat="server" Text="Program Group:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlProgramGroup" runat="server" Width="325px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtProgramGroup" Width="315px" ReadOnly="True" MaxLength="50" CssClass="Textbox_Display"
                    runat="server" Visible="False"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
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
    <uc1:TransactionHistory ID="TransactionHistory" runat="server" InitialStateExpanded="False"
        TableName="MenuOptionMaster" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
