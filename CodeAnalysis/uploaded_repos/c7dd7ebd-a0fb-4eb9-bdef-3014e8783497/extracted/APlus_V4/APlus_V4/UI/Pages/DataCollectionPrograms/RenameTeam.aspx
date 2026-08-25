<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RenameTeam.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RenameTeam"
    Title="Rename Team" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Namespace="WebApp.APlus.UI.CustomControls" TagPrefix="CC1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table cellspacing="2" cellpadding="2" border="0" class="Table_Default" id="Table1">
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblCurrentTeam" runat="server" EnableViewState="False"
                    CssClass="Label_Left_8PT" Text="Current Team:"></asp:Label>
            </td>
            <td>
                    <asp:TextBox ID="txtCurrentTeam" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                        Width="112px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblNewTeam" runat="server" EnableViewState="False"
                    CssClass="Label_Left_8PT" Text="New Team:"></asp:Label>
            </td>
            <td>
                    <asp:TextBox ID="txtTeam" runat="server" CssClass="Textbox_Entry" 
                        MaxLength="10" Width="112px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqTeam" runat="server" 
                        ControlToValidate="txtTeam" CssClass="Label_Left_8PT" Display="None" 
                        ErrorMessage="Enter New Team Name"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <br />
    <table id="Table4" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnOK" runat="server" Text="OK" CssClass="Button_Default" EnableViewState="False"
                    Visible="True" CausesValidation="True"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnCancel" runat="server" Text="Cancel" CssClass="Button_Default"
                    EnableViewState="False" Visible="True" CausesValidation="False"></asp:Button>
            </td>
        </tr>
    </table>
    <asp:ValidationSummary ID="Validationsummary1" runat="server" CssClass="Label_Left_8PT"
        DisplayMode="List" ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
