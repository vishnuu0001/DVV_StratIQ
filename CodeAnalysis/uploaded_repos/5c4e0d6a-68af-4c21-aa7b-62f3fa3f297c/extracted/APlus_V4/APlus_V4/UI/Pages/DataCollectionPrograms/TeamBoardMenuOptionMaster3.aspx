<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamBoardMenuOptionMaster3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamBoardMenuOptionMaster3"
    Title="Team Board Menu Option Master" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <CC1:MasterControl ID="mcTeam" runat="server" ProgramMode="TeamsMode" ShowAdd="False"
        ShowDelete="False" ShowEdit="False" ShowView="False" NewLinkCaption="Team" RedirectProgramName="TeamsMaintenance2"
        FormName="Teams Maintenance" ProgramName="TeamsMaintenance" CommandText="spSelTeamSummary"
        ShowExport="false" AlternatingRows="True" ShowRowCount="False" Translate="True"
        PrimaryControl="false" ShowExit="False">
        <GridColumns>
            <CC1:MasterControlField ShowReturns="False" DataField="TeamID" HeaderText="TeamID"
                Visible="false" />
            <CC1:MasterControlField ShowReturns="False" DataField="TeamNameOther" HeaderText="Team Name" />
            <CC1:MasterControlField ShowReturns="False" DataField="Site" HeaderText="Site" />
            <CC1:MasterControlField ShowReturns="False" DataField="PillarAbbrev" HeaderText="Pillar" />
            <CC1:MasterControlField ShowReturns="False" DataField="BusinessAreaAbbrev" HeaderText="BA" />
            <CC1:MasterControlField ShowReturns="False" DataField="BusinessUnitAbbrev" HeaderText="BU" />
            <CC1:MasterControlField ShowReturns="False" DataField="Route" HeaderText="Route" />
            <CC1:MasterControlField ShowReturns="False" DataField="OPI" HeaderText="OPI" />
            <CC1:MasterControlField ShowReturns="False" DataField="SavingsTracker" HeaderText="Savings Tracker" />
            <CC1:MasterControlField ShowReturns="False" DataField="TeamLeader" HeaderText="Leader" />
            <CC1:MasterControlField ShowReturns="False" DataField="TeamStatusDescription" HeaderText="Status" />
            <CC1:MasterControlField ShowReturns="False" DataField="TeamType" HeaderText="Type" />
            <CC1:MasterControlField ShowReturns="False" DataField="TeamStartDate" HeaderText="Start"
                HtmlEncode="false" />
            <CC1:MasterControlField ShowReturns="False" DataField="TeamFinishDate" HeaderText="Finish"
                HtmlEncode="false" />
            <CC1:MasterControlField ShowReturns="False" DataField="Duration" HeaderText="Duration" />
            <CC1:MasterControlField ShowReturns="False" DataField="EarliestPlanDate" HeaderText="Earliest Plan Date"
                HtmlEncode="false" />
            <CC1:MasterControlField ShowReturns="False" DataField="LatestPlanDate" HeaderText="Latest Plan Date"
                HtmlEncode="false" />
            <CC1:MasterControlField ShowReturns="False" DataField="LastMeetingDate" HeaderText="Last Meeting Date"
                HtmlEncode="false" />
        </GridColumns>
    </CC1:MasterControl>
    <br />
    <hr style="width: 99%; color: black; height: 1px">
    <br />
    <asp:Label ID="lblMenuOptions" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Team Board Defaults</asp:Label>
    <asp:GridView runat="server" ID="gvMenuOptions" Width="100%" AutoGenerateColumns="False"
        SkinID="GridView" DataKeyNames="TeamBoardMenuDefaultsID,BoardDefault">
        <Columns>
            <asp:TemplateField>
                <ItemTemplate>
                    <asp:CheckBox ID="chkSelected" runat="server" />
                </ItemTemplate>
            </asp:TemplateField>
            <asp:BoundField DataField="TeamBoardMenuDefaultsID" HeaderText="TeamBoardMenuDefaultsID"
                Visible="false"></asp:BoundField>
            <asp:BoundField DataField="BoardDefault" HeaderText="BoardDefault" Visible="false">
            </asp:BoundField>
            <asp:BoundField DataField="BoardColumn" HeaderText="Col"></asp:BoundField>
            <asp:BoundField DataField="BoardRow" HeaderText="Row"></asp:BoundField>
            <asp:BoundField DataField="RCSequence" HeaderText="Seq"></asp:BoundField>
            <asp:BoundField DataField="BoardDescription" HeaderText="Description"></asp:BoundField>
            <asp:BoundField DataField="LinkFileURL" HeaderText="File"></asp:BoundField>
        </Columns>
    </asp:GridView>
    <br />
    <asp:Label ID="lblOptions" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Other Menu Options</asp:Label>
    <br />
    <asp:CheckBox runat="server" ID="chkRoute" Text="Create links to Route Tools" />
    <br />
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
