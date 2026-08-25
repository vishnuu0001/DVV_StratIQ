<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MyTrackers.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MyTrackers"
    Title="My Savings Trackers" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
    <style type="text/css">
        .style4
        {
            width: 200px;
        }
        .style5
        {
            width: 75px;
        }
    </style>
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
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
                    <td style="width: 75px">
                        <asp:Label ID="lblSite" runat="server">Site:</asp:Label>
                    </td>
                    <td style="width: 200px">
                        <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td style="width: 75px">
                        <asp:Label ID="lblBA" runat="server">Bus Area:</asp:Label>
                    </td>
                    <td style="width: 200px">
                        <asp:DropDownList ID="ddlBusArea" runat="server" CssClass="DropdownList_Entry" Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td class="style5">
                        <asp:Label ID="lblCategory" runat="server">Category:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlSavingsCategory" runat="server" CssClass="DropdownList_Entry"
                            Width="190px">
                        </asp:DropDownList>
                    </td>
                </tr>
                <tr>
                    <td style="width: 75px">
                        <asp:Label ID="lblPillar" runat="server">Pillar:</asp:Label>
                    </td>
                    <td style="width: 200px">
                        <asp:DropDownList ID="ddlPillar" runat="server" CssClass="DropdownList_Entry" Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td style="width: 75px">
                        <asp:Label ID="lblBU" runat="server">Bus Unit:</asp:Label>
                    </td>
                    <td style="width: 200px">
                        <asp:DropDownList ID="ddlBusinessUnit" runat="server" CssClass="DropdownList_Entry"
                            Width="190px">
                        </asp:DropDownList>
                    </td>
                    <td class="style5">
                        <asp:Label ID="lblSavingsType" runat="server">Savings Type:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlSavingsType" runat="server" CssClass="DropdownList_Entry"
                            Width="190px">
                        </asp:DropDownList>
                    </td>
                </tr>
                <tr>
                    <td style="width: 75px">
                    </td>
                    <td style="width: 200px">
                    </td>
                    <td style="width: 75px">
                    </td>
                    <td style="width: 200px">
                    </td>
                    <td class="style5">
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
            <asp:Table ID="tblTrackers" runat="server" Width="100%" GridLines="None" CellPadding="1"
                CellSpacing="1" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
            </asp:Table>
            <asp:Panel runat="server" ID="pnlNoData" Visible="false">
                <div style="font-size: 10; color: Red;">
                    No Records Exist for current filter</div>
            </asp:Panel>
            <br />
            <CC1:MasterControl ID="mcTrackerTypeTotals" runat="server" ShowAdd="False" ShowDelete="False"
                ShowEdit="False" NewLinkCaption="Savings Tracker" RedirectProgramName="TrackerMaster2"
                FormName="Tracker Maintenance" ProgramName="TrackerMaster1" CommandText="spSelMyTrackerTypesTotals"
                ProgramMode="TrackerMode" AlternatingRows="True" PrimaryControl="False" ShowExit="False"
                ShowExport="False" ShowRowCount="False" ShowView="False" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="SiteAbbrev" HeaderText="Site" />
                    <CC1:MasterControlField DataField="PillarAbbrev" HeaderText="Pillar" />
                    <CC1:MasterControlField DataField="BusinessAreaAbbrev" HeaderText="Bus Area" />
                    <CC1:MasterControlField DataField="BusinessUnitAbbrev" HeaderText="Bus Unit" />
                    <CC1:MasterControlField DataField="SavingsCategory" HeaderText="Category" />
                    <CC1:MasterControlField DataField="TrackerType" HeaderText="Savings Type" />
                    <CC1:MasterControlField DataField="CurrencyAbbrev" HeaderText="Cur" />
                    <CC1:MasterControlField DataField="PreviousYearSavings" HeaderText="Prev Year" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="LastYearSavings" HeaderText="Last Year" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="YearSavings" HeaderText="Current Year" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="LastMonthSavings" HeaderText="Last Month" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="TotalSavings" HeaderText="Total" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                </GridColumns>
            </CC1:MasterControl>
            <br />
            <br />
            <CC1:MasterControl ID="mcTrackerTotals" runat="server" ShowAdd="False" ShowDelete="False"
                ShowEdit="False" NewLinkCaption="Savings Tracker" RedirectProgramName="TrackerMaster2"
                FormName="Tracker Maintenance" ProgramName="TrackerMaster1" CommandText="spSelMyTrackersTotals"
                ProgramMode="TrackerMode" AlternatingRows="True" PrimaryControl="False" ShowExit="False"
                ShowExport="False" ShowRowCount="False" ShowView="False" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="SiteAbbrev" HeaderText="Site" />
                    <CC1:MasterControlField DataField="PillarAbbrev" HeaderText="Pillar" />
                    <CC1:MasterControlField DataField="BusinessAreaAbbrev" HeaderText="Bus Area" />
                    <CC1:MasterControlField DataField="BusinessUnitAbbrev" HeaderText="Bus Unit" />
                    <CC1:MasterControlField DataField="SavingsCategory" HeaderText="Category" />
                    <CC1:MasterControlField DataField="CurrencyAbbrev" HeaderText="Cur" />
                    <CC1:MasterControlField DataField="PreviousYearSavings" HeaderText="Prev Year" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="LastYearSavings" HeaderText="Last Year" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="YearSavings" HeaderText="Current Year" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="LastMonthSavings" HeaderText="Last Month" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="TotalSavings" HeaderText="Total" HeaderStyle-HorizontalAlign="Right"
                        ItemStyle-HorizontalAlign="Right" DataFormatString="{0:0}">
                        <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                        <ItemStyle HorizontalAlign="Right"></ItemStyle>
                    </CC1:MasterControlField>
                </GridColumns>
            </CC1:MasterControl>
            <br />
            <br />
            <table>
                <tr>
                    <td align="left" class="style4">
                        <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                        </asp:Button>
                    </td>
                    <td align="left">
                        <asp:Button ID="btnExport" runat="server" EnableViewState="False" CssClass="Button_Default"
                            Text="Export"></asp:Button>
                    </td>
                </tr>
            </table>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
</asp:Content>
