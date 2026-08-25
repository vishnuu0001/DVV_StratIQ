<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIDailyValues1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIDailyValues1"
    Title="KPI Daily Values" %>

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
            width: 1000px;
        }
    </style>
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
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
            <CC1:MasterControlField DataField="KPIInterface" HeaderText="Interface" />
            <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
        </GridColumns>
    </CC1:MasterControl>
    <br />
    <br />
    <asp:Table ID="tblKPIValues" runat="server" Width="100%" GridLines="Both" CellPadding="1"
        CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
    </asp:Table>
    <br />
    <asp:Table ID="tblKPIDailyValues" runat="server" Width="100%" GridLines="Both" CellPadding="1"
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
                    &nbsp;
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server">
        <table id="Table5" cellspacing="0" cellpadding="2" border="0">
            <tr>
                <td align="left" style="width: 158px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td align="left" style="width: 158px">
                    <asp:Button ID="btnRunReport1" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Visible="false" Text="KPI Report 1" />
                </td>
                <td align="left" style="width: 158px">
                    <asp:Button ID="btnRunReport2" runat="server" CausesValidation="False" CssClass="Button_Variable"
                        Text="Selected Year Report" />
                </td>
                <td align="left" style="width: 158px">
                    <asp:Button ID="btnRunReport3" runat="server" CausesValidation="False" CssClass="Button_Variable"
                        Text="Prev 12 Mths Report" />
                </td>
                <td align="left" style="width: 158px">
                    <asp:Button ID="btnExport" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Export" />
                </td>
                <td align="left" style="width: 170px">
                    <asp:Button ID="btnKPIDaily" runat="server" CausesValidation="False" CssClass="Button_Variable"
                        Text="Show Monthly KPIs" />
                </td>
                <td align="left" style="width: 158px">
                    <asp:Button ID="btnKPIMaintenance" runat="server" CausesValidation="False" CssClass="Button_Variable"
                        Text="KPI Maintenance" Visible="False" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <asp:Panel runat="server" ID="pnlComments">
        <table width="100%">
            <tr>
                <td>
                    <asp:Label ID="lblComments" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Comments</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <asp:TextBox ID="txtExpandComments" runat="server" CssClass="Textbox_Display" Width="75%"
                        MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px" ReadOnly="true"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <asp:Panel runat="server" ID="pnlTeamOPI">
        <asp:Table ID="tblTeams" runat="server" Width="100%" GridLines="None" CellPadding="1"
            CellSpacing="1" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
        </asp:Table>
        <br />
        <CC1:MasterControl ID="mcTrackers" runat="server" ShowAdd="False" ShowDelete="False"
            ShowEdit="False" NewLinkCaption="Savings Tracker" RedirectProgramName="TrackerMaster2"
            FormName="Tracker Maintenance" ProgramName="TrackerMaster1" CommandText="spSelTrackersByKPI"
            ProgramMode="TrackerMode" AlternatingRows="True" PrimaryControl="False" ShowExit="False"
            ShowExport="False" ShowRowCount="False" ShowView="False" HideEmptyGrid="true"
            InitialSort="Team" InitialSortOrder="Asc" Translate="True">
            <GridColumns>
                <CC1:MasterControlField DataField="Team" HeaderText="Team" />
                <CC1:MasterControlField DataField="Tracker" HeaderText="Savings Tracker" />
                <CC1:MasterControlField DataField="Site" HeaderText="Site" />
                <CC1:MasterControlField DataField="PillarAbbrev" HeaderText="Pillar" />
                <CC1:MasterControlField DataField="BusinessAreaAbbrev" HeaderText="Bus Area" />
                <CC1:MasterControlField DataField="BusinessUnitAbbrev" HeaderText="Bus Unit" />
                <CC1:MasterControlField DataField="TrackerValueUOM" HeaderText="UOM" />
                <CC1:MasterControlField DataField="Historic" HeaderText="Historic" />
                <CC1:MasterControlField DataField="Target" HeaderText="Target" />
                <CC1:MasterControlField DataField="StartPeriod" HeaderText="Start" DataFormatString="{0:yyyy/MM/dd}" />
                <CC1:MasterControlField DataField="Active" HeaderText="Active" />
                <CC1:MasterControlField DataField="LastValueDate" HeaderText="Last Value" DataFormatString="{0:yyyy/MM/dd}" />
                <CC1:MasterControlField DataField="CurrencyAbbrev" HeaderText="Cur" />
                <CC1:MasterControlField DataField="PreviousYearSavings" HeaderText="Prev Year" DataFormatString="{0:0.00}"
                    HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                    <HeaderStyle HorizontalAlign="Right" />
                    <ItemStyle HorizontalAlign="Right" />
                </CC1:MasterControlField>
                <CC1:MasterControlField DataField="LastYearSavings" HeaderText="Last Year" DataFormatString="{0:0.00}"
                    HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                    <HeaderStyle HorizontalAlign="Right" />
                    <ItemStyle HorizontalAlign="Right" />
                </CC1:MasterControlField>
                <CC1:MasterControlField DataField="YearSavings" HeaderText="Current Year" DataFormatString="{0:0.00}"
                    HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                    <HeaderStyle HorizontalAlign="Right" />
                    <ItemStyle HorizontalAlign="Right" />
                </CC1:MasterControlField>
                <CC1:MasterControlField DataField="TotalSavings" HeaderText="Total" DataFormatString="{0:0.00}"
                    HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                    <HeaderStyle HorizontalAlign="Right" />
                    <ItemStyle HorizontalAlign="Right" />
                </CC1:MasterControlField>
            </GridColumns>
        </CC1:MasterControl>
        <br />
        <CC1:MasterControl ID="mcAnomaly" runat="server" ShowAdd="false" ShowDelete="false"
            Translate="true" ShowView="True" ShowEdit="False" NewLinkCaption="Anomaly" RedirectProgramName="AnomalyMaster2"
            FormName="Anomaly Maintenance" ProgramName="AnomalyMaster1" CommandText="spSelAnomalyMasterByKPI"
            ProgramMode="AnomalyMode" AlternatingRows="True" PrimaryControl="false" EditLabel=""
            ShowExit="False" ShowExport="False" ViewLabel="Actions" HideEmptyGrid="True">
            <GridColumns>
                <CC1:MasterControlField DataField="AnomalyID" HeaderText="ID" />
                <CC1:MasterControlField DataField="Site" HeaderText="Site" />
                <CC1:MasterControlField DataField="AnomalyType" HeaderText="Type" />
                <CC1:MasterControlField DataField="Anomaly" HeaderText="Anomaly" />
                <CC1:MasterControlField DataField="Subject" HeaderText="Description" />
                <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
                <CC1:MasterControlField DataField="Observations" HeaderText="Observations" ShowReturns="true" />
                <CC1:MasterControlField DataField="ClosedDateTime" HeaderText="Closed" />
                <CC1:MasterControlField DataField="CreatedUser" HeaderText="Created By" />
                <CC1:MasterControlField DataField="CreatedDateTime" HeaderText="Created" />
                <CC1:MasterControlField DataField="ResponsibleUserID" HeaderText="ResponsibleUserID"
                    Visible="false">
                </CC1:MasterControlField>
                <CC1:MasterControlField DataField="CreatedUserID" HeaderText="CreatedUserID" Visible="false">
                </CC1:MasterControlField>
            </GridColumns>
        </CC1:MasterControl>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="Validationsummary1" runat="server" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
