<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamBusinessUnitChange2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamBusinessUnitChange2"
    Title="Team Business Unit Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <CC1:MasterControl ID="mcTeam" runat="server" ShowAdd="False" ShowDelete="False"
        ShowEdit="False" NewLinkCaption="Team" RedirectProgramName="TeamBusinessUnitChange2"
        FormName="Business Area" ProgramName="TeamBusinessUnitChange2" CommandText="spSelTeamsByTeamList"
        ProgramMode="Mode" AlternatingRows="True" PrimaryControl="False" ShowExit="False"
        ShowExport="False" ShowRowCount="False" ShowView="False" Translate="True">
        <GridColumns>
            <CC1:MasterControlField DataField="TeamID" HeaderText="TeamID" Visible="false" />
            <CC1:MasterControlField DataField="Team" HeaderText="Team" />
            <CC1:MasterControlField DataField="TeamName" HeaderText="Team Name" />
            <CC1:MasterControlField DataField="Site" HeaderText="Site" />
            <CC1:MasterControlField DataField="PillarAbbrev" HeaderText="Pillar" />
            <CC1:MasterControlField DataField="BusinessAreaAbbrev" HeaderText="BA" />
            <CC1:MasterControlField DataField="BusinessUnitAbbrev" HeaderText="BU" />
            <CC1:MasterControlField DataField="TeamStartDate" HeaderText="Team Start" DataFormatString="{0:yyyy/MM/dd}" />
            <CC1:MasterControlField DataField="TeamFinishDate" HeaderText="Team Finish" DataFormatString="{0:yyyy/MM/dd}" />
            <CC1:MasterControlField DataField="Duration" HeaderText="Duration" />
            <CC1:MasterControlField DataField="TeamStatusDescription" HeaderText="Status" />
            <CC1:MasterControlField DataField="TeamType" HeaderText="Type" />
        </GridColumns>
    </CC1:MasterControl>
    <br />
    <table>
        <tr>
            <td>
                <asp:Label ID="lblBU" runat="server">Change To Business Unit:</asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessUnit" runat="server" CssClass="DropdownList_Entry"
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
