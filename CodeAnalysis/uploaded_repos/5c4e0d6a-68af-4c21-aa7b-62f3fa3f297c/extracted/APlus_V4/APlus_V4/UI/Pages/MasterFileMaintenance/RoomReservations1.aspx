<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RoomReservations1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RoomReservations1"
    Title="Room Reservations" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <style type="text/css">
        .webPlannerCaption
        {
            color: #000000;
            font-size: 8pt;
            font-family: Verdana;
            text-align: center;
            border-color: #C0C0C0;
            height: 20px;
            filter: progid:DXImageTransform.Microsoft.Gradient(GradientType=0, StartColorStr=#D4D0C8,EndColorStr=#FFFFFF);
        }
        .webPlannerSB
        {
            color: #000000;
            font-size: 8pt;
            font-family: Verdana;
            text-align: center;
            filter: progid:DXImageTransform.Microsoft.Gradient(GradientType=1, StartColorStr=#D4D0C8,EndColorStr=#FFFFFF);
        }
        .webPlannerTopBorder
        {
            border-top: black 1px solid;
        }
        .webPlannerSideBorders
        {
            border-right: black 1px solid;
            border-left: black 1px solid;
        }
        .webPlannerBottomBorder
        {
            border-bottom: black 1px solid;
        }
    </style>
    <table width="100%">
        <tr>
            <td valign="top" align="left" width="175">
                <asp:Panel ID="pnlCalendar" runat="server">
                    <table height="100%" width="100%">
                        <tr>
                            <td align="center">
                                <asp:Calendar ID="calReserve" runat="server" CellPadding="4" BorderColor="#999999"
                                    Font-Names="Verdana" Font-Size="8pt" ForeColor="Black" DayNameFormat="FirstLetter"
                                    BackColor="White" Height="104px" Width="175">
                                    <TodayDayStyle ForeColor="Black" BackColor="#CCCCCC"></TodayDayStyle>
                                    <SelectorStyle BackColor="#CCCCCC"></SelectorStyle>
                                    <NextPrevStyle VerticalAlign="Bottom"></NextPrevStyle>
                                    <DayHeaderStyle Font-Size="7pt" Font-Bold="True" BackColor="#CCCCCC"></DayHeaderStyle>
                                    <SelectedDayStyle Font-Bold="True" ForeColor="White" BackColor="#666666"></SelectedDayStyle>
                                    <TitleStyle Font-Bold="True" BorderColor="Black" BackColor="#999999"></TitleStyle>
                                    <WeekendDayStyle BackColor="#FFFFCC"></WeekendDayStyle>
                                    <OtherMonthDayStyle ForeColor="Gray"></OtherMonthDayStyle>
                                </asp:Calendar>
                                <asp:LinkButton ID="lbToday" runat="server">Go To Today:</asp:LinkButton>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                &nbsp;<br>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <asp:Button ID="btnReserveRoom" runat="server" Text="Reserve Room" 
                                    CssClass="Button_Variable" Visible="False">
                                </asp:Button>
                            </td>
                        </tr>
                    </table>
                </asp:Panel>
            </td>
            <td valign="top" align="left">
                <asp:Table ID="tblSchedule" runat="server" Width="100%" BorderColor="black" CellPadding="1"
                    BorderWidth="1" BorderStyle="Solid" CellSpacing="0" EnableViewState="False">
                </asp:Table>
            </td>
        </tr>
    </table>
    <table id="Table3" cellspacing="2" cellpadding="2" width="321" border="0">
        <tr>
            <td align="left">
                <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit"></asp:Button>
            </td>
        </tr>
    </table>
</asp:Content>
