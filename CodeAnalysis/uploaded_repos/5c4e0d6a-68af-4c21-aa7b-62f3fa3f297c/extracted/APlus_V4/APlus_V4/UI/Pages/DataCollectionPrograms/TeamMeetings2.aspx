<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamMeetings2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamMeetings2"
    Title="Team Meetings" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/APlusTimeControl.ascx" TagName="APlusTimeControl"
    TagPrefix="uc1" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table id="Table1" class="Table_Default">
        <tr>
            <td style="width: 76px">
                <asp:Label ID="lblMeetingDate" runat="server" Text="Meeting Date:" CssClass="Label_Left_8PT"></asp:Label><br />
            </td>
            <td style="width: 100px">
                <asp:TextBox ID="txtMeetingDate" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="76px"></asp:TextBox>
                <cc1:CalendarExtender ID="txtMeetingDate_CalendarExtender" runat="server" PopupButtonID="imgMeetingDate"
                    TargetControlID="txtMeetingDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgMeetingDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqMeetingDate" runat="server" ErrorMessage="Enter a Meeting Date"
                    ControlToValidate="txtMeetingDate" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator><asp:CompareValidator
                        ID="cmpMeetingDate" runat="server" ErrorMessage="Invalid Meeting Date" ControlToValidate="txtMeetingDate"
                        Display="None" Operator="DataTypeCheck" Type="Date" CssClass="Label_Left_8PT"></asp:CompareValidator>
            </td>
            <td style="width: 76px" valign="middle">
                <asp:Label ID="lblMeetingTime" runat="server" Width="76px" Text="Meeting Time:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 114px">
                <uc1:APlusTimeControl ID="ucMeetingTime" runat="server"></uc1:APlusTimeControl>
                <asp:TextBox ID="txtMeetingTime" runat="server" CssClass="Textbox_Display" Width="34px"></asp:TextBox>
            </td>
            <td style="width: 54px">
                <asp:Label ID="lblDuration" runat="server" Text="Duration:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 80px">
                <asp:TextBox ID="txtMeetingLength" runat="server" CssClass="Textbox_Entry" MaxLength="10"
                    Width="76px"></asp:TextBox>
            </td>
            <td>
                <asp:CheckBox ID="chkAudit" runat="server" Text="Audit" Font-Bold="True"></asp:CheckBox>
            </td>
        </tr>
    </table>
    <table cellspacing="0" cellpadding="0" style="width: 100%">
        <tr>
            <td valign="top" width="40%">
                <table id="TABLE2" class="Table_Default">
                    <tr>
                        <td style="vertical-align: top; width: 338px;">
                            <asp:Label ID="lblMeetingLocation" runat="server" Text="Meeting Location:" CssClass="Label_Left_8PT"></asp:Label><asp:TextBox
                                ID="txtMeetingLocation" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                                Width="290px"></asp:TextBox>
                            <asp:Button ID="btnLookupRoom" runat="server" Width="16px" CssClass="Button_Variable"
                                Text="..." CausesValidation="False"></asp:Button>
                            <asp:RequiredFieldValidator ID="reqMeetingLocation" runat="server" ErrorMessage="Enter Meeting Location"
                                ControlToValidate="txtMeetingLocation" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                        </td>
                    </tr>
                    <tr>
                        <td valign="top" style="width: 338px">
                            <asp:Label ID="lblAgenda" runat="server" Text="Agenda:" CssClass="Label_Left_8PT"></asp:Label><br />
                            <asp:TextBox ID="txtExpandAgenda" runat="server" CssClass="Textbox_Entry" Width="460px"
                                Height="28px" Rows="8" TextMode="MultiLine"></asp:TextBox>
                            <asp:RequiredFieldValidator ID="reqAgenda" runat="server" ErrorMessage="Enter Agenda "
                                ControlToValidate="txtExpandAgenda" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                            <asp:RegularExpressionValidator ID="reqValidAgenda" runat="server" ErrorMessage="Agenda must be less then 2000 characters"
                                ControlToValidate="txtExpandAgenda" Display="None" ValidationExpression="(.|\n){1,2000}"
                                CssClass="Label_Left_8PT"></asp:RegularExpressionValidator>
                        </td>
                    </tr>
                    <tr>
                        <td style="width: 338px" valign="top">
                            <asp:Label ID="lblMinutes" runat="server" Text="Minutes:" CssClass="Label_Left_8PT"></asp:Label><br />
                            <asp:TextBox ID="txtExpandMinutes" runat="server" CssClass="Textbox_Entry" Width="460px"
                                Height="28px" Rows="20" TextMode="MultiLine"></asp:TextBox>
                        </td>
                    </tr>
                    <tr>
                        <td valign="top" style="width: 338px">
                            <asp:Label ID="lblAgendaNextMeeting" runat="server" Text="Agenda For Next Meeting:"
                                CssClass="Label_Left_8PT"></asp:Label><br />
                            <asp:TextBox ID="txtExpandAgendaNextMeeting" runat="server" CssClass="Textbox_Entry"
                                Width="460px" Height="28px" TextMode="MultiLine"></asp:TextBox>
                            <asp:RegularExpressionValidator ID="reqValidNextAgenda" runat="server" ErrorMessage="Next Meeting Agenda must be less then 2000 characters"
                                ControlToValidate="txtExpandAgendaNextMeeting" Display="None" ValidationExpression="(.|\n){1,2000}"
                                CssClass="Label_Left_8PT"></asp:RegularExpressionValidator>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table id="TABLE3" class="Table_Default">
                                <tr>
                                    <td style="vertical-align: middle; width: 144px;">
                                        <asp:Label ID="Label2" runat="server" Text="Next Proposed Meeting Date:" CssClass="Label_Left_8PT"></asp:Label>
                                    </td>
                                    <td colspan="3">
                                        <asp:TextBox ID="txtNextMeeting" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                                            Width="76px"></asp:TextBox><cc1:CalendarExtender ID="txtNextMeeting_CalendarExtender"
                                                runat="server" PopupButtonID="imgNextMeeting" TargetControlID="txtNextMeeting"
                                                CssClass="APlus_Calendar">
                                            </cc1:CalendarExtender>
                                        <asp:ImageButton ID="imgNextMeeting" runat="server" ImageUrl="~/Images/date-time_select.gif"
                                            ToolTip="Click to Select Date..." CausesValidation="False" />
                                        <asp:CompareValidator ID="cmpNextMeeting" runat="server" ErrorMessage="Invalid Next Meeting Date"
                                            ControlToValidate="txtNextMeeting" Display="None" Operator="DataTypeCheck" Type="Date"
                                            CssClass="Label_Left_8PT"></asp:CompareValidator>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="width: 144px">
                                        <asp:Label ID="lblMaintenanceUserID" runat="server" Text="Maintenance UserID:"></asp:Label>
                                    </td>
                                    <td style="width: 85px">
                                        <asp:TextBox ID="txtMaintenanceUserID" runat="server" CssClass="Textbox_Display"
                                            MaxLength="10" Width="69px"></asp:TextBox>
                                    </td>
                                    <td style="width: 95px">
                                        <asp:Label ID="lblMaintenanceDate" runat="server" Text="Maintenance Date:" CssClass="Label_Left_8PT"></asp:Label>
                                    </td>
                                    <td>
                                        <asp:TextBox ID="txtMaintenanceDate" runat="server" CssClass="Textbox_Display" MaxLength="50"
                                            Width="120px"></asp:TextBox>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <asp:CheckBox ID="chkSendMeetingStatusEmail" runat="server" Text="Send a Meeting Status Email when Saved"
                                Font-Bold="True"></asp:CheckBox>&nbsp;&nbsp;<asp:CheckBox ID="chkEmailInvited" runat="server"
                                    Text="Send Only to Invited"></asp:CheckBox>
                        </td>
                    </tr>
                </table>
            </td>
            <td width="0" valign="top">
                <table class="Table_Default" id="Table5">
                    <tr>
                        <td>
                            <asp:Label ID="lblTeamMeetingAttendance" runat="server" Text="Team Meeting Attendance:"
                                CssClass="Label_Left_8PT"></asp:Label>
                            <asp:GridView ID="gvTeamMeetingAttendance" runat="server" AutoGenerateColumns="False"
                                SkinID="GridView" Width="435px" DataKeyNames="UserID">
                                <Columns>
                                    <asp:BoundField DataField="UserID" HeaderText="UserID" ReadOnly="True" Visible="false" />
                                    <asp:BoundField DataField="UserName" HeaderText="User Name" ReadOnly="True" HtmlEncode="false" />
                                    <asp:TemplateField HeaderText="Invited">
                                        <ItemTemplate>
                                            <asp:CheckBox ID="chkInvited" runat="server" Checked='<%# Bind("Invited") %>' Enabled="true" />
                                        </ItemTemplate>
                                    </asp:TemplateField>
                                    <asp:TemplateField HeaderText="Attended">
                                        <ItemTemplate>
                                            <asp:CheckBox ID="chkAttended" runat="server" Checked='<%# Bind("Attended") %>' Enabled="true" />
                                        </ItemTemplate>
                                    </asp:TemplateField>
                                    <asp:BoundField DataField="EmailAddress" HeaderText="Email Address" ReadOnly="True" />
                                </Columns>
                            </asp:GridView>
                            <br />
                            <table id="Table6" class="Table_Default">
                                <tr>
                                    <td style="width: 127px">
                                        <asp:Button ID="btnNewUserToAttendMeeting" runat="server" CssClass="Button_Default"
                                            Width="120px" Text="Add New User"></asp:Button>
                                    </td>
                                    <td style="width: 127px">
                                        <asp:Button ID="btnCheckAllAttended" runat="server" CssClass="Button_Default" Width="120px"
                                            Text="Check ALL Attended"></asp:Button>
                                    </td>
                                    <td>
                                        <asp:Button ID="btnRemoveUsers" runat="server" CssClass="Button_Default" Text="Remove User">
                                        </asp:Button>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <br />
                            <br />
                            <asp:Label ID="lblTeamActionPlan" runat="server" Text="Team Meeting Action Plan:"
                                CssClass="Label_Left_8PT"></asp:Label><asp:GridView ID="gvTeamActionPlan" runat="server"
                                    SkinID="GridView" Width="435px">
                                    <Columns>
                                        <asp:BoundField DataField="UserName" HeaderText="Assigned" ReadOnly="True" />
                                        <asp:BoundField DataField="ActionItem" HeaderText="Action" ReadOnly="True" />
                                        <asp:BoundField DataField="TargetDate" DataFormatString="{0:d}" HeaderText="Target"
                                            ReadOnly="True" />
                                        <asp:BoundField DataField="ClosedDate" DataFormatString="{0:d}" HeaderText="Closed"
                                            ReadOnly="True" />
                                    </Columns>
                                </asp:GridView>
                            <br />
                            <asp:Button ID="btnNewTeamActionPlan" runat="server" CssClass="Button_Default" Width="120px"
                                Text="Add New Team Action "></asp:Button>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    <div>
        <asp:HyperLink ID="lnkPrintPage" runat="server" Visible="False" Target="_blank" NavigateUrl="~/UI/Pages/DataCollectionPrograms/TeamRouteSteps3.aspx"
            Text="Printer Friendly Version" CssClass="Link_Default"></asp:HyperLink></div>
    <div>
        <br />
        <asp:HyperLink ID="lnkAddToCalendar" runat="server" Visible="False" Target="_blank"
            NavigateUrl="~/UI/UserControls/TeamMeetingCalendarEvent.aspx" Text="Add Meeting to my Outlook Calendar"
            CssClass="Link_Default"></asp:HyperLink></div>
    <asp:Panel runat="server" ID="pnlConfirm" Visible="False">
        <br />
        <table style="width: 368px; height: 105px">
            <tr>
                <td style="width: 61px" rowspan="2">
                    <img alt="Help" id="imgQuestion" src="~/Images/HelpDoc.gif" runat="server" />
                </td>
                <td colspan="2">
                    <br />
                    <asp:Label ID="Label3" runat="server" Width="295px" Font-Size="10pt">You have entered a Next Proposed Meeting Date. Do you want to create this new meeting now?</asp:Label>
                </td>
            </tr>
            <tr>
                <td style="width: 13px">
                    <asp:Button ID="btnConfirm" runat="server" CssClass="Button_Default" Text="Yes">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnConfirmCancel" runat="server" CssClass="Button_Default" Text="No"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
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
                <td style="width: 150px">
                    <asp:Button ID="btnReschedule" runat="server" CssClass="Button_Variable" Text="Reschedule Meeting"
                        CausesValidation="False" Visible="False"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnReserveRoom" runat="server" CssClass="Button_Variable" Text="Reserve Room"
                        Visible="False" />
                </td>
            </tr>
            <tr>
                <td>
                </td>
                <td align="left">
                </td>
                <td align="left">
                </td>
                <td align="left">
                    &nbsp;
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table4" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
