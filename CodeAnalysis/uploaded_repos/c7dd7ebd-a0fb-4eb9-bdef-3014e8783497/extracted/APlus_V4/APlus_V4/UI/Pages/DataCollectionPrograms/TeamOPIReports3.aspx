<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIReports3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIReports3"
    Title="OPI Reports" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:GridView ID="grdReportSummary" runat="server" AutoGenerateColumns="False" Width="100%"
        SkinID="GridView">
        <Columns>
            <asp:BoundField DataField="Team" HeaderText="Team"></asp:BoundField>
            <asp:BoundField DataField="OPI" HeaderText="OPI"></asp:BoundField>
        </Columns>
    </asp:GridView>
    <br />
    <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="~/UI/Pages/DataCollectionPrograms/TeamOPIReports6.aspx"
        Text="Printer Friendly Version"></asp:HyperLink>
    <br />
    <asp:Label ID="lblNoData" runat="server" Width="100%" Visible="False" Text="No Data Available for Selected Time Frame."
        CssClass="Label_Left_8PT"></asp:Label>
    <br />
    <table id="tbButtons" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnCancel" runat="server" CausesValidation="False" Text="Exit" CssClass="Button_Default">
                </asp:Button>
            </td>
            <td>
                <asp:Button ID="btnExport" runat="server" Text="Export" CssClass="Button_Default"
                    EnableViewState="False"></asp:Button>
            </td>
        </tr>
    </table>
</asp:Content>
