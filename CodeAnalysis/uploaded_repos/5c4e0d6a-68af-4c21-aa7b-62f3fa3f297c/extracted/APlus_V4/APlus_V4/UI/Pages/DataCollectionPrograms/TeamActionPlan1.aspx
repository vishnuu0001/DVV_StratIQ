<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamActionPlan1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamActionPlan1"
    Title="Team Action Plan Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelTeamActionPlans"
                ProgramName="TeamActionPlan" FormName="Team Action Plan" RedirectProgramName="TeamActionPlanMaintenance2"
                NewLinkCaption="Team Action" ShowView="True" ShowEdit="True" ShowDelete="True"
                ShowAdd="True" ProgramMode="TeamActionPlanMode" ShowExport="True" AlternatingRows="True"
                Translate="True" RaiseExitEvent="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamMeetingID" HeaderText="TeamMeetingID" Visible="false" />
                    <CC1:MasterControlField DataField="ActionNumber" SortExpression="ActionNumber" HeaderText="Action#" />
                    <CC1:MasterControlField DataField="StepNo" SortExpression="StepNo" HeaderText="Step" />
                    <CC1:MasterControlField DataField="MeetingDateTime" SortExpression="MeetingDateTime"
                        HeaderText="Meeting Date" HtmlEncode="false" />
                    <CC1:MasterControlField DataField="ActionItem" SortExpression="ActionItem" HeaderText="Action Item" />
                    <CC1:MasterControlField DataField="AssignedTo" SortExpression="AssignedTo" HeaderText="Assigned" />
                    <CC1:MasterControlField DataField="AssignedToOther" SortExpression="AssignedToOther"
                        HeaderText="Assigned Other" />
                    <CC1:MasterControlField DataField="TargetDate" SortExpression="TargetDate" HeaderText="Target Date"
                        HtmlEncode="false" />
                    <CC1:MasterControlField DataField="ClosedDate" SortExpression="ClosedDate" HeaderText="Closed Date"
                        HtmlEncode="false" />
                    <CC1:MasterControlField DataField="Cancelled" HeaderText="Cancelled" Visible="false" />
                    <CC1:MasterControlField DataField="ActionItemDefinition" HeaderText="ActionItemDefinition"
                        Visible="false" />
                </GridColumns>
            </CC1:MasterControl>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
    <table id="tbButtons" class="Table_Default">
        <tr>
            <td class="style1">
                <asp:CheckBox ID="chkDisplayClosedTeamActions" runat="server" Checked="True" Width="176px"
                    AutoPostBack="True" Text="Include Closed Team Actions" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
            <td class="style2">
                <asp:CheckBox ID="chkSendStatusEmail" runat="server" Text="Send Email on Exit"></asp:CheckBox>
            </td>
            <td>
                <asp:HyperLink ID="lnkPrintPage" runat="server" NavigateUrl="TeamActionPlan3.aspx"
                    Target="_blank" Text="Printer Friendly Version" CssClass="Link_Default"></asp:HyperLink>
            </td>
        </tr>
    </table>
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 215px;
        }
        .style2
        {
            width: 200px;
        }
    </style>
</asp:Content>
