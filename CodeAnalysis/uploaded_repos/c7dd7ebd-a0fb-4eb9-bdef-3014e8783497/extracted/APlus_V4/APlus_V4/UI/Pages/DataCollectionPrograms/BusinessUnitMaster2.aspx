<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="BusinessUnitMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.BusinessUnitMaster2"
    Title="Business Unit Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblBusinessUnitID" runat="server" Text="Business Unit ID:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtBusinessUnitID" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="31px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblBusinessUnit" runat="server" Text="Business Unit:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtBusinessUnit" runat="server" CssClass="Textbox_Entry" MaxLength="30"
                    Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqBusinessUnit" runat="server" ErrorMessage="Enter Business Unit"
                    ControlToValidate="txtBusinessUnit" Display="None" 
                    CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAbbreviation" runat="server" Text="Abbrev:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtBusinessUnitAbbrev" runat="server" CssClass="Textbox_Entry" MaxLength="3"
                    Width="50px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAbbrev" runat="server" ErrorMessage="Enter Abbreviation"
                    ControlToValidate="txtBusinessUnitAbbrev" Display="None" 
                    CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblBusinessArea" runat="server" Text="Business Area:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessArea" runat="server" CssClass="DropdownList_Entry"
                    Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtBusinessArea" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActive" runat="server" Text="Active:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckActive" runat="server" />
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
