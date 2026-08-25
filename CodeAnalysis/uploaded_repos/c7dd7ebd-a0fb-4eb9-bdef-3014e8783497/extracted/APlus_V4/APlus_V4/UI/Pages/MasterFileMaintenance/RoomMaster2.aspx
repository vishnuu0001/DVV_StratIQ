<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RoomMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RoomMaster2"
    Title="Room Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 150px">
                <asp:Label ID="Label2" runat="server" Text="Room ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRoomID" runat="server" MaxLength="10" ReadOnly="True" CssClass="Textbox_Display"
                    Width="48px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="Label1" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" MaxLength="50" ReadOnly="True" CssClass="Textbox_Display"
                    Width="216px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Room:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRoom" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="216px"></asp:TextBox><asp:RequiredFieldValidator ID="reqRoom" runat="server"
                        Display="None" ControlToValidate="txtRoom" ErrorMessage="Enter Conference Room"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="Label3" runat="server" Text="Sequence:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRoomSequence" runat="server" Width="40px" CssClass="Textbox_Entry"
                    MaxLength="50"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSequence" runat="server" ErrorMessage="Enter Sequence"
                    ControlToValidate="txtRoomSequence" Display="None"></asp:RequiredFieldValidator>
                <asp:CompareValidator ID="reqValidSequence" runat="server" ErrorMessage="Invalid Sequence"
                    ControlToValidate="txtRoomSequence" Operator="DataTypeCheck" Type="Integer"></asp:CompareValidator>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
