<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MyActionItems.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MyActionItems"
    Title="My Action Items" %>

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
            <table id="Table1" width="100%">
                <tr>
                    <td style="width: 340px">
                        <asp:CheckBox ID="ckTeamMember" runat="server" Text="Include Action Items for Teams where I am a Team Member" />
                    </td>
                    <td style="width: 240px">
                        <asp:CheckBox ID="ckMyTeams" runat="server" Text="Include Action Items for All My Teams" />
                    </td>
                    <td style="width: 40px">
                        <asp:Label ID="lblPillar" runat="server">Pillar:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlPillar" runat="server" CssClass="DropdownList_Entry" Width="195px">
                        </asp:DropDownList>
                    </td>
                </tr>
                <tr>
                    <td>
                        <asp:CheckBox ID="ckMyPillarTeams" runat="server" Text="Include Action Items for Teams where I am a Pillar Member" />
                    </td>
                    <td>
                        <asp:CheckBox ID="ckClosedItems" runat="server" Text="Include Closed Action Items" />
                    </td>
                </tr>
            </table>
            <table>
                <tr>
                    <td style="width: 146px">
                        <asp:Button ID="btnApplyFilter" TabIndex="3" Text="Apply Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                    <td>
                        <asp:Button ID="btnClearFilter" TabIndex="3" Text="Clear Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                </tr>
            </table>
            <hr style="width: 99%; color: black; height: 1px">
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelMyActionItems"
                ProgramName="MyActionItems" FormName="My Action Items" RedirectProgramName="TeamActionPlanMaintenance2"
                NewLinkCaption="" ShowView="True" ShowEdit="True" ShowDelete="False" ShowAdd="False"
                ProgramMode="TeamActionPlanMode" ShowExport="True" AlternatingRows="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamID" HeaderText="TeamID" Visible="false" />
                    <CC1:MasterControlField DataField="TeamStatus" SortExpression="TeamStatus" HeaderText="Status" />
                    <CC1:MasterControlField DataField="SiteAbbrev" SortExpression="SiteAbbrev" HeaderText="Site" />
                    <CC1:MasterControlField DataField="PillarAbbrev" SortExpression="PillarAbbrev" HeaderText="Pillar" />
                    <CC1:MasterControlField DataField="ActionNumber" SortExpression="ActionNumber" HeaderText="Action#" />
                    <CC1:MasterControlField DataField="StepNo" SortExpression="StepNo" HeaderText="Step" />
                    <CC1:MasterControlField DataField="MeetingDateTime" HeaderText="Meeting Date" HtmlEncode="false" />
                    <CC1:MasterControlField DataField="ActionItem" SortExpression="ActionItem" HeaderText="Action Item" />
                    <CC1:MasterControlField DataField="AssignedTo" SortExpression="AssignedTo" HeaderText="Assigned" />
                    <CC1:MasterControlField DataField="TargetDate" SortExpression="TargetDate" HeaderText="Target Date"
                        HtmlEncode="false" />
                    <CC1:MasterControlField DataField="ClosedDate" SortExpression="ClosedDate" HeaderText="Closed Date"
                        HtmlEncode="false" />
                    <CC1:MasterControlField DataField="Cancelled" HeaderText="Cancelled" Visible="false" />
                    <CC1:MasterControlField DataField="AllowEdit" HeaderText="AllowEdit" Visible="false" />
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
