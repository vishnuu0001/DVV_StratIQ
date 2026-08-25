<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPICollection2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPICollection2"
    Title="KPI Collection" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 91px;
        }
        .style2
        {
            width: 210px;
        }
        .style3
        {
            width: 200px;
        }
        .style5
        {
            width: 146px;
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
                    <td style="width: 40px">
                        <asp:Label ID="lblSite" runat="server">Site:</asp:Label>
                    </td>
                    <td class="style2">
                        <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="195px">
                        </asp:DropDownList>
                    </td>
                    <td style="width: 55px">
                        <asp:Label ID="lblBA" runat="server">Bus Area:</asp:Label>
                    </td>
                    <td class="style3">
                        <asp:DropDownList ID="ddlBusArea" runat="server" CssClass="DropdownList_Entry" Width="180px">
                        </asp:DropDownList>
                    </td>
                    <td class="style1">
                        <asp:Label ID="lblCategory" runat="server">Category:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlTeamCategory" runat="server" CssClass="DropdownList_Entry"
                            Width="125px">
                        </asp:DropDownList>
                    </td>
                    <td>
                    </td>
                    <td>
                    </td>
                </tr>
                <tr>
                    <td style="width: 40px">
                        <asp:Label ID="lblPillar" runat="server">Pillar:</asp:Label>
                    </td>
                    <td class="style2">
                        <asp:DropDownList ID="ddlPillar" runat="server" CssClass="DropdownList_Entry" Width="195px">
                        </asp:DropDownList>
                    </td>
                    <td style="width: 55px">
                        <asp:Label ID="lblBU" runat="server">Bus Unit:</asp:Label>
                    </td>
                    <td class="style3">
                        <asp:DropDownList ID="ddlBusinessUnit" runat="server" CssClass="DropdownList_Entry"
                            Width="180px">
                        </asp:DropDownList>
                    </td>
                    <td class="style1">
                        <asp:Label ID="lblReportingLevel" runat="server">Reporting Level:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlReportingLevel" runat="server" CssClass="DropdownList_Entry"
                            Width="175px">
                        </asp:DropDownList>
                    </td>
                    <td>
                        <asp:Label ID="lblPeriodView" runat="server">Period View:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlViewMode" runat="server" CssClass="DropdownList_Entry" Width="75px">
                            <asp:ListItem>Month</asp:ListItem>
                            <asp:ListItem>Quarter</asp:ListItem>
                        </asp:DropDownList>
                    </td>
                </tr>
                <tr>
                    <td style="width: 40px">
                        <asp:Label ID="lblArea" runat="server">Area:</asp:Label>
                    </td>
                    <td class="style2">
                        <asp:DropDownList ID="ddlArea" runat="server" CssClass="DropdownList_Entry" Width="195px">
                        </asp:DropDownList>
                    </td>
                    <td style="width: 55px">
                    </td>
                    <td class="style3">
                        <asp:CheckBox ID="ckAllAreas" runat="server" Text="Show All Area KPIs" />
                    </td>
                    <td class="style1">
                    </td>
                    <td style="width: 195px">
                        <asp:CheckBox ID="ckShowSupportingKPI" runat="server" Text="Show Supporting KPIs" />
                    </td>
                    <td style="width: 70px">
                        &nbsp;
                    </td>
                    <td>
                        <asp:CheckBox ID="ckResponsibleUser" runat="server" Text="Show Only My Responsible KPIs" />
                    </td>
                </tr>
            </table>
            <table>
                <tr>
                    <td style="width: 150px">
                        <asp:Button ID="btnApplyFilter" TabIndex="3" Text="Apply Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                    <td style="width: 150px">
                        <asp:Button ID="btnClearFilter" TabIndex="3" Text="Clear Filter" CssClass="Button_Default"
                            runat="server"></asp:Button>
                    </td>
                    <td style="width: 600px">
                    </td>
                    <td>
                        <asp:Button ID="btnShowTargets" TabIndex="3" Text="Show Monthly Targets" CssClass="Button_Variable"
                            runat="server"></asp:Button>
                    </td>
                </tr>
            </table>
            <hr style="width: 99%; color: black; height: 1px">
            <asp:Table ID="tblKPIValues" runat="server" Width="100%" GridLines="Both" CellPadding="1"
                CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
            </asp:Table>
            <br />
            <asp:Panel ID="pnlExit" runat="server">
                <table id="Table5" cellspacing="0" cellpadding="2" border="0">
                    <tr>
                        <td align="left" class="style5">
                            <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                            </asp:Button>
                        </td>
                        <td align="left" class="style5">
                            <asp:Button ID="btnRunReport1" runat="server" CausesValidation="False" CssClass="Button_Default"
                                Visible="false" Text="KPI Report 1" />
                        </td>
                        <td align="left" class="style5">
                            <asp:Button ID="btnRunReport2" runat="server" CausesValidation="False" CssClass="Button_Variable"
                                Text="Selected Year Report" />
                        </td>
                        <td align="left" style="width: 158px">
                            <asp:Button ID="btnRunReport3" runat="server" CausesValidation="False" CssClass="Button_Variable"
                                Text="Prev 12 Mths Report" />
                        </td>
                        <td align="left" style="width: 158px">
                            <asp:Button ID="btnExport" runat="server" CausesValidation="False" CssClass="Button_Default"
                                Text="Export" />
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
