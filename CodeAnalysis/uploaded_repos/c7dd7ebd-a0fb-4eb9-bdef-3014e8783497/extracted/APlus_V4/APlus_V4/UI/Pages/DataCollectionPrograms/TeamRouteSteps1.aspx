<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamRouteSteps1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamRouteSteps1"
    Title="Team Route Steps" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <br />
    <table id="tblRoutInfo" class="Table_Default" runat="server">
        <tr>
            <td>
                <asp:Label ID="lblRoute" runat="server" Text="Route Info" CssClass="Label_Left_10PT"></asp:Label>
            </td>
            <td style="text-align: right">
                <asp:Label ID="lblPlanned" runat="server" Text="Planned" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 50px; background-color: #FFE4E1;">
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblNoInfo" runat="server" Text="No Info" CssClass="Label_ErrorControl"></asp:Label>
            </td>
            <td style="text-align: right">
                <asp:Label ID="lblActual" runat="server" Text="Actual" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 50px; background-color: #B0C4DE;">
            </td>
        </tr>
    </table>
    <table id="Table2" cellpadding="0" cellspacing="0">
        <tr>
            <td align="left" valign="top" style="width: auto">
                <asp:GridView ID="gvRouteSteps" runat="server" AutoGenerateColumns="False" SkinID="TeamGridView"
                    Width="100%">
                    <RowStyle Wrap="False" />
                    <EmptyDataRowStyle Wrap="False" />
                    <Columns>
                        <asp:BoundField DataField="RouteStep" ReadOnly="True">
                            <HeaderStyle BorderStyle="None" />
                            <ItemStyle HorizontalAlign="Center" VerticalAlign="Middle" Wrap="False" Width="15px"
                                Height="33px" CssClass="TeamWhiteCell1" />
                        </asp:BoundField>
                        <asp:TemplateField HeaderText="Route Steps" ShowHeader="False">
                            <ItemTemplate>
                                <asp:LinkButton ID="lbRouteSteps" runat="server" CausesValidation="False" Text='<%# Left(Eval("Step").ToString,50) %>'
                                    CommandArgument='<%# Eval("RouteStep") %>' CommandName="EditRow"></asp:LinkButton>
                            </ItemTemplate>
                            <HeaderStyle HorizontalAlign="Left" VerticalAlign="Middle" Wrap="False" />
                            <ItemStyle HorizontalAlign="Left" VerticalAlign="Middle" Wrap="False" Height="33px"
                                CssClass="TeamWhiteCell1" />
                        </asp:TemplateField>
                    </Columns>
                    <SelectedRowStyle Wrap="False" />
                    <HeaderStyle CssClass="Grid_Team_MasterPlan_HeaderStyle" Height="32px" />
                    <AlternatingRowStyle Wrap="False" />
                </asp:GridView>
            </td>
            <td align="left" valign="top">
                <asp:Panel ID="Panel1" runat="server" Width="750px" ScrollBars="Horizontal">
                    <asp:GridView ID="gvRouteSteps2" runat="server" AutoGenerateColumns="False" SkinID="TeamGridView"
                        Width="100%">
                        <HeaderStyle CssClass="Grid_Team_MasterPlan_HeaderStyle" />
                    </asp:GridView>
                </asp:Panel>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td>
                    <asp:HyperLink ID="lnkPrintPage" runat="server" NavigateUrl="~/UI/Pages/DataCollectionPrograms/TeamRouteSteps3.aspx"
                        Target="_blank" Text="Printer Friendly Version"></asp:HyperLink>
                </td>
            </tr>
            <tr>
                <td>
                </td>
            </tr>
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" Text="Exit" CssClass="Button_Default" EnableViewState="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
