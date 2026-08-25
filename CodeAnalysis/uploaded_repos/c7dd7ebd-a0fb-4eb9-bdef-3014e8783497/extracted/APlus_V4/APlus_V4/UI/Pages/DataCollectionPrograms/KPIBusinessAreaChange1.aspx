<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIBusinessAreaChange1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIBusinessAreaChange1"
    Title="KPI Business Area Change" %>

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
                        <asp:Label ID="lblBA" runat="server">Business Area:</asp:Label>
                    </td>
                    <td>
                        <asp:DropDownList ID="ddlBusinessArea" runat="server" CssClass="DropdownList_Entry"
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
            <asp:GridView runat="server" ID="grdKPI" Width="100%" AutoGenerateColumns="False"
                EmptyDataText="No Records" CssClass="Grid_Default" AlternatingRowStyle-CssClass="alt"
                DataKeyNames="KPIID,KPI,KPIOther,UOM,TeamCategory,SortSequence,Site,PillarAbbrev,BusinessAreaAbbrev,BusinessUnitAbbrev,AreaAbbrev,ResponsibleUser,DailyKPI,Active">
                <Columns>
                    <asp:BoundField DataField="KPIID" HeaderText="KPIID" Visible="false"></asp:BoundField>
                    <asp:BoundField DataField="KPI" HeaderText="KPI"></asp:BoundField>
                    <asp:BoundField DataField="KPIOther" HeaderText="KPI (English)"></asp:BoundField>
                    <asp:BoundField DataField="UOM" HeaderText="UOM"></asp:BoundField>
                    <asp:BoundField DataField="TeamCategory" HeaderText="Category"></asp:BoundField>
                    <asp:BoundField DataField="SortSequence" HeaderText="Seq"></asp:BoundField>
                    <asp:BoundField DataField="Site" HeaderText="Site"></asp:BoundField>
                    <asp:BoundField DataField="PillarAbbrev" HeaderText="PIL"></asp:BoundField>
                    <asp:BoundField DataField="BusinessAreaAbbrev" HeaderText="BA"></asp:BoundField>
                    <asp:BoundField DataField="BusinessUnitAbbrev" HeaderText="BU"></asp:BoundField>
                    <asp:BoundField DataField="AreaAbbrev" HeaderText="Area"></asp:BoundField>
                    <asp:BoundField DataField="ResponsibleUser" HeaderText="Resp User"></asp:BoundField>
                    <asp:BoundField DataField="DailyKPI" HeaderText="Daily KPI"></asp:BoundField>
                    <asp:BoundField DataField="Active" HeaderText="Active"></asp:BoundField>
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
                    <asp:Button ID="btnProcess" runat="server" CssClass="Button_Variable" Text="Change Business Area"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
