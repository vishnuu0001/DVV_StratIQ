<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MasterPlanSavings4.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MasterPlanSavings4"
    Title="Master Plan Savings" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
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
                    <td class="style1">
                        <asp:Label ID="lblSite" runat="server">Site:</asp:Label>
                    </td>
                    <td class="style3">
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
                        <asp:CheckBox ID="chkProjected" runat="server" Text="Show Projected / Phantom" />
                    </td>
                    <td style="width: 200px">
                        <asp:Label ID="lblMessage" runat="server" ForeColor="Red" Visible="False">You must select a Site or a Business Area</asp:Label>
                    </td>
                </tr>
            </table>
            <table width="100%">
                <tr>
                    <td style="width: 146px">
                        <asp:Button ID="btnApplyFilter" TabIndex="3" Text="Apply Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                    <td>
                        <asp:Button ID="btnClearFilter" TabIndex="3" Text="Clear Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                    <td style="text-align: right;">
                        <asp:Button ID="btnLocalCurrency" TabIndex="3" Text="Show Savings in local currency"
                            CssClass="Button_Variable" runat="server"></asp:Button>
                    </td>
                </tr>
            </table>
            <hr style="width: 99%; color: black; height: 1px">
            <asp:Table ID="tblTrackerSavings" runat="server" Width="99%" GridLines="Both" CellPadding="1"
                CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White"
                Style="margin: 2px;">
            </asp:Table>
            <br />
            <hr style="width: 99%; color: black; height: 1px">
            <asp:Table ID="tblBATotals" runat="server" Width="99%" GridLines="Both" CellPadding="1"
                CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White"
                Style="margin: 2px;">
            </asp:Table>
            <br />
            <hr style="width: 99%; color: black; height: 1px">
            <asp:Table ID="tblTotals" runat="server" Width="99%" GridLines="Both" CellPadding="1"
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
<asp:Content ID="Content3" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 50px;
        }
        .style3
        {
            width: 210px;
        }
        .style5
        {
            width: 160px;
        }
    </style>
</asp:Content>
