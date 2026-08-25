<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerPlanMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerPlanMaster1"
    Title="Master Plan Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table>
        <tr>
            <td class="style1">
                <asp:CheckBox runat="server" ID="chkShowInactive" Text="Show Inactive" />
            </td>
            <td class="style2">
                <asp:CheckBox runat="server" ID="chkShowPlan" Text="Show Plan" />
            </td>
            <td class="style2">
                <asp:Button runat="server" ID="btnApplyFilter" Text="Apply Filter" CssClass="Button_Default" />
            </td>
        </tr>
    </table>
    <hr style="width: 100%" />
    <asp:Table ID="tblMasterPlan" runat="server" Width="100%" GridLines="Both" CellPadding="2"
        CellSpacing="0" BorderColor="White" BorderWidth="1" BorderStyle="Ridge" BackColor="White">
    </asp:Table>
    <br />
    <hr style="width: 99%; color: black; height: 1px">
    <asp:Table ID="tblSiteTotals" runat="server" Width="100%" GridLines="Both" CellPadding="2"
        CellSpacing="0" BorderColor="White" BorderWidth="1" BorderStyle="Ridge" BackColor="White">
    </asp:Table>
    <br />
    <asp:Panel ID="pnlExit" runat="server">
        <table id="Table5" cellspacing="0" cellpadding="2" width="321" border="0">
            <tr>
                <td align="left" style="width: 158px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td align="left" style="width: 158px">
                    <asp:Button ID="btnAdd" runat="server" CssClass="Button_Variable" Text="New Savings Plan"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 130px;
        }
        .style2
        {
            width: 149px;
        }
    </style>
</asp:Content>
