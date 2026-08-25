<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamBusinessUnitChange1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamBusinessUnitChange1"
    Title="Team Business Unit Change" %>

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
                    <td>
                        <asp:Label ID="lblBU" runat="server">Business Unit:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlBusinessUnit" runat="server" CssClass="DropdownList_Entry"
                            Width="180px">
                        </asp:DropDownList>
                    </td>
                </tr>
                <tr>
                    <td>
                        <asp:Button ID="btnApply" runat="server" CausesValidation="False" CssClass="Button_Default"
                            Text="Apply" />
                    </td>
                    <td>
                        &nbsp;
                    </td>
                </tr>
            </table>
            <br />
            <asp:GridView runat="server" ID="grdTeam" Width="100%" AutoGenerateColumns="False"
                EmptyDataText="No Records" CssClass="Grid_Default" AlternatingRowStyle-CssClass="alt"
                DataKeyNames="TeamID,Team,TeamName,Site,PillarAbbrev,BusinessAreaAbbrev,BusinessUnitAbbrev,TeamStartDate,TeamFinishDate,Duration,TeamStatusDescription,TeamType">
                <Columns>
                    <asp:BoundField DataField="TeamID" HeaderText="TeamID" Visible="false"></asp:BoundField>
                    <asp:BoundField DataField="Team" HeaderText="Team"></asp:BoundField>
                    <asp:BoundField DataField="TeamName" HeaderText="Team Name"></asp:BoundField>
                    <asp:BoundField DataField="Site" HeaderText="Site"></asp:BoundField>
                    <asp:BoundField DataField="PillarAbbrev" HeaderText="PIL"></asp:BoundField>
                    <asp:BoundField DataField="BusinessAreaAbbrev" HeaderText="BA"></asp:BoundField>
                    <asp:BoundField DataField="BusinessUnitAbbrev" HeaderText="BU"></asp:BoundField>
                    <asp:BoundField DataField="DeptNumber" HeaderText="Dept"></asp:BoundField>
                    <asp:BoundField DataField="TeamStartDate" HeaderText="Team Start" DataFormatString="{0:yyyy/MM/dd}">
                    </asp:BoundField>
                    <asp:BoundField DataField="TeamFinishDate" HeaderText="Team Finish" DataFormatString="{0:yyyy/MM/dd}">
                    </asp:BoundField>
                    <asp:BoundField DataField="Duration" HeaderText="Duration"></asp:BoundField>
                    <asp:BoundField DataField="TeamStatusDescription" HeaderText="Status"></asp:BoundField>
                    <asp:BoundField DataField="TeamType" HeaderText="Type"></asp:BoundField>
                    <asp:TemplateField>
                        <ItemTemplate>
                            <asp:CheckBox ID="chkSelected" runat="server" />
                        </ItemTemplate>
                    </asp:TemplateField>
                </Columns>
                <AlternatingRowStyle CssClass="alt" />
                <EmptyDataRowStyle ForeColor="Red" Font-Bold="true" />
            </asp:GridView>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
    <br />
    <asp:Panel ID="pnlExit" runat="server">
        <table style="width: 95%">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td style="text-align: right">
                    <asp:Button ID="btnProcess" runat="server" CssClass="Button_Variable" Text="Change Business Unit"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
