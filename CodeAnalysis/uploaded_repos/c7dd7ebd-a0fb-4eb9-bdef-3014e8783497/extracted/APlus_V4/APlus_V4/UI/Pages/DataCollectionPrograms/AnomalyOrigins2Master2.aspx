<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyOrigins2Master2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyOrigins2Master2"
    Title="Anomaly Origins Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 145">
                <asp:Label ID="Label3" runat="server">Anomaly Origin 2 ID:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOrigin2ID" runat="server" CssClass="Textbox_Display" MaxLength="5"
                    Width="56px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label1" runat="server">Anomaly Origin 1:</asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlOrigin1" runat="server" CssClass="Textbox_Entry" Width="336px">
                </asp:DropDownList>
                <asp:TextBox ID="txtOrigin1" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Visible="False" Width="328px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqOrigin1" runat="server" ControlToValidate="ddlOrigin1"
                    Display="None" ErrorMessage="Select Anomaly Origin 1"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblRoute" runat="server">Anomaly Origin 2:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOrigin2" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="325px" Rows="1"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqOrigin2" runat="server" ErrorMessage="Enter Anomaly Origin 2"
                    ControlToValidate="txtOrigin2" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 153px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="OK"></asp:Button>
                </td>
                <td style="width: 153px" align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 153px" align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Normal" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
