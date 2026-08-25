<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="RoomReservations2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.RoomReservations2"
    Title="Room Reservations" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            height: 6px;
        }
    </style>
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 133px">
                <asp:Label ID="Label7" runat="server" Text="Room Reservation ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRoomReservationID" runat="server" Width="48px" CssClass="Textbox_Display"
                    ReadOnly="True" MaxLength="10"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="lblAttribute1" runat="server" CssClass="Label_Left_8PT" Text="Date:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDate" runat="server" Width="88px" CssClass="Textbox_Display"
                    MaxLength="12" ReadOnly="True"></asp:TextBox>
                <cc1:CalendarExtender ID="txtDate_CalendarExtender" runat="server" PopupButtonID="imgDate"
                    TargetControlID="txtDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqDate" runat="server" Display="None" ControlToValidate="txtDate"
                    ErrorMessage="Enter a Value Date"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="Label1" runat="server" CssClass="Label_Left_8PT" Text="Room:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlRoom" runat="server" Width="216px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtRoom" runat="server" Width="232px" CssClass="Textbox_Display"
                    ReadOnly="True" MaxLength="10" Visible="False"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqRoom" runat="server" Display="None" ControlToValidate="ddlRoom" ErrorMessage="Select Conference Room"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="Label4" runat="server" CssClass="Label_Left_8PT" Text="Start Time:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlStartTime" runat="server" Width="40px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="00" Text="00"></asp:ListItem>
                    <asp:ListItem Value="01" Text="01"></asp:ListItem>
                    <asp:ListItem Value="02" Text="02"></asp:ListItem>
                    <asp:ListItem Value="03" Text="03"></asp:ListItem>
                    <asp:ListItem Value="04" Text="04"></asp:ListItem>
                    <asp:ListItem Value="05" Text="05"></asp:ListItem>
                    <asp:ListItem Value="06" Text="06"></asp:ListItem>
                    <asp:ListItem Value="07" Text="07"></asp:ListItem>
                    <asp:ListItem Value="08" Text="08"></asp:ListItem>
                    <asp:ListItem Value="09" Text="09"></asp:ListItem>
                    <asp:ListItem Value="10" Text="10"></asp:ListItem>
                    <asp:ListItem Value="11" Text="11"></asp:ListItem>
                    <asp:ListItem Value="12" Text="12"></asp:ListItem>
                    <asp:ListItem Value="13" Text="13"></asp:ListItem>
                    <asp:ListItem Value="14" Text="14"></asp:ListItem>
                    <asp:ListItem Value="15" Text="15"></asp:ListItem>
                    <asp:ListItem Value="16" Text="16"></asp:ListItem>
                    <asp:ListItem Value="17" Text="17"></asp:ListItem>
                    <asp:ListItem Value="18" Text="18"></asp:ListItem>
                    <asp:ListItem Value="19" Text="19"></asp:ListItem>
                    <asp:ListItem Value="20" Text="20"></asp:ListItem>
                    <asp:ListItem Value="21" Text="21"></asp:ListItem>
                    <asp:ListItem Value="22" Text="22"></asp:ListItem>
                    <asp:ListItem Value="23" Text="23"></asp:ListItem>
                </asp:DropDownList>
                <asp:DropDownList ID="ddlStartTimeMinutes" runat="server" Width="40px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="00">00</asp:ListItem>
                    <asp:ListItem Value="30">30</asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtStartTime" runat="server" Width="56px" CssClass="Textbox_Display"
                    ReadOnly="True" MaxLength="10" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="Label5" runat="server" CssClass="Label_Left_8PT" Text="End Time:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlEndTime" runat="server" Width="40px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="00" Text="00"></asp:ListItem>
                    <asp:ListItem Value="01" Text="01"></asp:ListItem>
                    <asp:ListItem Value="02" Text="02"></asp:ListItem>
                    <asp:ListItem Value="03" Text="03"></asp:ListItem>
                    <asp:ListItem Value="04" Text="04"></asp:ListItem>
                    <asp:ListItem Value="05" Text="05"></asp:ListItem>
                    <asp:ListItem Value="06" Text="06"></asp:ListItem>
                    <asp:ListItem Value="07" Text="07"></asp:ListItem>
                    <asp:ListItem Value="08" Text="08"></asp:ListItem>
                    <asp:ListItem Value="09" Text="09"></asp:ListItem>
                    <asp:ListItem Value="10" Text="10"></asp:ListItem>
                    <asp:ListItem Value="11" Text="11"></asp:ListItem>
                    <asp:ListItem Value="12" Text="12"></asp:ListItem>
                    <asp:ListItem Value="13" Text="13"></asp:ListItem>
                    <asp:ListItem Value="14" Text="14"></asp:ListItem>
                    <asp:ListItem Value="15" Text="15"></asp:ListItem>
                    <asp:ListItem Value="16" Text="16"></asp:ListItem>
                    <asp:ListItem Value="17" Text="17"></asp:ListItem>
                    <asp:ListItem Value="18" Text="18"></asp:ListItem>
                    <asp:ListItem Value="19" Text="19"></asp:ListItem>
                    <asp:ListItem Value="20" Text="20"></asp:ListItem>
                    <asp:ListItem Value="21" Text="21"></asp:ListItem>
                    <asp:ListItem Value="22" Text="22"></asp:ListItem>
                    <asp:ListItem Value="23" Text="23"></asp:ListItem>
                </asp:DropDownList>
                <asp:DropDownList ID="ddlEndTimeMinutes" runat="server" Width="40px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="00">00</asp:ListItem>
                    <asp:ListItem Value="30">30</asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtEndTime" runat="server" Width="56px" CssClass="Textbox_Display"
                    ReadOnly="True" MaxLength="10" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="lblRoute" runat="server" CssClass="Label_Left_8PT" Text="Name/Description:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandDescription" runat="server" Width="325px" CssClass="Textbox_Entry"
                    MaxLength="100" Height="32px" TextMode="MultiLine" Rows="1"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqDescription" runat="server" Display="None" ControlToValidate="txtExpandDescription"
                        ErrorMessage="Enter Description"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <asp:Panel runat="server" ID="pnlNotes" Visible="false">
            <tr>
                <td style="width: 133px">
                    <asp:Label ID="Label11" runat="server" CssClass="Label_Left_8PT" Text="Notes:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandNotes" runat="server" Width="325px" CssClass="Textbox_Entry"
                        MaxLength="100" Height="32px" TextMode="MultiLine" Rows="1"></asp:TextBox>
                </td>
            </tr>
        </asp:Panel>
        <tr>
            <td style="width: 133px; height: 19px">
                <asp:Label ID="Label9" runat="server" CssClass="Label_Left_8PT" Text="Catering:"
                    Visible="false"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckLunch" runat="server" Text="Lunch" Visible="false"></asp:CheckBox>&nbsp;
                <asp:CheckBox ID="ckCoffee" runat="server" Text="Tea / Coffee" Visible="false"></asp:CheckBox>&nbsp;
                <asp:CheckBox ID="ckDinner" runat="server" Text="Dinner" Visible="false"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="Label10" runat="server" CssClass="Label_Left_8PT" Text="Video Conferencing:"
                    Visible="false"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckVideoConferencing" runat="server" Visible="false"></asp:CheckBox>
            </td>
        </tr>
        <asp:Panel runat="server" ID="pnlTeam">
            <tr>
                <td style="width: 133px">
                    <asp:Label ID="Label2" runat="server" CssClass="Label_Left_8PT" Text="Team:"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlTeam" runat="server" Width="216px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtTeam" runat="server" Width="232px" CssClass="Textbox_Display"
                        ReadOnly="True" MaxLength="10" Visible="False"></asp:TextBox>
                </td>
            </tr>
        </asp:Panel>
        <tr>
            <td style="width: 133px">
                <asp:Label ID="Label6" runat="server" CssClass="Label_Left_8PT" Text="Created By:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUserID" runat="server" Width="160px" CssClass="Textbox_Display"
                    ReadOnly="True" MaxLength="15"></asp:TextBox>
            </td>
        </tr>
        <asp:Panel ID="pnlMaintenance" runat="server">
            <tr>
                <td style="width: 133px">
                    <asp:Label ID="Label3" runat="server" CssClass="Label_Left_8PT" Text="Last Updated By:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtMaintUserID" runat="server" MaxLength="10" ReadOnly="True" CssClass="Textbox_Display"
                        Width="160px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 133px">
                    <asp:Label ID="Label8" runat="server" CssClass="Label_Left_8PT" Text="Last Updated:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtMaintDate" runat="server" MaxLength="10" ReadOnly="True" CssClass="Textbox_Display"
                        Width="160px"></asp:TextBox>
                </td>
            </tr>
        </asp:Panel>
        <tr>
            <td style="width: 133px">
                <asp:HyperLink ID="lnkPrintPage" runat="server" Visible="False" NavigateUrl="~/UI/Pages/DataCollectionPrograms/TeamRouteSteps3.aspx"
                    Target="_blank" Text="Printer Friendly Version"></asp:HyperLink>
            </td>
            <td>
            </td>
        </tr>
    </table>
    <table id="Table2" style="width: 321px; height: 26px" cellspacing="2" cellpadding="2"
        width="321" border="0">
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td style="width: 110px">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnDelete" runat="server" CssClass="Button_Default" Visible="False"
                        Text="Delete" CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
