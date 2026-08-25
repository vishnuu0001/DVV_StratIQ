<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerPlanSavings1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerPlanSavings1"
    Title="Master Plan Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <CC1:MasterControl ID="mcTrackerPlan" runat="server" ShowAdd="False" ShowDelete="True"
        ShowEdit="True" NewLinkCaption="Tracker Plan Savings" RedirectProgramName="TrackerPlanSavings2"
        FormName="Tracker Plan Maintenance" ProgramName="TrackerPlanSavings1" CommandText="spSelTrackerPlan"
        ProgramMode="TrackerPlanSavingsMode" AlternatingRows="false" UseScrollingColor="false"
        Translate="True" PrimaryControl="False" ShowExit="False" ShowExport="False" ShowView="False">
        <GridColumns>
            <CC1:MasterControlField Visible="False" DataField="TrackerPlanID" HeaderText="TrackerPlanID" />
            <CC1:MasterControlField DataField="Site" HeaderText="Site" />
            <CC1:MasterControlField DataField="Pillar" HeaderText="Pillar" />
            <CC1:MasterControlField DataField="BusinessArea" HeaderText="Business Area" />
            <CC1:MasterControlField DataField="BusinessUnit" HeaderText="Business Unit" />
            <CC1:MasterControlField DataField="SavingsCategory" HeaderText="Category" />
            <CC1:MasterControlField DataField="Active" HeaderText="Active" />
            <CC1:MasterControlField DataField="PlanSavings" HeaderText="Cur Plan" DataFormatString="{0:0.##}" />
            <CC1:MasterControlField DataField="StretchSavings" HeaderText="Cur Stretch" DataFormatString="{0:0.##}" />
        </GridColumns>
    </CC1:MasterControl>
    <br />
    <br />
    <asp:Table ID="tblMasterPlan" runat="server" Width="100%" GridLines="Both" CellPadding="1"
        CellSpacing="0" BorderColor="Black" BorderWidth="1" BorderStyle="Solid" BackColor="White">
    </asp:Table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" style="width: 640px;" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 120px" align="left">
                    <p>
                        <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                            Text="OK"></asp:Button></p>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
</asp:Content>
