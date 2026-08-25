<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="TeamActionPlan3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamActionPlan3"
    Title="Team Action Plan Maintenance" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Table ID="Table1" runat="server" Width="100%">
        <asp:TableRow>
            <asp:TableCell>
                <asp:Table runat="server" ID="Table2">
                    <asp:TableRow>
                        <asp:TableCell>
                            <asp:Image runat="server" ID="Image2" ImageUrl="~/Images/company_logo.png"></asp:Image>
                        </asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell></asp:TableCell>
                    </asp:TableRow>
                </asp:Table>
            </asp:TableCell>
            <asp:TableCell>
                <asp:Table runat="server" ID="Table3">
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Center">
                            <asp:Label Font-Bold="True" Font-Size="Large" runat="server" ID="lblTeamActionPlan"
                                Text="Team Action Plan"></asp:Label>
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
                        <asp:TableCell HorizontalAlign="Right">
                            <asp:Label ID="lblClosed" runat="server" Text="Completed"></asp:Label></asp:TableCell>
                        <asp:TableCell Width="65px" HorizontalAlign="Left" ID="CompletedCell"></asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Right">
                            <asp:Label ID="lblInProgress" runat="server" Text="InProgress"></asp:Label></asp:TableCell>
                        <asp:TableCell Width="65px" HorizontalAlign="Left" ID="InprogressCell"></asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Right">
                            <asp:Label ID="lblLate" runat="server" Text="Late"></asp:Label></asp:TableCell>
                        <asp:TableCell Width="65px" HorizontalAlign="Left" ID="LateCell"></asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Right">
                            <asp:Label ID="lblClosedLate" runat="server" Text="Completed Late"></asp:Label></asp:TableCell>
                        <asp:TableCell Width="65px" HorizontalAlign="Left" ID="LateCompletedCell"></asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Right">
                            <asp:Label ID="lblCancelled" runat="server" Text="Cancelled"></asp:Label></asp:TableCell>
                        <asp:TableCell Width="65px" HorizontalAlign="Left" ID="CancelledCell"></asp:TableCell>
                    </asp:TableRow>
                </asp:Table>
            </asp:TableCell>
            <asp:TableCell HorizontalAlign="Right">
                <asp:Image runat="server" ID="Image4" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    <table class="Table_TeamActionPlan" id="Table5" style="width: 100%" cellspacing="0"
        cellpadding="0" align="center" border="0">
        <tr>
            <td style="width: 278px; height: 1px" align="left" colspan="2">
                <div ms_positioning="FlowLayout">
                    &nbsp;</div>
            </td>
        </tr>
        <tr align="center">
            <td style="width: 100%" valign="top" align="center">
                <asp:GridView ID="gvTeamActionPlan" runat="server" AutoGenerateColumns="False" SkinID="GridView"
                    DataKeyNames="Cancelled">
                    <Columns>
                        <asp:BoundField DataField="ActionNumber" HeaderText="No." ReadOnly="True" />
                        <asp:BoundField DataField="StepNo" HeaderText="Step" ReadOnly="True" />
                        <asp:BoundField DataField="UserName" HeaderText="Who" ReadOnly="True" />
                        <asp:BoundField DataField="AssignedToOther" HeaderText="Others" ReadOnly="True" />
                        <asp:BoundField DataField="ActionItem" HeaderText="Action Item" ReadOnly="True" />
                        <asp:BoundField DataField="TargetDate" HeaderText="By When" ReadOnly="True" DataFormatString="{0:yyyy/MM/dd}">
                            <HeaderStyle HorizontalAlign="Center" />
                            <ItemStyle Width="100px" HorizontalAlign="Center" />
                        </asp:BoundField>
                        <asp:BoundField DataField="ClosedDate" HeaderText="Closed Date" ReadOnly="True" DataFormatString="{0:yyyy/MM/dd}">
                            <HeaderStyle HorizontalAlign="Center" />
                            <ItemStyle Width="100px" HorizontalAlign="Center" />
                        </asp:BoundField>
                        <asp:BoundField DataField="Cancelled" HeaderText="Cancelled" Visible="false" />
                    </Columns>
                </asp:GridView>
            </td>
        </tr>
    </table>
    <asp:Panel ID="Panel1" runat="server" HorizontalAlign="Center">
        <asp:Label ID="lblPrintDate" runat="server"></asp:Label>
    </asp:Panel>
</asp:Content>
