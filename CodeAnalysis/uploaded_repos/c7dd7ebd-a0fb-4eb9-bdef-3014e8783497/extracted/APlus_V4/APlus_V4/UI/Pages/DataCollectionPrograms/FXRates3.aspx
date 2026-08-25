<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="FXRates3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.FXRates3"
    Title="FX Rates Maintenance" %>

<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <CC1:MasterControl ID="mcFXRateElement" runat="server" ShowView="False" ShowAdd="False"
        ShowDelete="False" ShowEdit="False" NewLinkCaption="FX Rate" RedirectProgramName="FXRates3"
        FormName="FX Rate Maintenance" ProgramName="FXRates2" PrimaryControl="false"
        CommandText="spSelFXRateElements" ProgramMode="FXRateMode" AlternatingRows="True"
        UseScrollingColor="False">
        <GridColumns>
            <CC1:MasterControlField Visible="False" DataField="FXRateID" HeaderText="FXRateID" />
            <CC1:MasterControlField DataField="FXRateElement" HeaderText="Element" />
            <CC1:MasterControlField DataField="FXRateFrom" HeaderText="From" />
            <CC1:MasterControlField DataField="FXRateTo" HeaderText="To" />
            <CC1:MasterControlField DataField="FXRatePeriod" HeaderText="Cur Period" DataFormatString="{0:yyyy/MM/dd}" />
            <CC1:MasterControlField DataField="FXRate" HeaderText="Cur Rate" />
        </GridColumns>
    </CC1:MasterControl>
    <hr width="100%" />
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblPeriod" runat="server" Text="Period:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPeriod" runat="server" CssClass="Textbox_Entry" MaxLength="30"
                    Width="100px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqPeriod" runat="server" ErrorMessage="Enter Period"
                    ControlToValidate="txtPeriod" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblRate" runat="server" Text="Rate:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRate" runat="server" CssClass="Textbox_Entry" MaxLength="9" Width="50px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqRate" runat="server" ErrorMessage="Enter Rate"
                    ControlToValidate="txtRate" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblLastUpdated" runat="server" Text="Last Updated:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLastUpdated" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="150px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
