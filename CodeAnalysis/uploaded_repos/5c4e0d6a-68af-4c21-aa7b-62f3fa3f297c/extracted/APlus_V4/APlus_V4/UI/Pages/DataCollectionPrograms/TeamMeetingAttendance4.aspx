<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamMeetingAttendance4.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamMeetingAttendance4"
    Title="Team Meeting Attendance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelTeamMeetingAttendanceNonMembers"
                FormName="Team Meeting Attendance" ProgramMode="TeamMeetingAttendanceMode" ProgramName="TeamMeetingAttendance4"
                RedirectProgramName="TeamMeetingAttendance2" ShowView="False" ShowEdit="False"
                ShowDelete="True" ShowAdd="False" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="MeetingDate" SortExpression="MeetingDate" HeaderText="Meeting Date" />
                    <CC1:MasterControlField DataField="MeetingTime" SortExpression="MeetingTime" HeaderText="Meeting Time"
                        ShowReturns="False" />
                    <CC1:MasterControlField DataField="UserName" SortExpression="UserName" HeaderText="User"
                        ShowReturns="False" />
                    <CC1:MasterControlField DataField="Invited" SortExpression="Invited" HeaderText="Invited"
                        ShowReturns="False" />
                    <CC1:MasterControlField DataField="Attended" SortExpression="Attended" HeaderText="Attended"
                        ShowReturns="False" />
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
