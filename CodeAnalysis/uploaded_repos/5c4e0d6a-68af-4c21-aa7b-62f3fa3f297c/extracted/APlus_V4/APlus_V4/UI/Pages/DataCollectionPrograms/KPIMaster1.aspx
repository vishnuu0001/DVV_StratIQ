<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIMaster1"
    Title="KPI Maintenance" %>

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
            <table>
                <tr>
                    <td class="style4">
                        <asp:Label ID="lblSearch" runat="server">Search:</asp:Label>
                    </td>
                    <td class="style1">
                        <asp:TextBox runat="server" ID="txtSearch" CssClass="Textbox_Entry" MaxLength="50"
                            Width="150px"></asp:TextBox>
                    </td>
                    <td class="style6">
                        <asp:Label ID="lblActive" runat="server">Show Inactive:</asp:Label>
                    </td>
                    <td class="style1">
                        <asp:CheckBox runat="server" ID="chkActive" />
                    </td>
                </tr>
                <tr>
                    <td class="style4">
                    </td>
                    <td class="style1">
                    </td>
                    <td class="style6">
                        &nbsp;
                    </td>
                    <td class="style1">
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
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="True" ShowDelete="True"
                ShowEdit="True" NewLinkCaption="KPI" RedirectProgramName="KPIMaster2" FormName="KPI Maintenance"
                ProgramName="KPIMaster1" CommandText="spSelKPIMaster" ProgramMode="KPIMasterMode"
                AlternatingRows="True" Translate="true">
                <GridColumns>
                    <CC1:MasterControlField DataField="KPI" SortExpression="KPI" HeaderText="KPI" />
                    <CC1:MasterControlField DataField="KPIOther" SortExpression="KPIOther" HeaderText="KPI (English)" />
                    <CC1:MasterControlField DataField="PrimaryKPI" HeaderText="Primary KPI" />
                    <CC1:MasterControlField DataField="UOM" SortExpression="UOM" HeaderText="UOM" />
                    <CC1:MasterControlField Visible="False" DataField="TargetUp" SortExpression="TargetUp"
                        HeaderText="Target Up" />
                    <CC1:MasterControlField DataField="SiteAbbrev" SortExpression="SiteAbbrev" HeaderText="Site" />
                    <CC1:MasterControlField DataField="TeamCategory" SortExpression="TeamCategory" HeaderText="Category" />
                    <CC1:MasterControlField DataField="SortSequence" SortExpression="SortSequence" HeaderText="Seq" />
                    <CC1:MasterControlField DataField="PillarAbbrev" SortExpression="PillarAbbrev" HeaderText="PIL" />
                    <CC1:MasterControlField DataField="BusinessAreaAbbrev" SortExpression="BusinessAreaAbbrev"
                        HeaderText="BA" />
                    <CC1:MasterControlField DataField="BusinessUnitAbbrev" SortExpression="BusinessUnitAbbrev"
                        HeaderText="BU" />
                    <CC1:MasterControlField DataField="AreaAbbrev" SortExpression="AreaAbbrev" HeaderText="Area" />
                    <CC1:MasterControlField DataField="ReportingLevelAbbrev" SortExpression="ReportingLevelAbbrev"
                        HeaderText="Rep Lvl" />
                    <CC1:MasterControlField Visible="False" DataField="SumType" SortExpression="SumType"
                        HeaderText="Type" />
                    <CC1:MasterControlField DataField="ResponsibleUser" SortExpression="ResponsibleUser"
                        HeaderText="Resp User" />
                    <CC1:MasterControlField DataField="DailyKPI" SortExpression="DailyKPI"
                        HeaderText="Daily KPI" />
                    <CC1:MasterControlField DataField="Interface" HeaderText="Interface" SortExpression="Interface" />
                    <CC1:MasterControlField DataField="AutoGenerateAnomaly" HeaderText="Generate Anomaly"
                        SortExpression="AutoGenerateAnomaly" />
                    <CC1:MasterControlField DataField="Active" HeaderText="Active" SortExpression="Active" />
                    <CC1:MasterControlField Visible="False" DataField="KPIID" HeaderText="KPIID" />
                    <CC1:MasterControlField Visible="False" DataField="AllowEdit" HeaderText="AllowEdit" />
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
            width: 181px;
        }
        .style4
        {
            width: 75px;
        }
        .style5
        {
            width: 60px;
        }
        .style6
        {
            width: 100px;
        }
    </style>
</asp:Content>
