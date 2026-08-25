<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MyActions.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MyActions"
    Title="My Actions" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:UpdateProgress ID="UpdateProgress1" runat="server" DisplayAfter="50">
        <ProgressTemplate>
            <div style="position: absolute; z-index: 1;">
                <asp:Image runat="server" ID="imgWait" Height="48" Width="48" ImageUrl="~/images/barcircle.gif" />
                <asp:AlwaysVisibleControlExtender ID="imgWait_AlwaysVisibleControlExtender" runat="server"
                    Enabled="True" TargetControlID="imgWait" VerticalSide="Middle" HorizontalSide="Center">
                </asp:AlwaysVisibleControlExtender>
            </div>
        </ProgressTemplate>
    </asp:UpdateProgress>
    <asp:UpdatePanel ID="UpdatePanel1" runat="server">
        <ContentTemplate>
            <asp:Label ID="lblTeamActions" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Team Action Items</asp:Label>
            <CC1:MasterControl ID="mcTeamActions" runat="server" CommandText="spSelMyActionItems"
                ProgramName="MyActionItems" FormName="My Action Items" RedirectProgramName="TeamActionPlanMaintenance2"
                NewLinkCaption="" ShowView="True" ShowEdit="True" ShowDelete="False" ShowAdd="False"
                PrimaryControl="false" ProgramMode="TeamActionPlanMode" ShowExport="false" AlternatingRows="True"
                Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamID" HeaderText="TeamID" Visible="false" />
                    <CC1:MasterControlField DataField="SiteAbbrev" HeaderText="Site" />
                    <CC1:MasterControlField DataField="PillarAbbrev" HeaderText="Pillar" />
                    <CC1:MasterControlField DataField="ActionNumber" HeaderText="Action#" />
                    <CC1:MasterControlField DataField="StepNo" HeaderText="Step" />
                    <CC1:MasterControlField DataField="MeetingDateTime" HeaderText="Meeting Date" HtmlEncode="false" />
                    <CC1:MasterControlField DataField="ActionItem" HeaderText="Action Item" />
                    <CC1:MasterControlField DataField="AssignedTo" HeaderText="Assigned" />
                    <CC1:MasterControlField DataField="TargetDate" HeaderText="Target Date" HtmlEncode="false" />
                    <CC1:MasterControlField DataField="AllowEdit" HeaderText="AllowEdit" Visible="false" />
                </GridColumns>
            </CC1:MasterControl>
            <br />
            <br />
            <asp:Panel runat="server" ID="pnlAnomalies" Visible="false">
                <asp:Label ID="lblAnomalyActions" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Anomaly Actions</asp:Label>
                <CC1:MasterControl ID="mcAnomalyActions" runat="server" ShowAdd="false" ShowDelete="false"
                    EditLabel="Process" ShowView="false" ShowEdit="True" NewLinkCaption="Anomaly Action"
                    RedirectProgramName="AnomalyActions2" FormName="Anomaly Actions" ProgramName="MyActions"
                    CommandText="spSelMyAnomalyActions" PrimaryControl="false" ShowExport="false"
                    ProgramMode="AnomalyActionMode" AlternatingRows="True" Translate="True">
                    <GridColumns>
                        <CC1:MasterControlField DataField="AnomalyActionID" HeaderText="AnomalyActionID"
                            Visible="false" />
                        <CC1:MasterControlField DataField="AnomalyID" HeaderText="ID" />
                        <CC1:MasterControlField DataField="Anomaly" HeaderText="Anomaly" />
                        <CC1:MasterControlField DataField="AnomalyCause" HeaderText="Cause" ShowReturns="True" />
                        <CC1:MasterControlField DataField="ActionWhat" HeaderText="What" ShowReturns="True" />
                        <CC1:MasterControlField DataField="TargetDate" HeaderText="Target Date" HtmlEncode="false" />
                        <CC1:MasterControlField DataField="Actions" HeaderText="Actions" ShowReturns="True" />
                    </GridColumns>
                </CC1:MasterControl>
                <br />
                <br />
                <asp:Label ID="lblAnomalyActionPlan" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Anomalies</asp:Label>
                <CC1:MasterControl ID="mcAnomalyActionPlan" runat="server" ShowAdd="false" ShowDelete="false"
                    EditLabel="Process" ShowView="false" ShowEdit="True" NewLinkCaption="Anomaly"
                    RedirectProgramName="AnomalyMaster2" PrimaryControl="false" FormName="Anomaly Maintenance"
                    ProgramName="AnomalyMaster1" CommandText="spSelMyAnomalyActionPlan" ProgramMode="AnomalyMode"
                    AlternatingRows="True" ShowExport="False" Translate="True">
                    <GridColumns>
                        <CC1:MasterControlField DataField="AnomalyID" HeaderText="ID" />
                        <CC1:MasterControlField DataField="AnomalyType" HeaderText="Type" />
                        <CC1:MasterControlField DataField="Anomaly" HeaderText="Anomaly" />
                        <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
                        <CC1:MasterControlField DataField="CreatedDateTime" HeaderText="Created" />
                        <CC1:MasterControlField DataField="CreatedUser" HeaderText="Created By" />
                        <CC1:MasterControlField DataField="EditAnomaly" HeaderText="EditAnomaly" Visible="False" />
                        <CC1:MasterControlField DataField="EditActions" HeaderText="EditActions" Visible="False" />
                        <CC1:MasterControlField DataField="AutoGenerated" HeaderText="AutoGenerated" Visible="False" />
                    </GridColumns>
                </CC1:MasterControl>
                <br />
                <br />
                <asp:Label ID="lblAnomaliesAnalysis" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Anomalies Pending Analysis</asp:Label>
                <CC1:MasterControl ID="mcAnomalies" runat="server" ShowAdd="false" ShowDelete="false"
                    EditLabel="Process" ShowView="false" ShowEdit="True" NewLinkCaption="Anomaly"
                    RedirectProgramName="AnomalyMaster2" PrimaryControl="false" FormName="Anomaly Maintenance"
                    ProgramName="AnomalyMaster1" CommandText="spSelMyAnomalies" ProgramMode="AnomalyMode"
                    AlternatingRows="True" ShowExport="False" Translate="True">
                    <GridColumns>
                        <CC1:MasterControlField DataField="AnomalyID" HeaderText="ID" />
                        <CC1:MasterControlField DataField="AnomalyType" HeaderText="Type" />
                        <CC1:MasterControlField DataField="Anomaly" HeaderText="Anomaly" />
                        <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
                        <CC1:MasterControlField DataField="CreatedDateTime" HeaderText="Created" />
                        <CC1:MasterControlField DataField="CreatedUser" HeaderText="Created By" />
                        <CC1:MasterControlField DataField="EditAnomaly" HeaderText="EditAnomaly" Visible="False" />
                        <CC1:MasterControlField DataField="AutoGenerated" HeaderText="AutoGenerated" Visible="False" />
                    </GridColumns>
                </CC1:MasterControl>
                <br />
                <br />
                <asp:Label ID="lblAnomalyEvaluation" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Anomalies Pending Evaluation</asp:Label>
                <CC1:MasterControl ID="mcAnomalyEvaluation" runat="server" ShowAdd="false" ShowDelete="False"
                    ShowEdit="True" NewLinkCaption="Anomaly" RedirectProgramName="AnomalyMaster2"
                    EditLabel="Process" PrimaryControl="false" FormName="Anomaly Maintenance" ProgramName="AnomalyMaster1"
                    CommandText="spSelMyAnomaliesPendingEvaluation" ProgramMode="AnomalyMode" AlternatingRows="True"
                    ShowExport="False" Translate="True">
                    <GridColumns>
                        <CC1:MasterControlField DataField="AnomalyID" HeaderText="ID" />
                        <CC1:MasterControlField DataField="AnomalyType" HeaderText="Type" />
                        <CC1:MasterControlField DataField="Anomaly" HeaderText="Anomaly" />
                        <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
                        <CC1:MasterControlField DataField="CreatedDateTime" HeaderText="Created" />
                        <CC1:MasterControlField DataField="CreatedUser" HeaderText="Created By" />
                        <CC1:MasterControlField DataField="ClosedDateTime" HeaderText="Closed" />
                        <CC1:MasterControlField DataField="EditAnomaly" HeaderText="EditAnomaly" Visible="False" />
                        <CC1:MasterControlField DataField="EditActions" HeaderText="EditActions" Visible="False" />
                    </GridColumns>
                </CC1:MasterControl>
                <br />
                <br />
            </asp:Panel>
            <asp:Label ID="lblMyKPI" runat="server" CssClass="HeaderTitleText" Font-Bold="True">KPIs Pending Input</asp:Label>
            <CC1:MasterControl ID="mcMyKPI" runat="server" ShowAdd="false" ShowDelete="false"
                EditLabel="Process" ShowView="false" ShowEdit="True" NewLinkCaption="Anomaly"
                RedirectProgramName="AnomalyMaster2" PrimaryControl="false" FormName="Anomaly Maintenance"
                ProgramName="AnomalyMaster1" ShowExport="false" CommandText="spSelMyResponsibleKPI"
                ProgramMode="AnomalyMode" AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="KPIID" HeaderText="KPIID" Visible="False" />
                    <CC1:MasterControlField DataField="KPI" HeaderText="KPI" />
                    <CC1:MasterControlField DataField="UOM" HeaderText="UOM" />
                    <CC1:MasterControlField DataField="ValueType" HeaderText="Entry Type" />
                </GridColumns>
            </CC1:MasterControl>
            <br />
            <br />
            <table id="Table3" class="Table_Default">
                <tr>
                    <td>
                        <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                        </asp:Button>
                    </td>
                </tr>
            </table>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
</asp:Content>
