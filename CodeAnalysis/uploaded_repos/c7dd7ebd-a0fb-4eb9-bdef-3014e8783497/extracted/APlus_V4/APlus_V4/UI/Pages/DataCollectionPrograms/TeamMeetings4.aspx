<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamMeetings4.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamMeetings4"
    Title="Team Meetings" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/APlusTimeControl.ascx" TagName="APlusTimeControl"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="Table1" class="Table_Default">
        <tr>
            <td style="width: 178px">
                <asp:Label runat="server" ID="Label1" Text="Original Meeting Date / Time" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:Label runat="server" ID="Label2" Text="New Meeting Date / Time" CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 178px">
                <table>
                    <tr>
                        <td style="width: 80px">
                            <asp:Label ID="Label5" runat="server" Text="Meeting Date:" CssClass="Label_Left_8PT"></asp:Label>
                        </td>
                        <td>
                            <asp:TextBox ID="txtOldMeetingDate" runat="server" CssClass="Textbox_Display" MaxLength="10"
                                Width="77" ReadOnly="True"></asp:TextBox>
                        </td>
                    </tr>
                    <tr>
                        <td style="width: 80px">
                            <asp:Label ID="Label8" runat="server" Width="76px" Text="Meeting Time:" CssClass="Label_Left_8PT"></asp:Label>
                        </td>
                        <td>
                            <asp:TextBox ID="txtOldMeetingTime" runat="server" CssClass="Textbox_Display" Width="77px"
                                MaxLength="5" ReadOnly="True"></asp:TextBox>
                        </td>
                    </tr>
                </table>
            </td>
            <td>
                <table id="Table2" class="Table_Default">
                    <tr>
                        <td style="width: 80px">
                            <asp:Label ID="Label6" runat="server" Text="Meeting Date:" CssClass="Label_Left_8PT"></asp:Label>
                        </td>
                        <td>
                            <asp:TextBox ID="txtMeetingDate" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                                Width="76px"></asp:TextBox>
                            <cc1:CalendarExtender ID="txtMeetingDate_CalendarExtender" runat="server" PopupButtonID="imgMeetingDate"
                                TargetControlID="txtMeetingDate" CssClass="APlus_Calendar">
                            </cc1:CalendarExtender>
                            <asp:ImageButton ID="imgMeetingDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                                ToolTip="Click to Select Date..." CausesValidation="False" />
                            <asp:CompareValidator ID="Comparevalidator2" runat="server" ErrorMessage="Invalid Meeting Date"
                                ControlToValidate="txtMeetingDate" Display="None" Operator="DataTypeCheck" Type="Date"
                                CssClass="Label_Left_8PT"></asp:CompareValidator>
                            <asp:RequiredFieldValidator ID="Requiredfieldvalidator2" runat="server" ErrorMessage="Enter a Meeting Date"
                                ControlToValidate="txtMeetingDate" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                        </td>
                    </tr>
                    <tr>
                        <td style="width: 80px">
                            <asp:Label ID="Label7" runat="server" Width="76px" Text="Meeting Time:" CssClass="Label_Left_8PT"></asp:Label>
                        </td>
                        <td>
                            <uc1:APlusTimeControl ID="ucMeetingTime" runat="server"></uc1:APlusTimeControl>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    <asp:Panel ID="Panel1" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
