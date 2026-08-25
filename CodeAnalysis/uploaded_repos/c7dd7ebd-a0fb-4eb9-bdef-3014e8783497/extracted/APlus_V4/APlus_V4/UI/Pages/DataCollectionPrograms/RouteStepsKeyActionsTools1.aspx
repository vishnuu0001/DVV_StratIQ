<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RouteStepsKeyActionsTools1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RouteStepsKeyActionsTools1"
    Title="Routes Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="[spSelRouteStepsKeyActionsTools]"
                ProgramName="RouteStepsKeyActionsTools1" FormName="Route Step Key Actions Tools"
                RedirectProgramName="RouteStepsKeyActionsTools2" NewLinkCaption="Key Action Tool"
                ShowView="True" ShowEdit="True" ShowDelete="True" ShowAdd="True" ProgramMode="RouteStepsKeyActionsToolsMode"
                AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField ShowReturns="False" DataField="ToolID" HeaderText="ToolID" />
                    <CC1:MasterControlField ShowReturns="False" DataField="RouteAbbrev" SortExpression="RouteAbbrev"
                        HeaderText="Route" />
                    <CC1:MasterControlField ShowReturns="False" DataField="StepNo" SortExpression="StepNo"
                        HeaderText="Step" />
                    <CC1:MasterControlField ShowReturns="False" DataField="KeyActionNo" SortExpression="KeyActionNo"
                        HeaderText="Key Action" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Tool" SortExpression="Tool"
                        HeaderText="Tool" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TemplateAttachment" HeaderText="Template" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TrainingAttachment" HeaderText="Training" />
                    <CC1:MasterControlField ShowReturns="False" DataField="URLLink" HeaderText="URL" />
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
