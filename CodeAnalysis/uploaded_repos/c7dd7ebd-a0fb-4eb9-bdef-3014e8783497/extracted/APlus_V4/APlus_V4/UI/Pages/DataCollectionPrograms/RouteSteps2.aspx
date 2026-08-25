<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RouteSteps2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RouteSteps2"
    Title="Route Steps Maintenance" %>

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
    <div>
        <table class="Table_Default" id="Table1">
            <tr>
                <td style="width: 115px" valign="top">
                    <asp:Label ID="lblRouteAbbrev" runat="server" Text="Route:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtRouteAbbrev" runat="server" Width="208px" CssClass="Textbox_Display"
                        ReadOnly="True"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 115px" valign="top">
                    <asp:Label ID="lblRoute" runat="server" Text="Step Number:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtStepNumber" runat="server" Width="43px" MaxLength="4" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqStepNumber" runat="server" Display="None" ControlToValidate="txtStepNumber"
                        CssClass="Label_Left_8PT" ErrorMessage="Enter Step Number"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 115px" valign="top">
                    <asp:Label ID="lblRouteDefinition" runat="server" Text="Step:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td style="height: 15px">
                    <asp:TextBox ID="txtStep" runat="server" Width="525px" MaxLength="100" CssClass="Textbox_Entry"
                        Height="18px"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqStep" runat="server" ErrorMessage="Enter Step"
                        CssClass="Label_Left_8PT" ControlToValidate="txtStep" Display="None"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 115px; vertical-align: top; text-align: left;" valign="top">
                    <asp:Label ID="lblMasterTemplatePath" runat="server" Text="Step Definition:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandStepDefinition" runat="server" Width="600px" MaxLength="500"
                        CssClass="Textbox_Entry" Height="50px" TextMode="MultiLine"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 115px">
                    <asp:Label ID="Label1" runat="server" Text="Start Date Offset:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtStartDateOffset" runat="server" Width="43px" CssClass="Textbox_Entry"
                        MaxLength="4"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqStartOffset" runat="server" ErrorMessage="Enter Start Date Offset"
                        ControlToValidate="txtStartDateOffset" Display="None"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 115px">
                    <asp:Label ID="Label2" runat="server" Text="Planned Duration:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtPlannedDuration" runat="server" Width="43px" CssClass="Textbox_Entry"
                        MaxLength="4"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqPlannedDuration" runat="server" ErrorMessage="Enter Planned Duration"
                        ControlToValidate="txtPlannedDuration" Display="None"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 115px">
                </td>
                <td>
                </td>
            </tr>
            <tr>
                <td style="width: 115px">
                    <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="RouteStepsDetail.aspx"
                        Text="Printer Friendly Version" CssClass="Link_Default"></asp:HyperLink>
                </td>
                <td>
                </td>
            </tr>
        </table>
    </div>
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
                    <asp:Button ID="btnKeyActions" runat="server" CssClass="Button_Default" Text="Key Actions"
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
                    <asp:Button ID="btnKeyActionsView" runat="server" CssClass="Button_Default" Text="Key Actions"
                        CausesValidation="False" Visible="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
