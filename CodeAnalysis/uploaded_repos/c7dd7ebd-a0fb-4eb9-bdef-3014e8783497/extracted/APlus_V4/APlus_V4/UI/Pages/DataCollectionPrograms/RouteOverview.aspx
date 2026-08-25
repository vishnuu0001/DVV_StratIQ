<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RouteOverview.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RouteOverview"
    Title="Route Overview" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Table runat="server" Width="100%" CellPadding="0" CellSpacing="0" ID="tblHeaders">
        <asp:TableRow>
            <asp:TableCell Width="100%" ColumnSpan="3" BackColor="LightGrey">Step</asp:TableCell>
        </asp:TableRow>
        <asp:TableRow>
            <asp:TableCell Width="10%"></asp:TableCell>
            <asp:TableCell ColumnSpan="2" BackColor="LightGrey">Key Action</asp:TableCell>
        </asp:TableRow>
        <asp:TableRow>
            <asp:TableCell Width="10%"></asp:TableCell>
            <asp:TableCell Width="10%"></asp:TableCell>
            <asp:TableCell BackColor="LightGrey">Tool</asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    <br />
    <asp:Table ID="tblRoute" Width="100%" runat="server" BorderStyle="Ridge" BorderColor="#4A3C8C"
        BorderWidth="1px">
        <asp:TableRow>
            <asp:TableCell>
                <asp:Label ID="lblRoute" runat="server" Font-Bold="True">Route Name goes Here</asp:Label>
            </asp:TableCell>
            <asp:TableCell HorizontalAlign="Right">
                <asp:LinkButton ID="lnkEditRoute" runat="server" CommandName="Route|EditRow">Edit Route</asp:LinkButton>
                |
                <asp:LinkButton ID="lnkAddStep" runat="server" CommandName="Step|AddRow">Add Route Step</asp:LinkButton>
            </asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    <br />
    <asp:Repeater ID="rpSteps" runat="server">
        <ItemTemplate>
            <asp:Table runat="server" ID="tblSteps" Width="100%" CellSpacing="0" CellPadding="1"
                BorderStyle="Ridge" BorderColor="#4A3C8C" BorderWidth="1px">
                <asp:TableRow>
                    <asp:TableCell Font-Bold="True" ForeColor="#4A3C8C" HorizontalAlign="Left">
                        <asp:Label runat="server" ID="lblStep"></asp:Label>
                    </asp:TableCell>
                    <asp:TableCell HorizontalAlign="Right">
                        <asp:LinkButton runat="server" ID="lnkEditStep">Edit</asp:LinkButton>
                        |
                        <asp:LinkButton runat="server" ID="lnkDeleteStep">Delete</asp:LinkButton>
                        |
                        <asp:LinkButton runat="server" ID="lnkAddKeyAction">Add Key Action</asp:LinkButton>
                    </asp:TableCell>
                </asp:TableRow>
                <asp:TableRow>
                    <asp:TableCell HorizontalAlign="Right" ColumnSpan="2">
                        <asp:Repeater ID="rpKeyActions" runat="server">
                            <ItemTemplate>
                                <asp:Table runat="server" ID="tblKeyActions" Width="90%" CellPadding="0" CellSpacing="1">
                                    <asp:TableRow>
                                        <asp:TableCell ColumnSpan="2">
													<hr>
                                        </asp:TableCell>
                                    </asp:TableRow>
                                    <asp:TableRow>
                                        <asp:TableCell HorizontalAlign="Left">
                                            <asp:Label runat="server" ID="lblKeyAction"></asp:Label>
                                        </asp:TableCell>
                                        <asp:TableCell HorizontalAlign="Right">
                                            <asp:LinkButton runat="server" ID="lnkEditKeyAction">Edit</asp:LinkButton>
                                            |
                                            <asp:LinkButton runat="server" ID="lnkDeleteKeyAction">Delete</asp:LinkButton>
                                            |
                                            <asp:LinkButton runat="server" ID="lnkAddTool">Add Tool</asp:LinkButton>
                                        </asp:TableCell>
                                    </asp:TableRow>
                                    <asp:TableRow>
                                        <asp:TableCell ColumnSpan="2" HorizontalAlign="Right">
                                            <asp:Repeater ID="rpTools" runat="server">
                                                <ItemTemplate>
                                                    <asp:Table ID="tblTools" runat="server" Width="90%" CellPadding="0" CellSpacing="1">
                                                        <asp:TableRow Height="2px">
                                                            <asp:TableCell ColumnSpan="2">
																		<hr>
                                                            </asp:TableCell>
                                                        </asp:TableRow>
                                                        <asp:TableRow>
                                                            <asp:TableCell HorizontalAlign="Left">
                                                                <asp:HyperLink runat="server" ID="lnkTool"></asp:HyperLink>
                                                            </asp:TableCell>
                                                            <asp:TableCell HorizontalAlign="Right">
                                                                <asp:LinkButton runat="server" ID="lnkEditTool">Edit</asp:LinkButton>
                                                                |
                                                                <asp:LinkButton runat="server" ID="lnkDeleteTool">Delete</asp:LinkButton>
                                                            </asp:TableCell>
                                                        </asp:TableRow>
                                                    </asp:Table>
                                                </ItemTemplate>
                                            </asp:Repeater>
                                        </asp:TableCell>
                                    </asp:TableRow>
                                </asp:Table>
                            </ItemTemplate>
                        </asp:Repeater>
                    </asp:TableCell>
                </asp:TableRow>
            </asp:Table>
        </ItemTemplate>
    </asp:Repeater>
    <br />
    <br />
    <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="RouteStepsDetail.aspx">Printer Friendly Version</asp:HyperLink>
    <br />
    <br />
    <asp:Panel ID="pnlExit" runat="server">
        <table id="Table3" style="width: 152px; height: 26px" cellspacing="2" cellpadding="2"
            width="152" border="0">
            <tr>
                <td align="left">
                    <asp:Button ID="btnExit" runat="server" CausesValidation="False" Text="Exit" CssClass="Button_Default">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
