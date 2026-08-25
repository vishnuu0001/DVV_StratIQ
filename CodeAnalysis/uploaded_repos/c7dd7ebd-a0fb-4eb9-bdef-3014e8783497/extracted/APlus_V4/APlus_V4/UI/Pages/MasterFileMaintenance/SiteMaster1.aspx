<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SiteMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.SiteMaster1"
    Title="Site Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelSiteMaster"
                FormName="Site Master Maintenance" NewLinkCaption="Site" ProgramMode="SiteMasterMode"
                ProgramName="SiteMaster1" RedirectProgramName="SiteMaster2" ShowExport="True"
                Translate="True" AlternatingRows="True" InitialSort="Site|Active">
                <GridColumns>
                    <CC1:MasterControlField DataField="SiteID" HeaderText="SiteID" ShowReturns="False"
                        Visible="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" ShowReturns="False" SortExpression="Site|Active">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ADSite" HeaderText="AD Site" ShowReturns="False"
                        SortExpression="ADSite|Active">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="SiteAbbrev" HeaderText="Site Abbrev" ShowReturns="False"
                        SortExpression="SiteAbbrev|Active">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="CurrencyAbbrev" HeaderText="Cur Abbrev" ShowReturns="False"
                        SortExpression="CurrencyAbbrev|Active">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="TimeOffsetHours" HeaderText="Time Offset" ShowReturns="False"
                        SortExpression="TimeOffsetHours|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Active" HeaderText="Active" ShowReturns="False"
                        SortExpression="Active|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="TeamActions" HeaderText="Team Action" ShowReturns="False"
                        SortExpression="TeamActions|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="TeamActionsReminder" HeaderText="Team Action Reminder"
                        ShowReturns="False" SortExpression="TeamActionsReminder|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPIValueEntry" HeaderText="KPI Value Entry" ShowReturns="False"
                        SortExpression="KPIValueEntry|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPIValueEntryReminder" HeaderText="KPI Value Entry Reminder"
                        ShowReturns="False" SortExpression="KPIValueEntryReminder|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPITargetEntry" HeaderText="KPI Target Entry"
                        ShowReturns="False" SortExpression="KPITargetEntry|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPITargetEntryReminder" HeaderText="KPI Target Entry Reminder"
                        ShowReturns="False" SortExpression="KPITargetEntryReminder|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyPending" HeaderText="Anomaly Pending" ShowReturns="False"
                        SortExpression="AnomalyPending|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyPendingReminder" HeaderText="Anomaly Pending Reminder"
                        ShowReturns="False" SortExpression="AnomalyPendingReminder|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyActions" HeaderText="Anomaly Actions" ShowReturns="False"
                        SortExpression="AnomalyActions|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyActionsReminder" HeaderText="Anomaly Actions Reminder"
                        ShowReturns="False" SortExpression="AnomalyActionsReminder|Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="TeamMeetingReminder" HeaderText="Team Meeting"
                        ShowReturns="False" SortExpression="TeamMeetingReminder|Site">
                    </CC1:MasterControlField>
                </GridColumns>
            </CC1:MasterControl>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
</asp:Content>
