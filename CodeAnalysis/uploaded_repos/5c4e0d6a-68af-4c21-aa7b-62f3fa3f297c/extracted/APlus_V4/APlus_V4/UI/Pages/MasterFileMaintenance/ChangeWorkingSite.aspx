<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="ChangeWorkingSite.aspx.vb" Inherits="WebApp.APlus.UI.Pages.ChangeWorkingSite"
    Title="Change Working Site" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Namespace="WebApp.APlus.UI.CustomControls" TagPrefix="CC1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table cellspacing="2" cellpadding="2" border="0" class="Table_Default" id="Table1">
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblNewWorkingSite" runat="server" EnableViewState="False" Visible="True"
                    CssClass="Label_Left_8PT" Text="New Working Site:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlWorkingSite" runat="server" CssClass="DropdownList_Entry"
                    Width="232px" Visible="True">
                </asp:DropDownList>
            </td>
        </tr>
    </table>
    <br />
    <table id="Table4" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnOK" runat="server" Text="OK" CssClass="Button_Default" EnableViewState="False"
                    Visible="True" CausesValidation="True"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnCancel" runat="server" Text="Cancel" CssClass="Button_Default"
                    EnableViewState="False" Visible="True" CausesValidation="False"></asp:Button>
            </td>
        </tr>
    </table>
    <asp:ValidationSummary ID="Validationsummary1" runat="server" CssClass="Label_Left_8PT"
        DisplayMode="List" ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
