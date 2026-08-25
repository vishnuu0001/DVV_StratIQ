<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyOrigins3Master2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyOrigins3Master2"
    Title="Anomaly Origins Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 150">
                <asp:Label ID="Label3" runat="server">Anomaly Origin 3 ID:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOrigin3ID" runat="server" CssClass="Textbox_Display" MaxLength="5"
                    Width="56px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label1" runat="server">Anomaly Origin 2:</asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlOrigin2" runat="server" CssClass="Textbox_Entry" Width="320px">
                </asp:DropDownList>
                <asp:TextBox ID="txtOrigin2" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Visible="False" Width="320px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqOrigin2" runat="server" ControlToValidate="ddlOrigin2"
                    Display="None" ErrorMessage="Select Anomaly Origin 2"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblRoute" runat="server">Anomaly Origin 3:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOrigin3" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="325px" Rows="1"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqOrigin3" runat="server" ErrorMessage="Enter Anomaly Origin 3"
                    ControlToValidate="txtOrigin3" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" cellspacing="2" cellpadding="2" width="321" border="0">
            <tr>
                <td style="width: 153px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="OK"></asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" cellspacing="2" cellpadding="2" width="321" border="0">
            <tr>
                <td align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Normal" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
