<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="ApplicationCacheMaster.aspx.vb" Inherits="WebApp.APlus.UI.Pages.ApplicationCacheMaster"
    Title="Application Cache Master" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td valign="top" style="width: 185px">
                <asp:Label ID="Label3" runat="server" Text="Culture Translation Cache Hash table:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:Label ID="lblHashRows" runat="server" Text="Hash table Rows Goes Here" CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <asp:GridView ID="gvCach" runat="server" SkinID="GridView" AllowSorting="True" AutoGenerateColumns="False"
                    Width="185px">
                    <Columns>
                        <asp:BoundField DataField="Language" HeaderText="Culture">
                            <HeaderStyle ForeColor="White" />
                        </asp:BoundField>
                        <asp:BoundField DataField="NumberOfItems" HeaderText="Items">
                            <HeaderStyle ForeColor="White" />
                        </asp:BoundField>
                    </Columns>
                </asp:GridView>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default" style="width: 520px;">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" Text="Exit" CssClass="Button_Default"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnClearCultureCache" runat="server" Text="Clear Culture Translation Cache"
                        CssClass="Button_Variable" CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
