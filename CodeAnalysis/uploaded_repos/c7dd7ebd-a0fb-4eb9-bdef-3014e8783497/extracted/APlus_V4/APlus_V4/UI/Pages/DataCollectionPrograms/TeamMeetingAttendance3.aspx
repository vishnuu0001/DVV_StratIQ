<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="TeamMeetingAttendance3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamMeetingAttendance3"
    Title="Team Meeting Attendance" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <br />
    <table style="width: 100%;">
        <tr>
            <td rowspan="3" align="left" valign="top" style="width: 20%">
                <asp:Image runat="server" ID="Image2" ImageUrl="~/Images/company_logo.png"></asp:Image>
            </td>
            <td align="center">
                <asp:Label Font-Bold="True" Font-Size="Large" runat="server" ID="lblAttendance1"
                    Text="Attendance"></asp:Label>
            </td>
            <td rowspan="3" valign="top" style="width: 150px" align="center">
                <table style="border: 1px solid #000000;">
                    <tr>
                        <td style="width: 53px" align="right">
                            <asp:Label ID="lblAttended1" runat="server" Text="Attended"></asp:Label>
                        </td>
                        <td align="center" style="background-color: #00FF00; width: 55px" valign="middle">
                            <asp:Label ID="lblAttended" runat="server" BackColor="Lime" Text="X"></asp:Label>
                        </td>
                    </tr>
                    <tr>
                        <td style="width: 53px" align="right">
                            <asp:Label ID="lblAbsent1" runat="server" Text="Absent"></asp:Label>
                        </td>
                        <td align="center" style="background-color: #FF0000; width: 55px">
                            <asp:Label ID="lblAbsent" runat="server" Text="O"></asp:Label>
                        </td>
                    </tr>
                </table>
            </td>
            <td rowspan="3" align="right" style="width: 15%" valign="top">
                <asp:Image runat="server" ID="Image4" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </td>
        </tr>
        <tr>
            <td align="center">
                <asp:Label Font-Bold="True" runat="server" ID="lblTeamName" Text="Team Name goes Here"></asp:Label>
            </td>
        </tr>
        <tr>
            <td align="center">
                <asp:Label runat="server" Font-Bold="True" ID="lblTeam" Text="Team goes Here"></asp:Label>
            </td>
        </tr>
    </table>
    <table id="Table5" style="width: 905px" cellspacing="0" cellpadding="0" align="center"
        border="0">
        <tr>
            <td style="width: 278px;" align="left" colspan="2">
                <div>
                    &nbsp;</div>
            </td>
        </tr>
        <tr>
            <td align="center" colspan="2">
                <asp:Image ID="imgTeamPhoto" runat="server" Height="250"></asp:Image>
            </td>
        </tr>
        <tr>
            <td colspan="2" height="10">
            </td>
        </tr>
    </table>
    <table align="center" cellpadding="0" cellspacing="0">
        <tr align="center">
            <td style="width: auto" valign="top" align="right">
                <asp:GridView ID="gvTeamMeetingAttendance" runat="server" AutoGenerateColumns="False"
                    SkinID="TeamDefaultGridView" Width="100%">
                    <Columns>
                        <asp:BoundField DataField="UserName" HeaderText="User Name" ReadOnly="True" ItemStyle-Wrap="false" />
                        <asp:BoundField DataField="Title" HeaderText="Title" ReadOnly="True" ItemStyle-Wrap="false" />
                        <asp:BoundField DataField="Role" HeaderText="Role" ReadOnly="True" ItemStyle-Wrap="false" />
                    </Columns>
                </asp:GridView>
            </td>
            <td valign="top" align="left">
                <asp:Panel ID="Panel2" runat="server" HorizontalAlign="Left">
                    <asp:GridView ID="gvTeamMeetingAttendance2" runat="server" AutoGenerateColumns="False"
                        SkinID="TeamGridView">
                        <RowStyle BorderColor="Black" BorderStyle="Solid" BorderWidth="1px" />
                    </asp:GridView>
                    <br />
                </asp:Panel>
            </td>
        </tr>
    </table>
    <asp:Panel ID="Panel1" runat="server" HorizontalAlign="Center">
        <asp:Label ID="lblAttendance" runat="server" Visible="False"></asp:Label>
        <br />
        <asp:Label ID="lblPrintDate" runat="server"></asp:Label>
    </asp:Panel>
    <br />
</asp:Content>
