<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIReportCategoryKPIMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIReportCategoryKPIMaster2"
    Title="KPI Group Item Maintenance" ValidateRequest="false" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
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
                <asp:Label ID="lblKPIReportCategoryID" runat="server" Text="KPI Group:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlKPIReportCategory" runat="server" Width="258px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtKPIReportCategory" runat="server" Width="249px" MaxLength="15"
                    CssClass="Textbox_Display" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqKPIReportCategory" runat="server" ErrorMessage="Select KPI Group"
                    ControlToValidate="ddlKPIReportCategory" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblKPI" runat="server" Text="KPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlKPI" runat="server" Width="325px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtKPI" runat="server" Width="310px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqKPI" runat="server" ErrorMessage="Select KPI"
                    ControlToValidate="ddlKPI" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                &nbsp;<asp:CheckBox ID="ckShowAllKPI" runat="server" AutoPostBack="True" 
                    Text="Show All KPIs" />
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblLegend" runat="server">Legend:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLegend" runat="server" CssClass="Textbox_Entry" MaxLength="30"
                    Width="174px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqLegend" runat="server" ErrorMessage="Enter Legend"
                    ControlToValidate="txtLegend" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblSequence" runat="server">Sequence:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSequence" runat="server" CssClass="Textbox_Entry" Width="43px"
                    MaxLength="2"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSequence" runat="server" ErrorMessage="Enter Sequence"
                    ControlToValidate="txtSequence" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <br />
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
