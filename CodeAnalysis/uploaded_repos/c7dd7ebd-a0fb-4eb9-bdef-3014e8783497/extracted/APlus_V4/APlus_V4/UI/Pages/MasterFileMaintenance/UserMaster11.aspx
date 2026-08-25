<%@ Page Language="vb" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="~/UI/Pages/MasterFileMaintenance/UserMaster11.aspx.vb"
    Inherits="WebApp.APlus.UI.Pages.UserMaster11" Title="User Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 130px">
                <asp:Label ID="lblUserName" runat="server" CssClass="Label_Left_8PT" Text="User ID:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUserID" runat="server" Width="176px" MaxLength="15" CssClass="Textbox_Entry_UpperCase"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUserID" runat="server" Display="None" ControlToValidate="txtUserID"
                    ErrorMessage="Enter a User Name" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label1" runat="server" CssClass="Label_Left_8PT" Text="Password:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPwd" runat="server" CssClass="Textbox_Entry" Width="175" TextMode="Password"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnUserMaster" runat="server" CssClass="Button_Default" Text="User Master"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
