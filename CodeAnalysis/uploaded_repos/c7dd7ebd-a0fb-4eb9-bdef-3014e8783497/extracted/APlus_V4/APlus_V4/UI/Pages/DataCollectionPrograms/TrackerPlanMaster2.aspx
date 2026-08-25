<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerPlanMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerPlanMaster2"
    Title="Master Plan Maintenance" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 150px;
        }
    </style>
</asp:Content>
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
                <asp:Label ID="lblSavingsTracker" runat="server" Text="Tracker Plan ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTrackerPlanID" runat="server" Width="75px" MaxLength="15" CssClass="Textbox_Display"
                    Height="16px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="True" Height="16px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblPillar" runat="server" Text="Pillar:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlPillar" runat="server" Width="175px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtPillar" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblBusinessArea" runat="server" Text="Business Area:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessArea" runat="server" Width="175px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtBusinessArea" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px" ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqBusinessArea" runat="server" ErrorMessage="Select Business Area"
                    ControlToValidate="ddlBusinessArea" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblBusinessUnit" runat="server" Text="Business Unit:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessUnit" runat="server" Width="175px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtBusinessUnit" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblSavingsCategory" runat="server" Text="Savings Category:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSavingsCategory" runat="server" Width="175px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSavingsCategory" runat="server" Width="175px" MaxLength="15"
                    CssClass="Textbox_Display" Visible="False" Height="16px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActive" runat="server" Text="Active:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="cbActive" runat="server"></asp:CheckBox>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons">
            <tr>
                <td class="style1">
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
        <table id="Table3">
            <tr>
                <td style="width: 150px">
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
