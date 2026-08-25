<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserMaster4.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserMaster4"
    Title="Change User Password" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 97px">
                <asp:Label ID="Label1" runat="server" CssClass="Label_Left_8PT" Text="User Name:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlUserID" runat="server" Width="236px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <asp:CheckBox ID="chkAllUsers" runat="server" Text="All Users in Working Site" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 97px">
                <asp:Label ID="lblNewPwd" runat="server" EnableViewState="False" CssClass="Label_Left_8PT"
                    Text="New Password:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPassword" runat="server" Width="128px" CssClass="Textbox_Entry"
                    MaxLength="10" TextMode="Password"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqNewPwd" runat="server" Display="None" ControlToValidate="txtPassword"
                    ErrorMessage="Enter a new password" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 97px">
                <asp:Label ID="lblConfPwd" runat="server" EnableViewState="False" CssClass="Label_Left_8PT"
                    Text="Confirm Password:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPassword2" AccessKey="1" runat="server" Width="128px" CssClass="Textbox_Entry"
                    MaxLength="10" TextMode="Password"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqConfNewPwd" runat="server" Display="None" ControlToValidate="txtPassword2"
                    ErrorMessage="Confirm the password" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <table id="Table4" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False"
                    CausesValidation="True"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                    EnableViewState="False" CausesValidation="False"></asp:Button>
            </td>
        </tr>
    </table>
    <asp:ValidationSummary ID="Validationsummary1" runat="server" CssClass="Label_Left_8PT"
        ShowSummary="False" ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
