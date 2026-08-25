<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RouteStepsKeyActionsTools2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RouteStepsKeyActionsTools2"
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
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 130px">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Route:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRouteAbbrev" runat="server" Width="259px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="lblRoute" runat="server" Text="Step Number:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtStepNumber" runat="server" Width="43px" MaxLength="4" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label3" runat="server" Text="Key Action Number:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtKeyActionNumber" runat="server" Width="43px" CssClass="Textbox_Display"
                    MaxLength="4" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="lblTool" runat="server" Text="Tool:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTool" runat="server" Width="312px" MaxLength="50" CssClass="Textbox_Entry"
                    Height="18px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTool" runat="server" ErrorMessage="Enter Tool"
                    ControlToValidate="txtTool" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label5" runat="server" Text="Template Attachment:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlTemplateFile" runat="server" Width="335px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtTemplateFile" runat="server" ReadOnly="True" CssClass="Textbox_Display"
                    Width="335px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
            </td>
            <td>
                <asp:Label ID="Label2" runat="server" Text="Or" CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label4" runat="server" Text="Training Attachment:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlTrainingFile" runat="server" Width="335px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtTrainingFile" runat="server" ReadOnly="True" CssClass="Textbox_Display"
                    Width="335px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label1" runat="server" Text="URL:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandURLLink" runat="server" Width="525px" CssClass="Textbox_Entry"
                    MaxLength="150" Height="18px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
            </td>
            <td>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="RouteStepsDetail.aspx"
                    Text="Printer Friendly Version" CssClass="Link_Default"></asp:HyperLink>
            </td>
            <td style="height: 15px">
            </td>
        </tr>
        <tr>
            <td>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
