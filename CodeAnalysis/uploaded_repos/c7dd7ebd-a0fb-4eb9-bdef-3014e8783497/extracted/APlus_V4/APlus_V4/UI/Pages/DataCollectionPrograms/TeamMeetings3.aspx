<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="TeamMeetings3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamMeetings3"
    Title="Team Meetings" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>

    <script type="text/javascript" language="javascript">
        $(document).ready(function() {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>

    <table id="Table1" width="100%" runat="server">
        <tr>
            <td valign="middle" align="left" width="20%">
                <asp:Image ID="Image1" runat="server" ImageUrl="~/Images/company_logo.png"></asp:Image>
            </td>
            <td align="center" width="60%">
                <table id="Table2" width="100%" runat="server">
                    <tr>
                        <td align="center">
                            <asp:Label ID="lblTeamMeeting" runat="server" Font-Bold="True" Font-Size="Large"
                                Text="Team Meeting"></asp:Label>
                        </td>
                    </tr>
                    <tr>
                        <td align="center">
                            <asp:Label ID="lblTeamName" runat="server" Font-Bold="True" Text="Team Name goes Here"></asp:Label>
                        </td>
                    </tr>
                    <tr>
                        <td align="center">
                            <asp:Label ID="lblTeam" runat="server" Font-Bold="True" Text="Team goes Here"></asp:Label>
                        </td>
                    </tr>
                </table>
            </td>
            <td align="right" width="20%">
                <asp:Image ID="Image4" runat="server" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </td>
        </tr>
    </table>
    <table class="Table_Default" id="Table3" style="width: 658px" cellspacing="2" cellpadding="2"
        border="0">
        <tr>
            <td style="width: 85px" valign="top">
                <asp:Label ID="lblMeetingDate" runat="server" Text="Meeting Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 157px" valign="top">
                <asp:TextBox ID="txtMeetingDate" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="76px" BackColor="White"></asp:TextBox>
            </td>
            <td style="width: 85px" valign="top">
                <asp:Label ID="lblMeetingTime" runat="server" Width="80px" Text="Meeting Time:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 125px" valign="top">
                <asp:TextBox ID="txtMeetingTime" runat="server" CssClass="Textbox_Display" Width="34px"
                    BackColor="White"></asp:TextBox>
            </td>
            <td>
                <asp:CheckBox ID="chkAudit" runat="server" Font-Bold="True" Text="Audit" Enabled="False">
                </asp:CheckBox>
            </td>
        </tr>
    </table>
    <table width="100%">
        <tr>
            <td valign="top" align="left" style="width: 350px">
                <table>
                    <tr>
                        <td style="width: 350px" valign="top">
                            <asp:Label ID="lblMeetingLocation" runat="server" Text="Meeting Location:" CssClass="Label_Left_8PT"></asp:Label><br />
                            <asp:TextBox ID="txtMeetingLocation" runat="server" CssClass="Textbox_Display" MaxLength="50"
                                Width="270px" BackColor="White"></asp:TextBox>
                        </td>
                    </tr>
                    <tr>
                        <td style="width: 350px" valign="top">
                            <asp:Label ID="lblAgenda" runat="server" Text="Agenda:" CssClass="Label_Left_8PT"></asp:Label><br />
                            <asp:TextBox ID="txtExpandAgenda" runat="server" CssClass="Textbox_Display" MaxLength="1000"
                                Width="500px" Height="28px" Rows="8" TextMode="MultiLine" 
                                BackColor="White"></asp:TextBox>
                        </td>
                    </tr>
                    <tr>
                        <td style="width: 350px" valign="top">
                            <asp:Label ID="lblMinutes" runat="server" Text="Minutes:" CssClass="Label_Left_8PT"></asp:Label><br />
                            <asp:TextBox ID="txtExpandMinutes" runat="server" Width="500px" MaxLength="2250"
                                CssClass="Textbox_Display" TextMode="MultiLine" Rows="20" Height="28px" 
                                BackColor="White"></asp:TextBox>
                        </td>
                    </tr>
                    <tr>
                        <td style="width: 350px" valign="top">
                            <asp:Label ID="lblAgendaNextMeeting" runat="server" Text="Agenda For Next Meeting:"
                                CssClass="Label_Left_8PT"></asp:Label><br />
                            <asp:TextBox ID="txtExpandAgendaNextMeeting" runat="server" Width="500px" MaxLength="1000"
                                CssClass="Textbox_Display" TextMode="MultiLine" Height="28px" 
                                BackColor="White"></asp:TextBox>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table id="TABLE4" class="Table_Default">
                                <tr>
                                    <td style="vertical-align: middle; width: 144px;">
                                        <asp:Label ID="lblNextMeetingDate" runat="server" Text="Next Proposed Meeting Date:"
                                            CssClass="Label_Left_8PT"></asp:Label>
                                    </td>
                                    <td colspan="3">
                                        <asp:TextBox ID="txtNextMeeting" runat="server" CssClass="Textbox_Display" MaxLength="50"
                                            Width="120px" BackColor="White"></asp:TextBox>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="width: 144px">
                                        <asp:Label ID="lblMaintenanceUserID" runat="server" Text="Maintenance UserID:"></asp:Label>
                                    </td>
                                    <td style="width: 85px">
                                        <asp:TextBox ID="txtMaintenanceUserID" runat="server" CssClass="Textbox_Display"
                                            MaxLength="10" Width="69px" BackColor="White"></asp:TextBox>
                                    </td>
                                    <td style="width: 95px">
                                        <asp:Label ID="lblMaintenanceDate" runat="server" Text="Maintenance Date:" CssClass="Label_Left_8PT"></asp:Label>
                                    </td>
                                    <td>
                                        <asp:TextBox ID="txtMaintenanceDate" runat="server" CssClass="Textbox_Display" MaxLength="50"
                                            Width="120px" BackColor="White"></asp:TextBox>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
            <td valign="top">
                <table>
                    <tr>
                        <td valign="top" align="left">
                            &nbsp;
                            <asp:Label ID="lblTeamMeetingAttendance" runat="server" Text="Team Meeting Attendance:"
                                CssClass="Label_Left_8PT"></asp:Label>
                            <asp:GridView ID="gvTeamMeetingAttendance" runat="server" AutoGenerateColumns="False"
                                SkinID="GridView" Width="390px">
                                <Columns>
                                    <asp:BoundField DataField="UserName" HeaderText="User Name" ReadOnly="True" />
                                    <asp:TemplateField HeaderText="Invited">
                                        <ItemTemplate>
                                            <asp:CheckBox ID="CheckBox1" runat="server" Checked='<%# Bind("Invited") %>' Enabled="false" />
                                        </ItemTemplate>
                                    </asp:TemplateField>
                                    <asp:TemplateField HeaderText="Attended">
                                        <ItemTemplate>
                                            <asp:CheckBox ID="CheckBox2" runat="server" Checked='<%# Bind("Attended") %>' Enabled="false" />
                                        </ItemTemplate>
                                    </asp:TemplateField>
                                    <asp:BoundField DataField="EmailAddress" HeaderText="Email Address" />
                                </Columns>
                            </asp:GridView>
                            <br />
                        </td>
                    </tr>
                    <tr>
                        <td valign="top">
                            &nbsp;
                            <asp:Label ID="lblTeamActionPlan" runat="server" Text="Team Meeting Action Plan:"
                                CssClass="Label_Left_8PT"></asp:Label>
                            <asp:GridView ID="gvTeamActionPlan" runat="server" AutoGenerateColumns="False" SkinID="GridView"
                                Width="392px">
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
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    <asp:Label ID="lblPrintDate" runat="server"></asp:Label>
    <br />
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style4
        {
            width: 170px;
        }
    </style>
</asp:Content>
