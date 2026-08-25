<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="Routes3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Routes3"
    Title="Routes Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Label Font-Bold="True" runat="server" ID="lblRoute" Text="Route Name goes Here"></asp:Label>
    <asp:Table ID="tblRouteSteps" runat="server" Width="100%" EnableViewState="False"
        CellSpacing="0" BorderWidth="0px" CellPadding="0" BorderStyle="None">
    </asp:Table>
    <br />
    <asp:HyperLink ID="lnkPrintPage" runat="server" NavigateUrl="RouteStepsDetail.aspx"
        Target="_blank" Text="Printer Friendly Version" CssClass="Link_Default"></asp:HyperLink>
    <br />
    <asp:Panel ID="pnlExit" runat="server">
        <table id="Table3" class="Table_Default">
            <tr>
                <td align="left" colspan="3">
                    <asp:Button ID="btnExit" runat="server" CausesValidation="False" Text="Exit" CssClass="Button_Default">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
