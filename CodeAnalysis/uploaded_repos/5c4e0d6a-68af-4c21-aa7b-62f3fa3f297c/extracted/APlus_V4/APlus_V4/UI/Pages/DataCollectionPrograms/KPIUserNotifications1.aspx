<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIUserNotifications1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIUserNotifications1"
    Title="KPI User Notifications" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelKPIUserNotifications"
                FormName="KPI Notifications" NewLinkCaption="KPI User Notification" ProgramMode="Mode"
                ProgramName="KPIUserNotifications1" RedirectProgramName="KPIUserNotifications2"
                AlternatingRows="True" ShowExport="True" ShowView="false" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="UserID" HeaderText="UserID" Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPIID" HeaderText="KPIID" Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="UserName" SortExpression="UserName" HeaderText="User">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPI" SortExpression="KPI" HeaderText="KPI">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPIValueEntry" SortExpression="KPIValueEntry"
                        HeaderText="Value Entry" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPIValueEntryReminder" SortExpression="KPIValueEntryReminder"
                        HeaderText="Reminder" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPITargetEntry" SortExpression="KPITargetEntry"
                        HeaderText="Target Entry" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPITargetEntryReminder" SortExpression="KPITargetEntryReminder"
                        HeaderText="Reminder" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPIDeviation" SortExpression="KPIDeviation" HeaderText="Deviation"
                        ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyPending" SortExpression="AnomalyPending"
                        HeaderText="Pending Anomalies" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyPendingReminder" SortExpression="AnomalyPendingReminder"
                        HeaderText="Reminder" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyActions" SortExpression="AnomalyActions"
                        HeaderText="Anomaly Actions" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyActionsReminder" SortExpression="AnomalyActionsReminder"
                        HeaderText="Reminder" ShowReturns="False">
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
