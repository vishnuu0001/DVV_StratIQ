<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="Teams3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Teams3"
    Title="My Teams" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 250px;
        }
        .style2
        {
            width: 220px;
        }
        .style3
        {
            width: 68px;
        }
        .style4
        {
            width: 50px;
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
                    <td class="style1">
                        <asp:CheckBox ID="ckTeamMember" runat="server" Text="Show Only Teams where I am a Member" />
                    </td>
                    <td class="style4">
                        <asp:Label ID="lblStatus" runat="server">Status:</asp:Label>
                    </td>
                    <td class="style2">
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
                    <td class="style1">
                        <asp:CheckBox ID="ckMyPillarTeams" runat="server" Text="Show Only Teams where I am a Pillar Member" />
                    </td>
                    <td class="style4">
                        <asp:Label ID="lblPillar" runat="server">Pillar:</asp:Label>
                    </td>
                    <td class="style2">
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
                    <td class="style1">
                    </td>
                    <td class="style4">
                    </td>
                    <td class="style2">
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
            <asp:Table ID="tblTeams" runat="server" Width="100%" GridLines="None" CellPadding="1"
                CellSpacing="1" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
            </asp:Table>
            <table>
                <tr>
                    <td>
                        <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="~/UI/Pages/DataCollectionPrograms/Teams4.aspx"
                            Text="Printer Friendly Version"></asp:HyperLink>
                    </td>
                </tr>
            </table>
            <table id="Table5" cellspacing="0" cellpadding="2" width="321" border="0" class="Table_Default">
                <tr>
                    <td align="left" colspan="3">
                        <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                        </asp:Button>
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
