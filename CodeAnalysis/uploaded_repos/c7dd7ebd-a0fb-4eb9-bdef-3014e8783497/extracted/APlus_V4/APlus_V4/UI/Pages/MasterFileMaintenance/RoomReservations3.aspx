<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="RoomReservations3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RoomReservations3"
    Title="Room Reservations" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>

    <script type="text/javascript" language="javascript">
        $(document).ready(function() {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>

    <table width="100%" runat="server" id="Table1">
        <tr>
            <td valign="middle" align="left" width="20%">
                <asp:Image ID="Image1" runat="server" ImageUrl="~/images/company_logo.png"></asp:Image>
            </td>
            <td align="center" width="60%">
                <table width="100%" runat="server" id="Table2">
                    <tr>
                        <td align="center">
                            <asp:Label ID="Label1" runat="server" Font-Size="Large" Font-Bold="True" Text="Room Reservation"></asp:Label>
                        </td>
                    </tr>
                </table>
            </td>
            <td align="right" width="20%">
                <asp:Image ID="Image4" runat="server" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </td>
        </tr>
    </table>
    <table runat="server" style="width: 584px; height: 140px" id="Table3">
        <tr>
            <td style="width: 110px; height: 15px">
            </td>
            <td style="height: 15px">
                <asp:TextBox ID="txtRoomReservationID" runat="server" CssClass="Textbox_Display"
                    MaxLength="10" Width="48px" ReadOnly="True" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label3" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="176px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblRouteAbbrev" runat="server" CssClass="Label_Left_8PT" Text="Room:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRoom" runat="server" CssClass="Textbox_Display" MaxLength="15"
                    Width="175px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblAttribute1" runat="server" CssClass="Label_Left_8PT" Text="Start Time:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtStartTime" runat="server" CssClass="Textbox_Display" MaxLength="12"
                    Width="150px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label4" runat="server" CssClass="Label_Left_8PT" Text="End Time:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEndTime" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="152px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblRoute" runat="server" CssClass="Label_Left_8PT" Text="Name/Description:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandDescription" runat="server" CssClass="Textbox_Display"
                    MaxLength="100" Width="325px" Height="28px" TextMode="MultiLine" Rows="1" 
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label9" runat="server" CssClass="Label_Left_8PT" Text="Catering:"
                    Visible="false"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckLunch" runat="server" Enabled="False" Visible="false"></asp:CheckBox>
                <asp:Label ID="Label12" runat="server" CssClass="Label_Left_8PT" Text="Lunch" Visible="false"></asp:Label>&nbsp;&nbsp;
                <asp:CheckBox ID="ckCoffee" runat="server" Enabled="False" Visible="false"></asp:CheckBox>
                <asp:Label ID="Label11" runat="server" CssClass="Label_Left_8PT" Text="Tea / Coffee"
                    Visible="false"></asp:Label>&nbsp;&nbsp;
                <asp:CheckBox ID="ckDinner" runat="server" Enabled="False" Visible="false"></asp:CheckBox>
                <asp:Label ID="Label2" runat="server" CssClass="Label_Left_8PT" Text="Dinner" Visible="false"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label10" runat="server" CssClass="Label_Left_8PT" Text="Video Conferencing:"
                    Visible="false"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckVideoConferencing" runat="server" Enabled="False" Visible="false">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label5" runat="server" CssClass="Label_Left_8PT" Text="Team:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeam" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label6" runat="server" CssClass="Label_Left_8PT" Text="Created By:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUserID" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px; height: 14px">
                <asp:Label ID="Label7" runat="server" CssClass="Label_Left_8PT" Text="Last Updated By:"></asp:Label>
            </td>
            <td style="height: 14px">
                <asp:TextBox ID="txtMaintenanceUserID" runat="server" Width="175px" MaxLength="15"
                    CssClass="Textbox_Display" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label8" runat="server" CssClass="Label_Left_8PT" Text="Last Updated:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMaintenanceDate" runat="server" Width="175px" MaxLength="15"
                    CssClass="Textbox_Display" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="Panel1" runat="server" HorizontalAlign="Left">
        <asp:Label ID="lblPrintDate" runat="server"></asp:Label>
    </asp:Panel>
</asp:Content>
