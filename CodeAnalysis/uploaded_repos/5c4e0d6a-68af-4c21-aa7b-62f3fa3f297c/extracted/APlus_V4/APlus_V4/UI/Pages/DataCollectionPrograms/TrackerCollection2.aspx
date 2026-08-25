<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerCollection2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerCollection2"
    Title="Tracker Collection Maintenance" %>

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
            <td style="width: 145px">
                <asp:Label ID="lblSavingsTracker" runat="server" Text="Savings Tracker:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlTracker" runat="server" Width="258px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtTracker" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTracker" runat="server" ErrorMessage="Select Tracker"
                    ControlToValidate="ddlTracker" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 145px">
                <asp:Label ID="lblSavingsType" runat="server" Text="Savings Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlTrackerType" runat="server" Width="258px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtTrackerType" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTrackerType" runat="server" ErrorMessage="Select Savings Type"
                    ControlToValidate="ddlTrackerType" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 145px">
                <asp:Label ID="lblSavingsTerm" runat="server" Text="Savings Term:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSavingsType" runat="server" Width="258px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSavingsType" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSavingsType" runat="server" ErrorMessage="Select Savings Term"
                    ControlToValidate="ddlSavingsType" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 145px">
                <asp:Label ID="lblManualEntered" runat="server" Text="Savings is Manually Entered:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="cbNoFormula" runat="server"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 145px">
                <asp:Label ID="lblFormula" runat="server" Text="Formula:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:TextBox ID="txtExpandFormula" runat="server" CssClass="Textbox_Entry" Width="400px"
                    MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>&nbsp;<img
                        alt="Show Data Elements Listing..." id="imgElements" style="cursor: hand;" src="~/images/MoreInformation.jpg"
                        name="imgElements" border="0" runat="server" />
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
