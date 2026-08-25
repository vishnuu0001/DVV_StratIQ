<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RouteStepsKeyActions1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RouteStepsKeyActions1"
    Title="Route Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelRouteStepsKeyActions"
                ProgramName="RouteStepsKeyActions1" FormName="Route Step Key Actions" RedirectProgramName="RouteStepsKeyActions2"
                NewLinkCaption="Key Action" ShowView="True" ShowEdit="True" ShowDelete="True"
                ShowAdd="True" ProgramMode="RouteStepsKeyActionsMode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="RouteAbbrev" SortExpression="RouteAbbrev" HeaderText="Route Abbreviation" />
                    <CC1:MasterControlField DataField="StepNo" SortExpression="StepNo" HeaderText="Step" />
                    <CC1:MasterControlField DataField="KeyActionNo" SortExpression="KeyActionNo" HeaderText="Key Action No" />
                    <CC1:MasterControlField DataField="KeyAction" HeaderText="Key Action" />
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
