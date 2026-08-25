<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerVariables1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerVariables1"
    Title="Tracker Variables Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="True" ShowDelete="True"
                ShowEdit="True" NewLinkCaption="Tracker Variable" RedirectProgramName="TrackerVariables2"
                FormName="Tracker Variable Maintenance" ProgramName="TrackerVariables1" CommandText="spSelTrackerVariables"
                ProgramMode="TrackerVariableMode" AlternatingRows="True" Translate="true">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="TrackerVariableID" HeaderText="TrackerVariableID" />
                    <CC1:MasterControlField DataField="TrackerVariable" SortExpression="TrackerVariable"
                        HeaderText="Variable" />
                    <CC1:MasterControlField DataField="VariableValue" SortExpression="VariableValue"
                        HeaderText="Value" />
                    <CC1:MasterControlField DataField="Site" SortExpression="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="Interface" SortExpression="Interface" HeaderText="Interface" />
                    <CC1:MasterControlField DataField="VariableTrackers" HeaderText="Trackers" ShowReturns="true" />
                    <CC1:MasterControlField DataField="LastUserID" HeaderText="Last Modified By" ShowReturns="true" />
                    <CC1:MasterControlField DataField="LastDateTime" HeaderText="Last Modified" ShowReturns="true"
                        HtmlEncode="false" />
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
