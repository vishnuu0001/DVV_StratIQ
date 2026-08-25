<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MasterPlanSavings2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MasterPlanSavings2"
    Title="Master Plan Savings" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
    <style type="text/css">
        .style5
        {
            width: 125px;
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
            <table>
                <tr>
                    <td>
                        <asp:CheckBox runat="server" ID="chkProjected" 
                            Text="Show Projected / Phantom" />
                    </td>
                </tr>
            </table>
            <table width="100%">
                <tr>
                    <td style="width: 146px">
                        <asp:Button ID="btnApplyFilter" TabIndex="3" Text="Apply Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                </tr>
            </table>
            <hr style="width: 99%; color: black; height: 1px">
            <asp:Table ID="tblSiteTotals" runat="server" Width="99%" GridLines="Both" CellPadding="1"
                CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White"
                Style="margin: 2px;">
            </asp:Table>
            <br />
            <hr style="width: 99%; color: black; height: 1px">
            <asp:Table ID="tblTrackerSavings" runat="server" Width="99%" GridLines="Both" CellPadding="1"
                CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White"
                Style="margin: 2px;">
            </asp:Table>
            <br />
            <asp:Table ID="tblTeams" runat="server" Width="99%" GridLines="Both" CellPadding="1"
                CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White"
                Style="margin: 2px;">
            </asp:Table>
            <br />
            <asp:Panel ID="pnlExit" runat="server">
                <table id="Table5" cellspacing="0" cellpadding="2" width="321" border="0">
                    <tr>
                        <td align="left" style="width: 158px">
                            <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                            </asp:Button>
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <asp:ValidationSummary ID="Validationsummary1" runat="server" ShowSummary="False"
                ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
</asp:Content>
