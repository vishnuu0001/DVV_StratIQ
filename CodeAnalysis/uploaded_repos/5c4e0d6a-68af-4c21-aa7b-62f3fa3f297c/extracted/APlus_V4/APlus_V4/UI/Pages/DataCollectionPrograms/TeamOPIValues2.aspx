<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIValues2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIValues2"
    Title="OPI Data Entry" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 111px">
                <asp:Label ID="lblOPIDescription" runat="server" Text="OPI Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandOPIDescription" runat="server" Height="0px" TextMode="MultiLine"
                    Rows="1" ReadOnly="True" Width="325px" MaxLength="100" CssClass="Textbox_Display"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 111px">
                <asp:Label ID="lblDate" runat="server" Text="Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOPIValueDateTime" runat="server" Width="82px" MaxLength="12"
                    CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtOPIValueDateTime_CalendarExtender" runat="server" PopupButtonID="imgOPIValueDateTime"
                    TargetControlID="txtOPIValueDateTime" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgOPIValueDateTime" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqValueDateTime" runat="server" ErrorMessage="Enter a Value Date"
                    ControlToValidate="txtOPIValueDateTime" Display="None"></asp:RequiredFieldValidator>
                <asp:CompareValidator ID="reqValidDateTime" runat="server" Display="None" ControlToValidate="txtOPIValueDateTime"
                    ErrorMessage="Invalid OPI Date" Type="Date" Operator="DataTypeCheck"></asp:CompareValidator>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlTime" runat="server">
        <table class="Table_Default" id="tbTime" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 111px">
                    <asp:Label ID="lblTime" runat="server" Text="Time:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtOPIValueTime" runat="server" CssClass="Textbox_Entry" MaxLength="7"
                        Width="43px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqValueTime" runat="server" Display="None" ControlToValidate="txtOPIValueTime"
                        ErrorMessage="Enter a Value Time" Enabled="False"></asp:RequiredFieldValidator>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlAttribute1" runat="server">
        <table class="Table_Default" id="tbAttribute1" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 111px">
                    <asp:Label ID="lblAttribute1" runat="server" Text="Label" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtAttribute1" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                        Width="200px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqA1" runat="server" Display="None" ControlToValidate="txtAttribute1"
                        ErrorMessage="Enter Attribute" Enabled="False"></asp:RequiredFieldValidator>
                    <asp:RegularExpressionValidator ID="reqValidA1" runat="server" Display="None" ControlToValidate="txtAttribute1"
                        ErrorMessage="Invalid OPI Value Entry"></asp:RegularExpressionValidator>
                    <asp:TextBox ID="lblOldA1" runat="server" CssClass="Textbox_Display" MaxLength="50"
                        Width="72px" ReadOnly="True" Visible="False"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlAttribute2" runat="server">
        <table class="Table_Default" id="tbAttribute2" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 111px">
                    <asp:Label ID="lblAttribute2" runat="server" CssClass="Label_Left_8PT" Text="Label"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtAttribute2" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                        Width="200px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqA2" runat="server" Display="None" ControlToValidate="txtAttribute2"
                        ErrorMessage="Enter Attribute" Enabled="False"></asp:RequiredFieldValidator>
                    <asp:RegularExpressionValidator ID="reqValidA2" runat="server" Display="None" ControlToValidate="txtAttribute2"
                        ErrorMessage="Invalid OPI Value Entry"></asp:RegularExpressionValidator>
                    <asp:TextBox ID="lblOldA2" runat="server" CssClass="Textbox_Display" MaxLength="50"
                        Width="72px" ReadOnly="True" Visible="False"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlAttribute3" runat="server">
        <table class="Table_Default" id="tbAttribute3" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 111px">
                    <asp:Label ID="lblAttribute3" runat="server" CssClass="Label_Left_8PT" Text="Label"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtAttribute3" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                        Width="200px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqA3" runat="server" Display="None" ControlToValidate="txtAttribute3"
                        ErrorMessage="Enter Attribute" Enabled="False"></asp:RequiredFieldValidator>
                    <asp:RegularExpressionValidator ID="reqValidA3" runat="server" Display="None" ControlToValidate="txtAttribute3"
                        ErrorMessage="Invalid OPI Value Entry"></asp:RegularExpressionValidator>
                    <asp:TextBox ID="lblOldA3" runat="server" CssClass="Textbox_Display" MaxLength="50"
                        Width="72px" ReadOnly="True" Visible="False"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlAttribute4" runat="server">
        <table class="Table_Default" id="tbAttribute4" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 111px">
                    <asp:Label ID="lblAttribute4" runat="server" CssClass="Label_Left_8PT" Text="Label"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtAttribute4" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                        Width="200px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqA4" runat="server" Display="None" ControlToValidate="txtAttribute4"
                        ErrorMessage="Enter Attribute" Enabled="False"></asp:RequiredFieldValidator>
                    <asp:RegularExpressionValidator ID="reqValidA4" runat="server" Display="None" ControlToValidate="txtAttribute4"
                        ErrorMessage="Invalid OPI Value Entry"></asp:RegularExpressionValidator>
                    <asp:TextBox ID="lblOldA4" runat="server" CssClass="Textbox_Display" MaxLength="50"
                        Width="72px" ReadOnly="True" Visible="False"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlAttribute5" runat="server">
        <table class="Table_Default" id="tbAttribute5" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 111px; height: 22px">
                    <asp:Label ID="lblAttribute5" runat="server" CssClass="Label_Left_8PT" Text="Label"></asp:Label>
                </td>
                <td style="height: 22px">
                    <asp:TextBox ID="txtAttribute5" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                        Width="200px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqA5" runat="server" Display="None" ControlToValidate="txtAttribute5"
                        ErrorMessage="Enter Attribute" Enabled="False"></asp:RequiredFieldValidator>
                    <asp:RegularExpressionValidator ID="reqValidA5" runat="server" Display="None" ControlToValidate="txtAttribute5"
                        ErrorMessage="Invalid OPI Value Entry"></asp:RegularExpressionValidator>
                    <asp:TextBox ID="lblOldA5" runat="server" CssClass="Textbox_Display" MaxLength="50"
                        Width="72px" ReadOnly="True" Visible="False"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlAttribute6" runat="server">
        <table class="Table_Default" id="tbAttribute6" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 112px">
                    <asp:Label ID="lblAttribute6" runat="server" CssClass="Label_Left_8PT" Text="Label"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtAttribute6" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                        Width="200px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqA6" runat="server" Display="None" ControlToValidate="txtAttribute6"
                        ErrorMessage="Enter Attribute" Enabled="False"></asp:RequiredFieldValidator>
                    <asp:RegularExpressionValidator ID="reqValidA6" runat="server" Display="None" ControlToValidate="txtAttribute6"
                        ErrorMessage="Invalid OPI Value Entry"></asp:RegularExpressionValidator>
                    <asp:TextBox ID="lblOldA6" runat="server" CssClass="Textbox_Display" MaxLength="50"
                        Width="72px" ReadOnly="True" Visible="False"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <table class="Table_Default" id="Table2" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblOPIValue" runat="server" Text="OPI Value:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOPIValue" runat="server" Width="100px" MaxLength="12" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqOPIValue" runat="server" ErrorMessage="Enter OPI Value" ControlToValidate="txtOPIValue"
                    Display="None"></asp:RequiredFieldValidator><asp:RegularExpressionValidator ID="reqValidOPIValue"
                        runat="server" ErrorMessage="Invalid OPI Value Entry" ControlToValidate="txtOPIValue"
                        Display="None"></asp:RegularExpressionValidator>&nbsp;<asp:TextBox ID="txtOPIUOM"
                            runat="server" ReadOnly="True" Width="120px" MaxLength="50" CssClass="Textbox_Display"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblCost" runat="server" Text="Cost:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtCost" runat="server" Width="100px" MaxLength="9" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqCost" runat="server" ErrorMessage="Enter OPI Cost" ControlToValidate="txtCost"
                    Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblNotes" runat="server" Text="Notes:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandNotes" runat="server" Height="0px" TextMode="MultiLine"
                    Rows="1" Width="325px" MaxLength="100" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlMaint" runat="server">
        <table class="Table_Default" id="tbMaint" cellspacing="2" cellpadding="2" border="0">
            <tr>
                <td style="width: 112px">
                    <asp:Label ID="lblMaintenanceUserID" runat="server" Text="Maintenance UserID:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td style="width: 80px">
                    <asp:TextBox ID="txtMaintenanceUserID" runat="server" CssClass="Textbox_Display"
                        MaxLength="50" Width="69px" ReadOnly="True"></asp:TextBox>
                </td>
                <td style="width: 95px">
                    <asp:Label ID="lblMaintenanceDate" runat="server" Text="Maintenance Date:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtMaintenanceDate" runat="server" CssClass="Textbox_Display" MaxLength="50"
                        Width="120px" ReadOnly="True"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td>
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
