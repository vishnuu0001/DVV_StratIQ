<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserJobMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserJobMaster2"
    Title="User Job Master" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:GridView ID="gvUsers" runat="server" AutoGenerateColumns="False" SkinID="GridView"
        Width="100%">
        <Columns>
            <asp:TemplateField HeaderText="Assigned">
                <ItemTemplate>
                    <asp:CheckBox ID="chkAssigned" runat="server" Checked='<%# Bind("Assigned") %>' Enabled="true" />
                </ItemTemplate>
                <HeaderStyle HorizontalAlign="Left" Width="60px" />
                <ItemStyle Width="60px" />
            </asp:TemplateField>
            <asp:BoundField DataField="LastName" HeaderText="Last Name" ReadOnly="True" SortExpression="Name" />
            <asp:BoundField DataField="FirstName" HeaderText="First Name" ReadOnly="True" />
            <asp:BoundField DataField="UserID" HeaderText="User ID" ReadOnly="True" />
            <asp:BoundField DataField="Title" HeaderText="Title" ReadOnly="True" />
            <asp:BoundField DataField="Department" HeaderText="Department" ReadOnly="True" SortExpression="Dept" />
        </Columns>
    </asp:GridView>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" Text="OK" EnableViewState="False" CssClass="Button_Default">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" Text="Cancel" CssClass="Button_Default"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
