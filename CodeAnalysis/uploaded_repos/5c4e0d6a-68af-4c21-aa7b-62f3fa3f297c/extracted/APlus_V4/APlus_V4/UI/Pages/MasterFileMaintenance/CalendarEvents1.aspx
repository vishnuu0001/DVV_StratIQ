<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="CalendarEvents1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.CalendarEvents1"
    Title="Calendar Events" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelCalendarEvents"
                FormName="Culture Master Maintenance" NewLinkCaption="Calendar Event" ProgramMode="CalendarEventsMode"
                ProgramName="CalendarEvents1" RedirectProgramName="CalendarEvents2" ShowExport="True"
                AlternatingRows="True" InitialSort="EventDate|Event" InitialSortOrder="Desc">
                <GridColumns>
                    <CC1:MasterControlField DataField="CalendarEventID" HeaderText="CalendarEventID"
                        ShowReturns="False" Visible="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" ShowReturns="False" SortExpression="Site|EventDate">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="EventType" HeaderText="Event Type" ShowReturns="False"
                        SortExpression="EventType|EventDate">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Event" HeaderText="Event" ShowReturns="False"
                        SortExpression="Event|EventDate">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="EventDate" HeaderText="Date" ShowReturns="False"
                        SortExpression="EventDate|EventType" HtmlEncode="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="EventTime" HeaderText="Time" ShowReturns="False">
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
