<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="QueryMaster4.aspx.vb" Inherits="WebApp.APlus.UI.Pages.QueryMaster4"
    Title="Query Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="tblParameter" class="Table_Default" runat="server">
        <tr>
            <td style="width: 150px">
            </td>
            <td>
                <asp:Label ID="lblQueryID" runat="server" Visible="False" Text="[QueryID]" CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label runat="server" ID="Label2" Text="Parameter:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtQueryParameter" runat="server" MaxLength="20" Width="150px" CssClass="Textbox_Entry"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqParameter" runat="server" ErrorMessage="Parameter is required"
                    ControlToValidate="txtQueryParameter" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="Label3" runat="server" Text="Prompt:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtParameterPrompt" runat="server" CssClass="Textbox_Entry" Width="312px"
                    MaxLength="50"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label runat="server" ID="Label1" Text="Parameter Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:RadioButtonList ID="rblParameterType" runat="server" AutoPostBack="True" RepeatDirection="Horizontal"
                    CssClass="Label_Left_8PT">
                    <asp:ListItem Value="TEXT">Text</asp:ListItem>
                    <asp:ListItem Value="TEAM">Teams</asp:ListItem>
                    <asp:ListItem Value="MYTEAMS">My Teams</asp:ListItem>
                    <asp:ListItem Value="SITE">Site</asp:ListItem>
                    <asp:ListItem Value="DATE">Date</asp:ListItem>
                </asp:RadioButtonList>
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
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
