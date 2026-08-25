<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="DataQuery2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.DataQuery2"
    Title="Data Query" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Table Width="100%" runat="server" ID="tblQuery" CellSpacing="2" CellPadding="2">
        <asp:TableRow>
            <asp:TableCell>
                <asp:Label ID="label4" runat="server" Text="Query:" CssClass="Label_Left_8PT"></asp:Label>
            </asp:TableCell>
            <asp:TableCell>
                <asp:Label ID="lblQueryID" runat="server" Visible="False"></asp:Label>
                <asp:Label ID="lblQuery" runat="server" CssClass="Textbox_Display" Width="425"></asp:Label>
            </asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    <table id="tbButtons" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnRunQuery" runat="server" CssClass="Button_Default" EnableViewState="False"
                    Text="Run Query"></asp:Button>
            </td>
            <td style="width: 110px">
                <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                </asp:Button>
            </td>
            <td>
                <asp:Button ID="btnExport" runat="server" CssClass="Button_Default" Text="Export"
                    EnableViewState="False" Visible="False"></asp:Button>
            </td>
        </tr>
    </table>
    <asp:DataGrid ID="grdQueryResults" runat="server" SkinID="DataGrid" AutoGenerateColumns="true">
    </asp:DataGrid>
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
