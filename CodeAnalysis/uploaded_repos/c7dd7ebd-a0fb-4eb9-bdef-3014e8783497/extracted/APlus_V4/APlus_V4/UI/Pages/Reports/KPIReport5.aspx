<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIReport5.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIReport5"
    Title="Key Asset KPIs" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
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
                    <td valign="top">
                        <table>
                            <tr>
                                <td align="right" class="style5">
                                    <asp:Label ID="lblBusinessArea" runat="server" Text="Business Area:" CssClass="Label_Left_8PT"></asp:Label>
                                </td>
                                <td>
                                    <asp:DropDownList ID="ddlBusinessArea" runat="server" CssClass="DropdownList_Entry"
                                        Width="250px">
                                    </asp:DropDownList>
                                </td>
                                <td align="right" class="style6">
                                    <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
                                </td>
                                <td>
                                    <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="200px">
                                    </asp:DropDownList>
                                </td>
                            </tr>
                            <tr>
                                <td class="style5">
                                    &nbsp;
                                </td>
                                <td class="style5">
                                    &nbsp;
                                </td>
                                <td class="style6">
                                    &nbsp;
                                </td>
                                <td class="style5">
                                    &nbsp;
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            <asp:Panel ID="pnlOKCancel" runat="server">
                <table>
                    <tr>
                        <td class="style4">
                            <asp:Button ID="btnApplyFilter" runat="server" CssClass="Button_Default" Text="Apply Filter"
                                EnableViewState="False"></asp:Button>
                        </td>
                        <td align="left" class="style4">
                            <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                            </asp:Button>
                        </td>
                        <td align="left">
                            <asp:Button ID="btnRunReport" runat="server" CssClass="Button_Default" Text="Run Report"
                                EnableViewState="False" Enabled="False"></asp:Button>
                        </td>
                        <td align="left">
                            <asp:Button ID="btnExport" runat="server" CssClass="Button_Default" Text="Export"
                                EnableViewState="False" Enabled="False"></asp:Button>
                        </td>
                        <td align="right" style="width: 75%">
                            <asp:Button ID="btnNoTargets" TabIndex="3" Text="Hide Monthly Targets" CssClass="Button_Variable"
                                runat="server"></asp:Button>
                        </td>
                        <td align="right">
                            <asp:Button ID="btnEditKPIReport" runat="server" CssClass="Button_Variable" EnableViewState="False"
                                Text="Edit KPI Group Items" />
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
                ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
            <hr style="width: 99%; color: black; height: 1px">
            <asp:Table ID="tblKPIValues" runat="server" Width="100%" GridLines="Both" CellPadding="1"
                CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
            </asp:Table>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
    <br />
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style4
        {
            width: 150px;
        }
        .style5
        {
            width: 95px;
        }
        .style6
        {
            width: 49px;
        }
    </style>
</asp:Content>
