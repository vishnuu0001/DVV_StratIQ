<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="Teams1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Teams1"
    Title="Teams Maintenance" %>

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
            <table id="Table2" width="100%">
                <tr>
                    <td class="style2">
                        <asp:Label ID="lblStatus" runat="server">Status:</asp:Label>
                    </td>
                    <td class="style1">
                        <asp:DropDownList ID="ddlStatus" runat="server" CssClass="DropdownList_Entry" Width="190px">
                            <asp:ListItem Value="X" Text=""></asp:ListItem>
                            <asp:ListItem Value="" Text="Planned/Open/Monitoring"></asp:ListItem>
                            <asp:ListItem Value="P" Text="Planned"></asp:ListItem>
                            <asp:ListItem Value="O" Text="Open"></asp:ListItem>
                            <asp:ListItem Value="S" Text="Stopped"></asp:ListItem>
                            <asp:ListItem Value="D" Text="Monitoring"></asp:ListItem>
                            <asp:ListItem Value="C" Text="Closed"></asp:ListItem>
                        </asp:DropDownList>
                    </td>
                    <td class="style3">
                        <asp:Label ID="lblTeamType" runat="server">Team Type:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlTeamType" runat="server" CssClass="DropdownList_Entry" Width="190px">
                        </asp:DropDownList>
                    </td>
                </tr>
                <tr>
                    <td class="style2">
                        <asp:Label ID="lblPillar" runat="server">Pillar:</asp:Label>
                    </td>
                    <td class="style1">
                        <asp:DropDownList ID="ddlPillar" runat="server" CssClass="DropdownList_Entry" Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td class="style3">
                        &nbsp;
                    </td>
                    <td>
                        &nbsp;
                    </td>
                </tr>
                <tr>
                    <td class="style2">
                    </td>
                    <td class="style1">
                        &nbsp;
                    </td>
                    <td class="style3">
                        &nbsp;
                    </td>
                    <td>
                        &nbsp;
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
            <CC1:MasterControl ID="MasterControl1" runat="server" ProgramMode="TeamsMode" ShowAdd="True"
                ShowDelete="True" ShowEdit="True" ShowView="True" NewLinkCaption="Team" RedirectProgramName="TeamsMaintenance2"
                FormName="Teams Maintenance" ProgramName="TeamsMaintenance" CommandText="[spSelTeamsBySite]"
                ShowExport="True" AlternatingRows="True" ShowRowCount="True" Translate="True"
                InitialSort="TeamSort">
                <GridColumns>
                    <CC1:MasterControlField ShowReturns="False" DataField="TeamID" HeaderText="TeamID"
                        Visible="false" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Team" SortExpression="TeamSort"
                        HeaderText="Team" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TeamName" SortExpression="TeamName"
                        HeaderText="Team Name" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Site" SortExpression="Site"
                        HeaderText="Site" />
                    <CC1:MasterControlField ShowReturns="False" DataField="PillarAbbrev" SortExpression="PillarAbbrev"
                        HeaderText="PIL" />
                    <CC1:MasterControlField ShowReturns="False" DataField="BusinessAreaAbbrev" SortExpression="BusinessAreaAbbrev"
                        HeaderText="BA" />
                    <CC1:MasterControlField ShowReturns="False" DataField="BusinessUnitAbbrev" SortExpression="BusinessUnitAbbrev"
                        HeaderText="BU" />
                    <CC1:MasterControlField ShowReturns="False" DataField="DeptNumber" SortExpression="DeptNumber"
                        HeaderText="Dept" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Route" SortExpression="Route"
                        HeaderText="Route" />
                    <CC1:MasterControlField ShowReturns="False" DataField="OPI" SortExpression="OPI"
                        HeaderText="OPI" />
                    <CC1:MasterControlField ShowReturns="False" DataField="SavingsTracker" SortExpression="SavingsTracker"
                        HeaderText="Savings Tracker" />
                    <CC1:MasterControlField ShowReturns="False" DataField="ResponsibleUser" SortExpression="ResponsibleUser"
                        HeaderText="Resp" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TeamStartDate" SortExpression="TeamStartDate"
                        HeaderText="Start" HtmlEncode="false" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TeamFinishDate" SortExpression="TeamFinishDate"
                        HeaderText="Finish" HtmlEncode="false" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Duration" SortExpression="Duration"
                        HeaderText="Duration" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TeamStatusDescription" SortExpression="TeamStatusDescription"
                        HeaderText="Status" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TeamType" SortExpression="TeamTypeID"
                        HeaderText="Type" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TeamSort" Visible="false" />
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
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 215px;
        }
        .style2
        {
            width: 70px;
        }
        .style3
        {
            width: 80px;
        }
    </style>
</asp:Content>
