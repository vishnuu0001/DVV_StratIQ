<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIEvents1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIEvents1"
    Title="OPI Events" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="[spSelTeamOPIEvents]"
                ProgramName="TeamOPIEvents1" FormName="Team OPI Events" RedirectProgramName="TeamOPIEvents2"
                ShowView="True" ShowEdit="True" ShowDelete="True" ShowAdd="True" NewLinkCaption="Team OPI Event"
                ProgramMode="TeamOPIEventMode" AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="Team" HeaderText="Team" />
                    <CC1:MasterControlField DataField="OPI" HeaderText="OPI" />
                    <CC1:MasterControlField DataField="EventDate" SortExpression="EventDate" HeaderText="Event Date" />
                    <CC1:MasterControlField DataField="EventDescription" SortExpression="EventDescription"
                        HeaderText="Description" />
                    <CC1:MasterControlField DataField="ShortDescription" SortExpression="ShortDescription"
                        HeaderText="Short Description" />
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
