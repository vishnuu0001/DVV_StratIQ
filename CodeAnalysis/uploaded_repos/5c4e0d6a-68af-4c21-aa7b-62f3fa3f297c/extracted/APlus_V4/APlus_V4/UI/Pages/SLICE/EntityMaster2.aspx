<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="EntityMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.EntityMaster2"
    Title="Entity Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 107px; height: 32px">
                <asp:Label ID="Label1" runat="server" Text="Entity ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 32px">
                <asp:TextBox ID="txtEntityID" runat="server" CssClass="Textbox_Display" MaxLength="5"
                    Width="88px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 107px; height: 32px">
                <asp:Label ID="Label2" runat="server" Text="Workcenter:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 32px">
                <asp:DropDownList ID="ddlWorkcenter" runat="server" Width="200px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtWorkcenter" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="200px" ReadOnly="True"></asp:TextBox>
            </td>
            <td style="height: 32px">
            </td>
            <td style="height: 32px">
            </td>
        </tr>
        <tr>
            <td style="width: 107px">
                <asp:Label ID="Label3" runat="server" Text="SAP Entity:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSAPEntity" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="304px"></asp:TextBox><asp:RequiredFieldValidator ID="reqSAPEntity" runat="server"
                        ErrorMessage="Enter a SAP Entity." ControlToValidate="txtSAPEntity" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 107px">
                <asp:Label ID="Label4" runat="server" Text="Entity/Component:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEntity" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="632px"></asp:TextBox><asp:RequiredFieldValidator ID="reqEntity" runat="server"
                        ErrorMessage="Enter a Entity." ControlToValidate="txtEntity" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 107px">
                <asp:Label ID="Label5" runat="server" Text="Location:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLocation" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="632px"></asp:TextBox><asp:RequiredFieldValidator ID="reqLocation" runat="server"
                        ErrorMessage="Enter a Location." ControlToValidate="txtLocation" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <table id="Table2" style="width: 321px; height: 26px" cellspacing="2" cellpadding="2"
        width="321" border="0">
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
