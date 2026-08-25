<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RouteStepsKeyActions2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RouteStepsKeyActions2"
    Title="Route Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 129px" valign="top">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Route:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRouteAbbrev" runat="server" Width="259px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 129px" valign="top">
                <asp:Label ID="lblRoute" runat="server" Text="Step Number:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtStepNumber" runat="server" Width="43px" MaxLength="4" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 129px" valign="top">
                <asp:Label ID="Label3" runat="server" Text="Key Action Number:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 15px">
                <asp:TextBox ID="txtKeyActionNumber" runat="server" Width="43px" CssClass="Textbox_Entry"
                    MaxLength="4"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqKeyActionNumber" runat="server" ErrorMessage="Enter Key Action Number"
                    ControlToValidate="txtKeyActionNumber" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 129px" valign="top">
                <asp:Label ID="lblKeyAction" runat="server" Text="Key Action:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 15px">
                <asp:TextBox ID="txtKeyAction" runat="server" Width="525px" MaxLength="100" CssClass="Textbox_Entry"
                    Height="18px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqKeyAction" runat="server" ErrorMessage="Enter Key Action"
                    ControlToValidate="txtKeyAction" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td>
            </td>
            <td>
            </td>
        </tr>
        <tr>
            <td style="width: 129px" valign="top">
                <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="RouteStepsDetail.aspx"
                    Text="Printer Friendly Version" CssClass="Link_Default"></asp:HyperLink>
            </td>
            <td style="height: 15px">
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
                <td style="width: 110px">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnTools" runat="server" CssClass="Button_Default" Text="Tools" Visible="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnToolsView" runat="server" CssClass="Button_Default" Text="Tools"
                        CausesValidation="False" Visible="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
