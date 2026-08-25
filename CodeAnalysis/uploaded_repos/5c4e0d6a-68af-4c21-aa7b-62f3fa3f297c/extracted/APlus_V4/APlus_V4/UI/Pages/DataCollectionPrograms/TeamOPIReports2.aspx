<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIReports2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIReports2"
    Title="OPI Reports" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ Register TagPrefix="uc1" TagName="TeamOPIGraph" Src="../../UserControls/TeamOPIGraph.ascx" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table align="center">
        <tr>
            <td>
                <uc1:TeamOPIGraph ID="TeamOPIGraph1" runat="server" />
            </td>
        </tr>
    </table>
    <table width="100%">
        <tr>
            <td align="right">
                <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="~/UI/Pages/DataCollectionPrograms/TeamOPIReports4.aspx"
                    Text="Printer Friendly Version"></asp:HyperLink>
            </td>
            <td align="right" width="25%">
                <asp:HyperLink ID="lnkCostBenefit" runat="server" NavigateUrl="~/UI/Pages/DataCollectionPrograms/TeamOPIReports5.aspx"
                    Target="_blank" Text="Cost Benefit Printer Friendly Version"></asp:HyperLink>
            </td>
        </tr>
    </table>
    <table id="tbButtons" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnCancel" runat="server" CausesValidation="False" Text="Exit" CssClass="Button_Default">
                </asp:Button>
            </td>
            <td style="width: 130px">
                <asp:Button ID="btnTeamOPI" runat="server" CssClass="Button_Variable" Text="Team OPI Maintenance"
                    CausesValidation="False"></asp:Button>
            </td>
            <td style="width: 130px">
                <asp:Button ID="btnDataEntry" runat="server" CssClass="Button_Variable" Text="Team OPI Data Entry"
                    EnableViewState="False"></asp:Button>
            </td>
            <td style="width: 130px">
                <asp:Button ID="btnControlLimits" runat="server" CssClass="Button_Variable" Text="Team OPI Control Limits"
                    EnableViewState="False"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnTeamOPIEvents" runat="server" CssClass="Button_Variable" Text="Team OPI Events"
                    EnableViewState="False"></asp:Button>
            </td>
            <td align="left">
            </td>
        </tr>
    </table>
    <asp:GridView ID="grdReportSummary" runat="server" AutoGenerateColumns="False" SkinID="GridView"
        Width="100%" DataKeyNames="TeamID,Team,OPI,ReportPeriod">
    </asp:GridView>
    <table id="tbButtons2" class="Table_Default">
        <tr>
            <td style="text-align: right">
                <asp:Button ID="btnViewData" runat="server" Visible="False" EnableViewState="False"
                    CssClass="Button_Default" Text="View All Detail"></asp:Button>
            </td>
            <td style="text-align: right; width: 110px;">
                <asp:Button ID="btnExport" runat="server" EnableViewState="False" CssClass="Button_Default"
                    Text="Export"></asp:Button>
            </td>
        </tr>
    </table>
</asp:Content>
