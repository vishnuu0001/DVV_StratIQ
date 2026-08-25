<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="Routes2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Routes2"
    Title="Routes Maintenance" %>

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
            <td style="width: 150px">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Route Abbreviation:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRouteAbbrev" runat="server" CssClass="Textbox_Entry" MaxLength="5"
                    Width="45px"></asp:TextBox><asp:RequiredFieldValidator ID="reqRouteAbbrev" runat="server"
                        ErrorMessage="Enter Route Abbreviation" ControlToValidate="txtRouteAbbrev" Display="None"
                        CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblRoute" runat="server" Text="Route:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRoute" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="400px"></asp:TextBox><asp:RequiredFieldValidator ID="reqRoute" runat="server"
                        ErrorMessage="Enter Route " ControlToValidate="txtRoute" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; vertical-align: top; text-align: left;">
                <asp:Label ID="lblRouteDefinition" runat="server" Text="Route Definition:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandRouteDefinition" runat="server" CssClass="Textbox_Entry"
                    MaxLength="500" Width="600px" TextMode="MultiLine" Height="50px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblMasterTemplatePath" runat="server" Text="Master Template Path:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMasterTemplatePath" runat="server" CssClass="Textbox_Entry" MaxLength="256"
                    Width="600px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblOwningPillar" runat="server" Text="Owning Pillar:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlOwningPillar" runat="server" Width="335px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtOwningPillar" runat="server" CssClass="Textbox_Display" Width="259px"
                    ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqPillar" runat="server" ErrorMessage="Select Owning Pillar"
                    ControlToValidate="ddlOwningPillar" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
            </td>
            <td>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="RouteStepsDetail.aspx"
                    Text="Printer Friendly Version" CssClass="Link_Default"></asp:HyperLink>
            </td>
            <td>
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
                <td style="width: 110px">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnRouteSteps" runat="server" CssClass="Button_Default" Text="Route Steps"
                        Visible="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnRouteStepsView" runat="server" CssClass="Button_Default" Text="Route Steps"
                        CausesValidation="False" Visible="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
