<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SavingsTracker1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.SavingsTracker1"
    Title="Savings Tracker" %>

<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="False" ShowDelete="False"
        ShowEdit="False" NewLinkCaption="Savings Tracker" RedirectProgramName="TrackerMaster2"
        FormName="Tracker Maintenance" ProgramName="TrackerMaster1" CommandText="spSelTracker"
        ProgramMode="TrackerMode" AlternatingRows="True" PrimaryControl="false" ShowExit="False"
        ShowExport="False" ShowRowCount="False" ShowView="False" Translate="True">
        <gridcolumns>
            <CC1:MasterControlField DataField="Team" HeaderText="Team" />
            <CC1:MasterControlField DataField="Tracker" HeaderText="Savings Tracker" />
            <CC1:MasterControlField DataField="Site" HeaderText="Site" />
            <CC1:MasterControlField DataField="PillarAbbrev" HeaderText="Pillar" />
            <CC1:MasterControlField DataField="BusinessAreaAbbrev" HeaderText="Bus Area" />
            <CC1:MasterControlField DataField="BusinessUnitAbbrev" HeaderText="Bus Unit" />
            <CC1:MasterControlField DataField="SavingsCategory" HeaderText="Category" />
            <CC1:MasterControlField DataField="TrackerValueUOM" HeaderText="UOM" />
            <CC1:MasterControlField DataField="Historic" ItemStyle-HorizontalAlign="Right" HeaderText="Historic"
                DataFormatString="{0:0.####}">
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
            <CC1:MasterControlField DataField="Target" ItemStyle-HorizontalAlign="Right" HeaderText="Target"
                DataFormatString="{0:0.####}">
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
            <CC1:MasterControlField DataField="StartPeriod" HeaderText="Start" DataFormatString="{0:yyyy/MM/dd}" />
            <CC1:MasterControlField DataField="Active" HeaderText="Active" />
            <CC1:MasterControlField DataField="LastValueDate" HeaderText="Last Value" DataFormatString="{0:yyyy/MM/dd}" />
            <CC1:MasterControlField DataField="CurrencyAbbrev" HeaderText="Cur" />
            <CC1:MasterControlField DataField="PreviousYearSavings" HeaderText="Prev Year" DataFormatString="{0:0.00}"
                HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
            <CC1:MasterControlField DataField="LastYearSavings" HeaderText="Last Year" DataFormatString="{0:0.00}"
                HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
            <CC1:MasterControlField DataField="YearSavings" HeaderText="Current Year" DataFormatString="{0:0.00}"
                HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
            <CC1:MasterControlField DataField="TotalSavings" HeaderText="Total" DataFormatString="{0:0.00}"
                HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
        </gridcolumns>
    </CC1:MasterControl>
    <br />
    <br />
    <CC1:MasterControl ID="mcTotals" runat="server" ShowAdd="False" ShowDelete="False"
        ShowEdit="False" NewLinkCaption="Savings Tracker" RedirectProgramName="TrackerMaster2"
        FormName="Tracker Maintenance" ProgramName="TrackerMaster1" CommandText="spSelSavingsTrackerSavingsTotals"
        ProgramMode="TrackerMode" AlternatingRows="True" PrimaryControl="False" ShowExit="False"
        ShowExport="False" ShowRowCount="False" ShowView="False" Translate="True">
        <gridcolumns>
            <CC1:MasterControlField DataField="SavingsType" HeaderText="Savings Type" />
            <CC1:MasterControlField DataField="PreviousYearSavings" HeaderText="Prev Year" DataFormatString="{0:0.00}"
                HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
            <CC1:MasterControlField DataField="LastYearSavings" HeaderText="Last Year" DataFormatString="{0:0.00}"
                HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
            <CC1:MasterControlField DataField="YearSavings" HeaderText="Current Year" DataFormatString="{0:0.00}"
                HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
            <CC1:MasterControlField DataField="TotalSavings" HeaderText="Total" DataFormatString="{0:0.00}"
                HeaderStyle-HorizontalAlign="Right" ItemStyle-HorizontalAlign="Right">
                <HeaderStyle HorizontalAlign="Right"></HeaderStyle>
                <ItemStyle HorizontalAlign="Right"></ItemStyle>
            </CC1:MasterControlField>
        </gridcolumns>
    </CC1:MasterControl>
    <br />
    <br />
    <asp:Table ID="tblSavingsTracker" runat="server" Width="100%" GridLines="Both" CellPadding="1"
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
    <asp:Panel ID="pnlConfirm" runat="server" Visible="false">
        <table id="Table1" style="width: 640px;" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 150px" align="left">
                    <p>
                        <asp:Button ID="btnExisting" runat="server" CssClass="Button_Variable" EnableViewState="False"
                            Text="Existing Formulas"></asp:Button></p>
                </td>
                <td align="left" style="width: 177px">
                    <asp:Button ID="btnCurrent" runat="server" CssClass="Button_Variable" EnableViewState="False"
                        Text="Current Formulas" />
                </td>
                <td align="left">
                    <asp:Button ID="btnCancelConfirm" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Cancel" />
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
    <br />
    <asp:Panel runat="server" ID="pnlMasterControls">
        <table style="width: 100%">
            <tr>
                <td>
                    <CC1:MasterControl ID="mcVariables" runat="server" ShowAdd="False" ShowDelete="False"
                        ShowEdit="False" NewLinkCaption="Tracker Variable" RedirectProgramName="TrackerVariables2"
                        FormName="Tracker Variable Maintenance" ProgramName="TrackerVariables1" CommandText="spSelTrackerVariablesByTrackerID"
                        ProgramMode="TrackerVariableMode" AlternatingRows="True" PrimaryControl="True"
                        ShowExit="False" ShowExport="False" ShowView="False" ShowFunctionButtonOne="true"
                        FunctionButtonOneLabel="Tracker Variable Maintenance" HideEmptyGrid="true" Translate="True">
                        <gridcolumns>
                            <CC1:MasterControlField DataField="TrackerVariable" HeaderText="Variable" />
                            <CC1:MasterControlField DataField="VariableValue" HeaderText="Value" />
                            <CC1:MasterControlField DataField="Site" HeaderText="Site" />
                            <CC1:MasterControlField DataField="LastUserID" HeaderText="Last Modified By" ShowReturns="true" />
                            <CC1:MasterControlField DataField="LastDateTime" HeaderText="Last Modified" ShowReturns="true"
                                HtmlEncode="false" />
                        </gridcolumns>
                    </CC1:MasterControl>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="Validationsummary1" runat="server" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
