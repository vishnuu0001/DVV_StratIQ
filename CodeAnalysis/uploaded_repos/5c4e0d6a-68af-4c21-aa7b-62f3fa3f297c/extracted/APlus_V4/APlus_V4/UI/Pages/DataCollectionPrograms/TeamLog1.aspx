<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamLog1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamLog1"
    Title="Team Log Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelTeamLogByTeam"
                FormName="Team Log" NewLinkCaption="Team Log" ProgramMode="TeamLogMode" ProgramName="TeamLog1"
                RedirectProgramName="TeamLog2" ShowView="True" ShowEdit="True" ShowDelete="True"
                ShowAdd="True" AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamLogID" HeaderText="TeamLogID" Visible="false" />
                    <CC1:MasterControlField DataField="CreateDateTime" SortExpression="CreateDateTime"
                        HeaderText="Create Date Time" DataFormatString="{0:yyyy/MM/dd hh:mm:ss}" />
                    <CC1:MasterControlField DataField="LogEntry" SortExpression="LogEntry" HeaderText="Log Entry"
                        ShowReturns="true" />
                    <CC1:MasterControlField DataField="LogResponse" SortExpression="LogResponse" HeaderText="Log Response"
                        ShowReturns="true" />
                    <CC1:MasterControlField DataField="UserName" SortExpression="UserName" HeaderText="User Name"
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
