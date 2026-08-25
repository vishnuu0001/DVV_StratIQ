<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIControlLimits1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIControlLimits1"
    Title="OPI Control Limits" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="[spSelTeamOPIControlLimits]"
                ProgramName="TeamOPIControlLimits1" FormName="Team OPI Control Limits" RedirectProgramName="TeamOPIControlLimits2"
                ShowView="True" ShowEdit="True" ShowDelete="True" ShowAdd="True" NewLinkCaption="Team OPI Control Limit"
                ProgramMode="TeamOPIControlLimitsMode" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamID" HeaderText="TeamID" Visible="false" />
                    <CC1:MasterControlField DataField="Team" SortExpression="Team" HeaderText="Team" />
                    <CC1:MasterControlField DataField="OPI" SortExpression="OPI" HeaderText="OPI" />
                    <CC1:MasterControlField DataField="StartDate" SortExpression="StartDate" HeaderText="Start Date" />
                    <CC1:MasterControlField DataField="UpperValue" SortExpression="UpperValue" HeaderText="Upper Value" />
                    <CC1:MasterControlField DataField="LowerValue" SortExpression="LowerValue" HeaderText="Lower Value" />
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
