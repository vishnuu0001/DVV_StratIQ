<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIValues2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIValues2"
    Title="KPI Values" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 141px;
        }
        #Table5
        {
            width: 522px;
        }
    </style>
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="False" ShowDelete="False"
        ShowEdit="False" NewLinkCaption="Savings Tracker" RedirectProgramName="KPIValues1"
        FormName="KPI Values" ProgramName="KPIValues1" CommandText="spSelKPIMasterByID"
        ProgramMode="KPIMasterMode" AlternatingRows="True" PrimaryControl="False" ShowExit="False"
        ShowExport="False" ShowRowCount="False" ShowView="False" Translate="True">
        <GridColumns>
            <CC1:MasterControlField DataField="KPI" HeaderText="KPI" />
            <CC1:MasterControlField DataField="UOM" HeaderText="UOM" />
            <CC1:MasterControlField DataField="Site" HeaderText="Site" />
            <CC1:MasterControlField DataField="TeamCategory" HeaderText="Category" />
            <CC1:MasterControlField DataField="Pillar" HeaderText="Pillar" />
            <CC1:MasterControlField DataField="BusinessArea" HeaderText="Bus Area" />
            <CC1:MasterControlField DataField="BusinessUnit" HeaderText="Bus Unit" />
            <CC1:MasterControlField DataField="Area" HeaderText="Area" />
            <CC1:MasterControlField DataField="ReportingLevelAbbrev" HeaderText="Rep Lvl" />
            <CC1:MasterControlField DataField="SummaryType" HeaderText="Summary Type" />
            <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
        </GridColumns>
    </CC1:MasterControl>
    <br />
    <br />
    <asp:Table ID="tblKPIValues" runat="server" Width="100%" GridLines="Both" CellPadding="1"
        CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
    </asp:Table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" style="width: 640px;" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 120px" align="left">
                    <p>
                        <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                            Text="OK"></asp:Button></p>
                </td>
                <td align="left" class="style1">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td align="left">
                    <asp:CheckBox ID="ckDataEntryMode" runat="server" AutoPostBack="True" 
                        Text="Data Entry Mode" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:ValidationSummary ID="Validationsummary1" runat="server" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
