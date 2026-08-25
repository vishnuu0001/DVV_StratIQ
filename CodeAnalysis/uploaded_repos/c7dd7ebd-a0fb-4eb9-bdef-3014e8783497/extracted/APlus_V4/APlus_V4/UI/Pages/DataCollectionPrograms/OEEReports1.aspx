<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="OEEReports1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.OEEReports1"
    Title="OEE Reports" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:DataGrid ID="dgOEEReports" GridLines="None" CellSpacing="1" PageSize="10000"
        AutoGenerateColumns="False" AllowSorting="True" BorderColor="White" BorderWidth="2px"
        CellPadding="3" Width="100%" BorderStyle="Ridge" BackColor="White" runat="server"
        SkinID="DataGrid">
        <Columns>
            <asp:BoundColumn ItemStyle-Width="10%" DataField="Workcenter" HeaderText="Work Center">
                <ItemStyle Width="10%"></ItemStyle>
            </asp:BoundColumn>
            <asp:BoundColumn DataField="Report" HeaderText="Report" Visible="False"></asp:BoundColumn>
            <asp:BoundColumn DataField="URL" HeaderText="URL" Visible="False"></asp:BoundColumn>
            <asp:TemplateColumn HeaderText="Report">
                <ItemTemplate>
                    <asp:LinkButton ID="lbtnReport" runat="server">
								<%# DataBinder.Eval(Container.DataItem,"Report")%>
                    </asp:LinkButton>
                </ItemTemplate>
            </asp:TemplateColumn>
            <asp:TemplateColumn>
                <ItemTemplate>
                    <asp:LinkButton ID="lbtnEdit" runat="server" CausesValidation="False" CommandName="EditRow"
                        Text="Edit">
                    </asp:LinkButton>
                </ItemTemplate>
            </asp:TemplateColumn>
            <asp:TemplateColumn>
                <ItemTemplate>
                    <asp:LinkButton ID="lbtnDelete" runat="server" CommandName="DeleteRow" Text="Delete">
                    </asp:LinkButton>
                </ItemTemplate>
            </asp:TemplateColumn>
        </Columns>
    </asp:DataGrid>
    <br />
    <table id="Table1" class="Table_Default">
        <tr>
            <td style="width: 110px;">
                <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnNew" runat="server" CssClass="Button_Variable" 
                    Text="New OEE Report" CommandName="AddRow">
                </asp:Button>
            </td>
        </tr>
    </table>
</asp:Content>
