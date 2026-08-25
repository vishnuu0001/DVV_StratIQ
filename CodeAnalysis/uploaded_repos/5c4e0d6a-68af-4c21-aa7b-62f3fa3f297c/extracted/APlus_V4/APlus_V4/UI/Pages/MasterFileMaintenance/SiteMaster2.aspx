<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SiteMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.SiteMaster2"
    Title="Site Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1">
        <tr>
            <td class="style1">
                <asp:Label ID="Label2" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" Width="250px" MaxLength="50" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqSite" runat="server" Display="None" ControlToValidate="txtSite" ErrorMessage="Enter a Site"
                    CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label1" runat="server" Text="Folder Icon Link:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandFolderLink" runat="server" CssClass="Textbox_Entry" MaxLength="200"
                    Width="440px" Height="28px" TextMode="MultiLine"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqFolderLink" runat="server" ErrorMessage="Enter a Folder Link"
                    ControlToValidate="txtExpandFolderLink" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label3" runat="server" Text="AD Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtADSite" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="250px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqADSite" runat="server" ErrorMessage="Enter an ADSite"
                    ControlToValidate="txtADSite" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label7" runat="server" Text="Site Abbrev:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSiteAbbrev" runat="server" CssClass="Textbox_Entry" MaxLength="3"
                    Width="83px" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSiteAbbrev" runat="server" ErrorMessage="Enter Site Abbrev"
                    ControlToValidate="txtSiteAbbrev" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label8" runat="server" Text="Currency Abbrev:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtCurrencyAbbrev" runat="server" CssClass="Textbox_Entry" MaxLength="3"
                    Width="83px" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqCurrencyAbbrev" runat="server" ErrorMessage="Enter Currency Abbrev"
                    ControlToValidate="txtCurrencyAbbrev" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label4" runat="server" Text="Time Offset Hours:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTimeOffset" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTimeOffset" runat="server" ErrorMessage="Enter Time Offset in Hours"
                    ControlToValidate="txtTimeOffset" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label6" runat="server" Text="Active:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckActive" runat="server" CssClass="Checkbox_Default" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                &nbsp;
            </td>
            <td>
                &nbsp;
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label5" runat="server" Text="Team Action:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamAction" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label17" runat="server" Text="Team Action Reminder:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamActionReminder" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label16" runat="server" Text="KPI Value Entry:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtKPIValue" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label15" runat="server" Text="KPI Value Reminder:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtKPIValueReminder" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label14" runat="server" Text="KPI Target Entry:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtKPITarget" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label13" runat="server" Text="KPI Target Reminder:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtKPITargetReminder" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label12" runat="server" Text="Anomaly Pending:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAnomalyPending" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label11" runat="server" Text="Anomaly Pending Reminder:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAnomalyPendingReminder" runat="server" CssClass="Textbox_Entry"
                    MaxLength="2" Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label10" runat="server" Text="Anomaly Actions:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAnomalyActions" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="Label9" runat="server" Text="Anomaly Actions Reminder:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAnomalyActionsReminder" runat="server" CssClass="Textbox_Entry"
                    MaxLength="2" Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label18" runat="server" Text="Team Meetings:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamMeetings" runat="server" CssClass="Textbox_Entry" MaxLength="2"
                    Width="45px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label19" runat="server" Text="Anomaly SGI:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAnomalySGI" runat="server" CssClass="Checkbox_Default" />
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="OK"></asp:Button>
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
                <td align="left">
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
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 150px;
        }
    </style>
</asp:Content>
