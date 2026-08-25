<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="TeamRouteSteps3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamRouteSteps3"
    Title="Team Route Steps" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Table ID="Table1" Width="100%" runat="server">
        <asp:TableRow>
            <asp:TableCell>
                <asp:Table runat="server" ID="Table2">
                    <asp:TableRow>
                        <asp:TableCell>
                            <asp:Image runat="server" ID="Image2" ImageUrl="~/Images/company_logo.png"></asp:Image>
                        </asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell>
                            <asp:Label runat="server" ID="lblRoute" Text="Route Goes Here"></asp:Label>
                        </asp:TableCell>
                    </asp:TableRow>
                </asp:Table>
            </asp:TableCell>
            <asp:TableCell>
                <asp:Table runat="server" ID="Table3">
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Center">
                            <asp:Label Font-Bold="True" Font-Size="Large" runat="server" ID="lblMasterPlan" Text="Master Plan"></asp:Label>
                        </asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Center">
                            <asp:Label Font-Bold="True" runat="server" ID="lblTeamName" Text="Team Name goes Here"></asp:Label>
                        </asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Center">
                            <asp:Label runat="server" Font-Bold="True" ID="lblTeam" Text="Team goes Here"></asp:Label>
                        </asp:TableCell>
                    </asp:TableRow>
                </asp:Table>
            </asp:TableCell>
            <asp:TableCell HorizontalAlign="Right">
                <asp:Table runat="server" BorderStyle="Solid" BorderWidth="1px" BorderColor="Black"
                    ID="Table4">
                    <asp:TableRow>
                        <asp:TableCell>
                            <asp:Label ID="lblPlanned" runat="server" Text="Planned"></asp:Label>
                        </asp:TableCell>
                        <asp:TableCell Width="50px" HorizontalAlign="Left" ID="PlannedCell"></asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell>
                            <asp:Label ID="lblActual" runat="server" Text="Actual"></asp:Label>
                        </asp:TableCell>
                        <asp:TableCell Width="50px" HorizontalAlign="Left" ID="ActualCell"></asp:TableCell>
                    </asp:TableRow>
                </asp:Table>
            </asp:TableCell>
            <asp:TableCell HorizontalAlign="Right">
                <asp:Image runat="server" ID="Image1" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    <br />
    <table id="Table5" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td style="vertical-align: top; text-align: left; width: 175px;">
                <asp:GridView ID="gvTeamMeetingAttendance" runat="server" AutoGenerateColumns="False"
                    SkinID="TeamGridView">
                    <RowStyle Wrap="False" />
                    <EmptyDataRowStyle Wrap="False" />
                    <Columns>
                        <asp:BoundField DataField="RouteStep" ReadOnly="True">
                            <HeaderStyle BorderStyle="None" />
                            <ItemStyle HorizontalAlign="Center" VerticalAlign="Middle" Wrap="False" Width="10px"
                                Height="33px" CssClass="TeamWhiteCell1" />
                        </asp:BoundField>
                        <asp:TemplateField HeaderText="Route Steps" ShowHeader="False">
                            <ItemTemplate>
                                <asp:Label ID="lblRouteSteps" runat="server" CausesValidation="False" Text='<%# Left(Eval("Step").ToString,50) %>'></asp:Label>
                            </ItemTemplate>
                            <HeaderStyle HorizontalAlign="Left" VerticalAlign="Middle" Wrap="False" />
                            <ItemStyle HorizontalAlign="Left" VerticalAlign="Middle" Wrap="True" Height="33px"
                                CssClass="TeamWhiteCell1" Width="150px" />
                        </asp:TemplateField>
                    </Columns>
                    <SelectedRowStyle Wrap="False" />
                    <HeaderStyle CssClass="Grid_Team_MasterPlan_HeaderStyle" Height="32px" />
                    <AlternatingRowStyle Wrap="False" />
                </asp:GridView>
            </td>
            <td align="left" valign="top">
                <asp:GridView ID="gvTeamMeetingAttendance2" runat="server" AutoGenerateColumns="False"
                    SkinID="TeamGridView" Width="100%">
                    <Columns>
                    </Columns>
                    <HeaderStyle CssClass="Grid_Team_MasterPlan_HeaderStyle1" />
                </asp:GridView>
            </td>
        </tr>
    </table>
    <br />
    <br />
    <asp:Label ID="lblPrintDate" runat="server"></asp:Label>
    <br />
</asp:Content>
