<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="PillarsMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.PillarsMaster2"
    Title="Pillar Maintenance" %>

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
            <td style="width: 120px">
                <asp:Label ID="lblPillarAbbrev" runat="server" Text="Pillar Abbreviation:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPillarAbbrev" runat="server" CssClass="Textbox_Entry" MaxLength="3"
                    Width="31px"></asp:TextBox><asp:RequiredFieldValidator ID="reqPillarAbbrev" runat="server"
                        ErrorMessage="Enter Pillar Abbreviation" ControlToValidate="txtPillarAbbrev"
                        Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblPillar" runat="server" Text="Pillar:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPillar" runat="server" CssClass="Textbox_Entry" MaxLength="40"
                    Width="259px"></asp:TextBox><asp:RequiredFieldValidator ID="reqPillar" runat="server"
                        ErrorMessage="Enter Pillar " ControlToValidate="txtPillar" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px; vertical-align: top; text-align: left;">
                <asp:Label ID="lblPillarDefinition" runat="server" Text="Pillar Definition:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandPillarDefinition" runat="server" CssClass="Textbox_Entry"
                    MaxLength="1000" Width="826px" TextMode="MultiLine"></asp:TextBox>
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
