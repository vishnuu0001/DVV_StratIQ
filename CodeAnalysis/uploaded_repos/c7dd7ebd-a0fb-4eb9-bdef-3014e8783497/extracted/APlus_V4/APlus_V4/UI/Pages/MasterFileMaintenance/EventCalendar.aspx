<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="EventCalendar.aspx.vb" Inherits="WebApp.APlus.UI.Pages.EventCalendar"
    Title="Event Calendar" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="Table1" runat="server" style="width: 100%">
        <tr>
            <td>
                <CC1:ApplicationEventCalendar DayField="EventDate" ID="calEvents" runat="server"
                    Width="100%" FirstDayOfWeek="Monday" ShowWeekNumber="true">
                    <TodayDayStyle BackColor="White" />
                    <OtherMonthDayStyle BackColor="LightGray" ForeColor="DarkGray" />
                    <DayStyle BackColor="LightYellow" VerticalAlign="Top" BorderColor="DimGray" HorizontalAlign="Left"
                        Font-Names="Arial" Font-Size="8pt" />
                    <ItemTemplate>
                    </ItemTemplate>
                    <NoEventsTemplate>
                        <br />
                        <br />
                        <br />
                        <br />
                        <br />
                    </NoEventsTemplate>
                </CC1:ApplicationEventCalendar>
            </td>
        </tr>
        <tr>
            <td>
            </td>
        </tr>
    </table>
    <table>
        <tr>
            <td align="left" style="border-right: black 1px solid" valign="top">
                <asp:RadioButtonList ID="rblTeams" runat="server" Width="200px" RepeatDirection="Vertical"
                    AutoPostBack="True">
                    <asp:ListItem Value="MyTeams" Selected="True">Show My Teams Meetings</asp:ListItem>
                    <asp:ListItem Value="AllTeams">Show All Teams Meetings</asp:ListItem>
                    <asp:ListItem Value="NoTeams">Hide All Teams Meetings</asp:ListItem>
                    <asp:ListItem Value="SelectedTeam">Show Selected Team Meetings Only</asp:ListItem>
                </asp:RadioButtonList>
            </td>
            <td align="left" style="width: 200px" valign="top">
                <asp:RadioButtonList ID="rblReservations" runat="server" Width="200px" RepeatDirection="Vertical"
                    AutoPostBack="True">
                    <asp:ListItem Value="MyReservations" Selected="True">Show My Room Reservations</asp:ListItem>
                    <asp:ListItem Value="NoReservations">Hide All Room Reservations</asp:ListItem>
                    <asp:ListItem Value="GroupReservations">Show Room Group Reservations</asp:ListItem>
                </asp:RadioButtonList>
                <asp:DropDownList ID="ddlRoomGroups" runat="server" Width="184px" AutoPostBack="True"
                    CssClass="Textbox_Entry" Visible="False">
                </asp:DropDownList>
            </td>
            <td>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            </td>
            <td align="left" style="width: 200px" valign="middle">
                <asp:Button ID="btnExit" runat="server" Text="Exit" CssClass="Button_Default"></asp:Button>
            </td>
            <td align="right" valign="middle">
                <asp:Button ID="btnRoomReservations" runat="server" CssClass="Button_Variable"
                    Text="Room Reservations"></asp:Button>
            </td>
        </tr>
    </table>
</asp:Content>
