<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="RouteStepsDetail.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RouteStepsDetail"
    Title="Route Step Detail" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Table ID="Table1" Width="100%" runat="server">
        <asp:TableRow>
            <asp:TableCell>
                <asp:Table runat="server" ID="Table2">
                    <asp:TableRow>
                        <asp:TableCell>
                            <asp:Image runat="server" ID="Image2" ImageUrl="../../../Images/company_logo.png">
                            </asp:Image>
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
                            <asp:Label Font-Bold="True" Font-Size="Large" runat="server" ID="Label1" Text="Route"></asp:Label>
                        </asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Center">
                            <asp:Label Font-Bold="True" runat="server" ID="lblRoute" Text="Route Name goes Here"></asp:Label>
                        </asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Center"></asp:TableCell>
                    </asp:TableRow>
                </asp:Table>
            </asp:TableCell>
            <asp:TableCell HorizontalAlign="Right">
                <asp:Label Font-Size="8" runat="server" ID="lblTeam" Text="Team Name goes Here"></asp:Label>
            </asp:TableCell>
            <asp:TableCell HorizontalAlign="Right">
                <asp:Image runat="server" ID="Image1" ImageUrl="../../../Images/APlus.jpg"></asp:Image>
            </asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    <br>
    <asp:Table ID="tblRouteSteps" runat="server" Width="100%" EnableViewState="False"
        CellSpacing="0" BorderWidth="0px" CellPadding="0" BorderStyle="None">
    </asp:Table>
    <br>
    <br>
    <asp:Panel ID="Panel1" runat="server" HorizontalAlign="Left">
        <asp:Label ID="lblPrintDate" runat="server"></asp:Label>
    </asp:Panel>
</asp:Content>
