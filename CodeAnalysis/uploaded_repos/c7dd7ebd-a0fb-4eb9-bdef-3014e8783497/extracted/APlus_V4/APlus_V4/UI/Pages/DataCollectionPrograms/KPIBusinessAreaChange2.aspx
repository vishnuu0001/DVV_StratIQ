<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIBusinessAreaChange2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIBusinessAreaChange2"
    Title="Business Area Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <CC1:MasterControl ID="mcKPI" runat="server" ShowAdd="False" ShowDelete="False" ShowEdit="False"
        NewLinkCaption="KPI" RedirectProgramName="KPIBusinessAreaChange2" FormName="Business Area"
        ProgramName="KPIBusinessAreaChange2" CommandText="spSelKPIMasterByKPIList" ProgramMode="Mode"
        AlternatingRows="True" PrimaryControl="False" ShowExit="False" ShowExport="False"
        ShowRowCount="False" ShowView="False" Translate="True">
        <GridColumns>
            <CC1:MasterControlField DataField="KPIID" HeaderText="KPIID" Visible="false" />
            <CC1:MasterControlField DataField="KPI" HeaderText="KPI" />
            <CC1:MasterControlField DataField="KPIOther" HeaderText="KPI (English)" />
            <CC1:MasterControlField DataField="UOM" HeaderText="UOM" />
            <CC1:MasterControlField DataField="TeamCategory" HeaderText="Category" />
            <CC1:MasterControlField DataField="SortSequence" HeaderText="Seq" />
            <CC1:MasterControlField DataField="Site" HeaderText="Site" />
            <CC1:MasterControlField DataField="PillarAbbrev" HeaderText="PIL" />
            <CC1:MasterControlField DataField="BusinessAreaAbbrev" HeaderText="BA" />
            <CC1:MasterControlField DataField="BusinessUnitAbbrev" HeaderText="BU" />
            <CC1:MasterControlField DataField="AreaAbbrev" HeaderText="Area" />
            <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Resp User" />
            <CC1:MasterControlField DataField="DailyKPI" HeaderText="Daily KPI" />
            <CC1:MasterControlField DataField="Active" HeaderText="Active" />
        </GridColumns>
    </CC1:MasterControl>
    <br />
    <table>
        <tr>
            <td>
                <asp:Label ID="lblBU" runat="server">Change To Business Area:</asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessArea" runat="server" CssClass="DropdownList_Entry"
                    Width="180px">
                </asp:DropDownList>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
