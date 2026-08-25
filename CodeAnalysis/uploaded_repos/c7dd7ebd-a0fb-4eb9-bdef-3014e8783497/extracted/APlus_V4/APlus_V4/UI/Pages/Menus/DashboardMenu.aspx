<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="DashboardMenu.aspx.vb" Inherits="WebApp.APlus.UI.Pages.DashboardMenu"
    Title="Dashboard" %>

<%@ Register Src="../../UserControls/MenuControl.ascx" TagName="MenuControl" TagPrefix="uc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript">
        function TrapKeysForMenu(event) {
            if (event.keyCode == 13)
            { document.all.btnOK.click(); return true; }
            else if ((event.keyCode >= 48 && event.keyCode <= 57)
				|| (event.keyCode == 8)
				|| (event.keyCode == 46)
				|| (event.keyCode == 9)
				|| (event.keyCode >= 96 && event.keyCode <= 105)
				|| (event.keyCode >= 37 && event.keyCode <= 40)
				|| (event.keyCode == 16)
				|| (event.keyCode >= 65 && event.keyCode <= 90))

            { event.returnValue = true; return true; }
            else { event.returnValue = false; event.cancel = true; event.keyCode = 0; return false; }
        }
    </script>
    <br />
    <table style="width: 100%; padding: 0px; margin: 0px;">
        <tr>
            <td style="width: 33%; text-align: center;">
                <asp:Panel runat="server" Style="height: 210px; width: 205px;" ID="Panel1">
                    <asp:Chart ID="chtTeams" runat="server" Height="200px" Width="200px" BackColor="WhiteSmoke">
                        <Series>
                            <asp:Series ChartType="Pie" Name="Series1" IsValueShownAsLabel="true" Legend="Legend1"
                                XValueMember="Description" YValueMembers="Teams">
                            </asp:Series>
                        </Series>
                        <ChartAreas>
                            <asp:ChartArea Name="ChartArea1" BackColor="WhiteSmoke">
                            </asp:ChartArea>
                        </ChartAreas>
                        <Legends>
                            <asp:Legend Name="Legend1" Alignment="Center" Docking="Bottom" Font="Trebuchet MS, 7pt,"
                                BackColor="WhiteSmoke">
                            </asp:Legend>
                        </Legends>
                        <Titles>
                            <asp:Title Text="My Teams" Font="Trebuchet MS, 8pt, style=Bold">
                            </asp:Title>
                        </Titles>
                    </asp:Chart>
                </asp:Panel>
            </td>
            <td style="width: 33%; text-align: center;">
                <asp:Panel runat="server" Style="height: 210px; width: 205px;" ID="Panel2">
                    <asp:Chart ID="chtParticipation" runat="server" Height="200px" Width="200px" BackColor="WhiteSmoke">
                        <Series>
                            <asp:Series ChartType="Pie" Name="Series1" IsValueShownAsLabel="true" Legend="Legend1"
                                XValueMember="ChartLegend" YValueMembers="Value">
                            </asp:Series>
                        </Series>
                        <ChartAreas>
                            <asp:ChartArea Name="ChartArea1" BackColor="WhiteSmoke">
                            </asp:ChartArea>
                        </ChartAreas>
                        <Legends>
                            <asp:Legend Name="Legend1" Alignment="Center" Docking="Bottom" Font="Trebuchet MS, 7pt,"
                                BackColor="WhiteSmoke">
                            </asp:Legend>
                        </Legends>
                        <Titles>
                            <asp:Title Text="Ongoing Participation" Font="Trebuchet MS, 8pt, style=Bold">
                            </asp:Title>
                        </Titles>
                    </asp:Chart>
                </asp:Panel>
            </td>
            <td style="width: 33%; text-align: center;">
                <asp:Panel runat="server" Style="height: 210px; width: 205px;" ID="Panel3">
                    <asp:Chart ID="chtNewParticipation" runat="server" Height="200px" Width="200px" BackColor="WhiteSmoke">
                        <Series>
                            <asp:Series ChartType="Pie" Name="Series1" IsValueShownAsLabel="true" Legend="Legend1"
                                XValueMember="ChartLegend" YValueMembers="Value">
                            </asp:Series>
                        </Series>
                        <ChartAreas>
                            <asp:ChartArea Name="ChartArea1" BackColor="WhiteSmoke">
                            </asp:ChartArea>
                        </ChartAreas>
                        <Legends>
                            <asp:Legend Name="Legend1" Alignment="Center" Docking="Bottom" Font="Trebuchet MS, 7pt,"
                                BackColor="WhiteSmoke">
                            </asp:Legend>
                        </Legends>
                        <Titles>
                            <asp:Title Text="New Participation" Font="Trebuchet MS, 8pt, style=Bold">
                            </asp:Title>
                        </Titles>
                    </asp:Chart>
                </asp:Panel>
            </td>
        </tr>
        <tr>
            <td style="width: 33%; text-align: center;">
                &nbsp;
            </td>
            <td style="width: 33%; text-align: center;">
                <asp:Panel runat="server" ID="pnlActions" Style="height: 210px; width: 250px;">
                    <table style="height: 150px; width: 245px;">
                        <tr style="height: 100%;">
                            <td style="vertical-align: top;">
                                <asp:Label runat="server" ID="lblNoActions" CssClass="HeaderTitleText" Text="You have no pending actions."></asp:Label><br />
                                <asp:Label runat="server" ID="lblTeamActions" CssClass="HeaderTitleText" Text="You have pending Team Actions."
                                    Visible="false"></asp:Label><br />
                                <asp:Label runat="server" ID="lblAnomalyActions" CssClass="HeaderTitleText" Text="You have pending Anomaly Actions."
                                    Visible="false"></asp:Label><br />
                                <asp:Label runat="server" ID="lblKPIActions" CssClass="HeaderTitleText" Text="You have KPIs pending input."
                                    Visible="false"></asp:Label><br />
                            </td>
                        </tr>
                        <tr style="height: 30px;">
                            <td>
                                <asp:Button runat="server" ID="btnActions" CssClass="Button_Default" Text="My Actions" />
                            </td>
                        </tr>
                    </table>
                </asp:Panel>
            </td>
            <td style="width: 33%; text-align: center;">
                &nbsp;
            </td>
        </tr>
    </table>
    <cc1:RoundedCornersExtender ID="Panel1_RoundedCornersExtender" runat="server" Enabled="True"
        BorderColor="Black" Corners="All" Radius="10" TargetControlID="Panel1">
    </cc1:RoundedCornersExtender>
    <cc1:RoundedCornersExtender ID="RoundedCornersExtender1" runat="server" Enabled="True"
        BorderColor="Black" Corners="All" Radius="10" TargetControlID="Panel2">
    </cc1:RoundedCornersExtender>
    <cc1:RoundedCornersExtender ID="RoundedCornersExtender2" runat="server" Enabled="True"
        BorderColor="Black" Corners="All" Radius="10" TargetControlID="Panel3">
    </cc1:RoundedCornersExtender>
    <cc1:RoundedCornersExtender ID="RoundedCornersExtender3" runat="server" Enabled="True"
        BorderColor="Black" Corners="All" Radius="10" TargetControlID="pnlActions">
    </cc1:RoundedCornersExtender>
    <hr style="width: 99%; color: black; height: 1px">
    <uc1:MenuControl ID="Menucontrol1" runat="server"></uc1:MenuControl>
</asp:Content>
