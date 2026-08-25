<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="Attachments.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Attachments"
    Title="Attachments" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Table ID="tblAttachments" runat="server" Width="100%" BorderWidth="3" BorderStyle="Ridge"
        BorderColor="White" BackColor="#DEDFDE" CellPadding="3" CellSpacing="0" GridLines="Horizontal">
    </asp:Table>
    <asp:Panel ID="pnlExit" runat="server">
        <table id="Table3" cellspacing="2" cellpadding="2" width="321" border="0">
            <tr>
                <td align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button></td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
