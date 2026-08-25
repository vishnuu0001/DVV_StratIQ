<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="CultureTranslation2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.CultureTranslation2"
    Title="Culture Translation Maintenance" %>

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
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 85px">
                <asp:Label ID="lblCulture" runat="server" Text="Culture:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlCulture" runat="server" CssClass="DropdownList_Entry" Width="191px">
                </asp:DropDownList>
                <asp:TextBox ID="txtCulture" runat="server" ReadOnly="True" Visible="False" CssClass="Textbox_Display"
                    MaxLength="50" Width="184px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqCulture" runat="server" ErrorMessage="Enter Culture"
                    ControlToValidate="ddlCulture" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="lblKey" runat="server" Text="Key:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandResourceKey" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    TextMode="MultiLine" Width="376px" Rows="1"></asp:TextBox><asp:RequiredFieldValidator
                        ID="RequiredFieldValidator1" runat="server" ControlToValidate="txtExpandResourceKey"
                        Display="None" ErrorMessage="Enter Resource Key" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="lblCultureValue" runat="server" Text="Default Value:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandDefaultValue" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="376px" TextMode="MultiLine" Rows="1"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqDescription" runat="server" ErrorMessage="Enter Value" ControlToValidate="txtExpandDefaultValue"
                        Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="lblTranslationText" runat="server" Text="Translation:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandTranslationText" runat="server" CssClass="Textbox_Entry"
                    MaxLength="100" Width="376px" TextMode="MultiLine" Rows="1"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
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
    <uc1:TransactionHistory ID="TransactionHistory" runat="server" InitialStateExpanded="False"
        TableName="CultureTranslationMaster" Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
