<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIReportCategoryKPIMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIReportCategoryKPIMaster1"
    Title="KPI Group KPI" %>

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
                    <td class="style1">
                        <asp:Label ID="lblSite" runat="server">Site:</asp:Label>
                    </td>
                    <td class="style3">
                        <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td class="style5">
                        <asp:Label ID="lblKPIGroup" runat="server">KPI Group:</asp:Label>
                    </td>
                    <td class="style4">
                        <asp:DropDownList ID="ddlKPIGroup" runat="server" CssClass="DropdownList_Entry" Width="190px">
                        </asp:DropDownList>
                    </td>
                </tr>
                <tr>
                    <td class="style1">
                        <asp:Label ID="lblBusinessArea" runat="server">Business Area:</asp:Label>
                    </td>
                    <td class="style3">
                        <asp:DropDownList ID="ddlBusinessArea" runat="server" CssClass="DropdownList_Entry"
                            Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td class="style5">
                    </td>
                    <td class="style4">
                    </td>
                </tr>
                <tr>
                    <td class="style1">
                        &nbsp;
                    </td>
                    <td class="style3">
                    </td>
                    <td class="style5">
                    </td>
                    <td class="style4">
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
                ShowEdit="True" NewLinkCaption="KPI Group Item" RedirectProgramName="KPIReportCategoryKPIMaster2"
                FormName="KPI Group KPI Maintenance" ProgramName="KPIReportCategoryKPIMaster1"
                CommandText="spSelKPIReportCategoryKPIMaster" ProgramMode="Mode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="KPIReportCategoryID" HeaderText="KPIReportCategoryID" />
                    <CC1:MasterControlField Visible="False" DataField="KPIID" HeaderText="KPIID" />
                    <CC1:MasterControlField DataField="BusinessArea" SortExpression="BusinessArea" HeaderText="Business Area" />
                    <CC1:MasterControlField DataField="KPIReportName" SortExpression="ReportSequence|KPIReportName"
                        HeaderText="KPI Group" />
                    <CC1:MasterControlField DataField="KPIOther" SortExpression="KPIOther" HeaderText="KPI" />
                    <CC1:MasterControlField DataField="ReportLegend" SortExpression="ReportLegend" HeaderText="Legend" />
                    <CC1:MasterControlField DataField="UOM" SortExpression="UOM" HeaderText="UOM" />
                    <CC1:MasterControlField Visible="False" DataField="ReportSequence" SortExpression="ReportSequence"
                        HeaderText="Report Seq" />
                    <CC1:MasterControlField DataField="Sequence" SortExpression="Sequence" HeaderText="Seq" />
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
            width: 81px;
        }
        .style3
        {
            width: 200px;
        }
        .style4
        {
            width: 195px;
        }
        .style5
        {
            width: 55px;
        }
    </style>
</asp:Content>
