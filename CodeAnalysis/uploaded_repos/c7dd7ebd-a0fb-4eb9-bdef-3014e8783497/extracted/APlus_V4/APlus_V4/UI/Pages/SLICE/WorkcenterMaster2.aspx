<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="WorkcenterMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.WorkcenterMaster2"
    Title="Workcenter Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px;">
                <asp:Label ID="Label1" runat="server" Text="Workcenter ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtWorkcenterID" runat="server" Width="56px" MaxLength="5" CssClass="Textbox_Display"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px;">
                <asp:Label ID="Label2" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" Width="200px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" Width="200px" MaxLength="3" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="Label3" runat="server" Text="Workcenter:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtWorkcenter" runat="server" Width="26px" MaxLength="3" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqWorkcenter" runat="server" ErrorMessage="Enter Workcenter." ControlToValidate="txtWorkcenter"
                    Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="Label4" runat="server" Text="Workcenter Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtWorkcenterDescription" runat="server" Width="577px" MaxLength="50"
                    CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator ID="reqWorkcenterDescription"
                        runat="server" ErrorMessage="Enter Workcenter Description." ControlToValidate="txtWorkcenterDescription"
                        Display="None"></asp:RequiredFieldValidator>
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
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
