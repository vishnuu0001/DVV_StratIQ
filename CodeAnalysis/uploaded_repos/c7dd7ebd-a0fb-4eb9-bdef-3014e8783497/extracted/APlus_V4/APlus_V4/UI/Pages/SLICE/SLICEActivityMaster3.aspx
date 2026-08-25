<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="SLICEActivityMaster3.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityMaster3"
    Title="SLICE Activity Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Table ID="Table1" BorderWidth="0" runat="server" Width="100%" BorderColor="black">
        <asp:TableRow>
            <asp:TableCell VerticalAlign="Top" Width="150" BorderWidth="0" BorderColor="black">
                <asp:Image runat="server" ID="Image2" ImageUrl="~/Images/company_logo.png">
                </asp:Image>
            </asp:TableCell>
            <asp:TableCell>
                <asp:Table runat="server" ID="Table3" Width="100%" BorderWidth="0" BorderColor="black">
                    <asp:TableRow Width="100%" HorizontalAlign="center">
                        <asp:TableCell HorizontalAlign="Center">
                            <asp:Label Font-Bold="True" Font-Size="medium" runat="server" ID="lblSLICEActivityMasterTitle">S</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="x-small" runat="server" ID="Label13">afety-</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="medium" runat="server" ID="Label14">L</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="x-small" runat="server" ID="Label15">ubrication-</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="medium" runat="server" ID="Label16">I</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="x-small" runat="server" ID="Label17">nspection-</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="medium" runat="server" ID="Label18">C</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="x-small" runat="server" ID="Label19">leaning-</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="medium" runat="server" ID="Label20">E</asp:Label>
                            <asp:Label Font-Bold="True" Font-Size="x-small" runat="server" ID="Label21">nvironmental</asp:Label>
                        </asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="Center">
                            <asp:Label Font-Bold="True" runat="server" ID="lblActivityGroup">Activity Group Info Here</asp:Label>
                            <br />
                            <asp:Label ID="lblPrintDate" runat="server">Date Here</asp:Label>
                            <br />
                            <br />
                        </asp:TableCell>
                    </asp:TableRow>
                    <asp:TableRow>
                        <asp:TableCell HorizontalAlign="center">
                            <asp:Label runat="server" Font-Bold="True" ID="lblTargetTime">Target Time: </asp:Label>
                            <asp:Label runat="server" Font-Bold="True" ID="lblShowTargetTime">###</asp:Label>
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            <asp:Label Font-Bold="True" runat="server" ID="lblElapsedTime">Elapsed Time: </asp:Label>
                            <asp:Label Font-Bold="True" runat="server" ID="lblShowElapsedTime">_____</asp:Label>
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            <asp:Label Font-Bold="True" runat="server" ID="lblStartTime">Start Time: </asp:Label>
                            <asp:Label Font-Bold="True" runat="server" ID="lblShowStartTime">_____</asp:Label>
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            <asp:Label Font-Bold="True" runat="server" ID="lblEndTime">End Time: </asp:Label>
                            <asp:Label Font-Bold="True" runat="server" ID="lblShowEndTime">_____</asp:Label>
                        </asp:TableCell>
                    </asp:TableRow>
                </asp:Table>
            </asp:TableCell>
            <asp:TableCell HorizontalAlign="Right" VerticalAlign="top" Width="69" BorderColor="red"
                BorderWidth="0">
                <asp:Image runat="server" ID="Image1" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </asp:TableCell>
        </asp:TableRow>
    </asp:Table>
    <asp:Table ID="tblSLICEActivityData" runat="server" BorderWidth="0px" Width="100%"
        BorderStyle="None" CellPadding="1" CellSpacing="0" EnableViewState="False">
    </asp:Table>
    <br />
    <br />
    <asp:Panel ID="pnlPrintInfo" runat="server" HorizontalAlign="Left">
    </asp:Panel>
</asp:Content>
