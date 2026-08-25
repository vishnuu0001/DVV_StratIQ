<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIReportCategoryMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIReportCategoryMaster1"
    Title="KPI Group" %>

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
                </tr>
                <tr>
                    <td class="style1">
                        <asp:Label ID="lblProgram" runat="server">Program:</asp:Label>
                    </td>
                    <td class="style3">
                        <asp:DropDownList ID="ddlReportGroup" runat="server" CssClass="DropdownList_Entry"
                            Width="190px">
                        </asp:DropDownList>
                    </td>
                </tr>
                <tr>
                    <td class="style6">
                        &nbsp;
                    </td>
                    <td class="style7">
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
                ShowEdit="True" NewLinkCaption="KPI Group" RedirectProgramName="KPIReportCategoryMaster2"
                FormName="KPI Group Maintenance" ProgramName="KPIReportCategoryMaster1" CommandText="spSelKPIReportCategoryMaster"
                ProgramMode="Mode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="KPIReportCategoryID" HeaderText="KPIReportCategoryID" />
                    <CC1:MasterControlField DataField="KPIReportGroup" SortExpression="KPIReportGroup"
                        HeaderText="Program" />
                    <CC1:MasterControlField DataField="Site" SortExpression="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="KPIReportName" SortExpression="KPIReportName"
                        HeaderText="KPI Group" />
                    <CC1:MasterControlField DataField="ReportKey" SortExpression="ReportKey" HeaderText="Report" />
                    <CC1:MasterControlField DataField="Sequence" SortExpression="Sequence" HeaderText="Sequence" />
                    <CC1:MasterControlField DataField="Active" SortExpression="Active" HeaderText="Active" />
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
        .style6
        {
            width: 81px;
            height: 17px;
        }
        .style7
        {
            width: 200px;
            height: 17px;
        }
        .style8
        {
            width: 55px;
            height: 17px;
        }
        .style9
        {
            width: 195px;
            height: 17px;
        }
    </style>
</asp:Content>
