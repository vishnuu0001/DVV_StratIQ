<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamStatus.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamStatus"
    Title="Team Status" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 200px;
        }
    </style>
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 75px">
                <asp:Label ID="lblPillar" runat="server" Text="Pillar:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 310px">
                <asp:TextBox ID="txtPillar" runat="server" BorderStyle="None" ReadOnly="True" Width="300px"
                    MaxLength="50" CssClass="Textbox_Display" Height="16px"></asp:TextBox>
            </td>
            <td style="width: 75px">
                <asp:Label ID="lblTeamStartDate" runat="server" Text="Start Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamStartDate" BorderStyle="None" ReadOnly="True" MaxLength="10"
                    CssClass="Textbox_Display" runat="server" Height="16px" Width="100px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 75px">
                <asp:Label ID="lblRoute" runat="server" Text="Route:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 310px">
                <asp:TextBox ID="txtRoute" runat="server" BorderStyle="None" ReadOnly="True" Width="300px"
                    MaxLength="50" CssClass="Textbox_Display"></asp:TextBox>
            </td>
            <td style="width: 75px">
                <asp:Label ID="lblTeamFinishDate" runat="server" Text="Finish Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamFinishDate" BorderStyle="None" ReadOnly="True" MaxLength="10"
                    CssClass="Textbox_Display" runat="server"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 75px">
                <asp:Label ID="lblDept" runat="server" Text="Department:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 310px">
                <asp:TextBox ID="txtDept" BorderStyle="None" ReadOnly="True" Width="37px" MaxLength="30"
                    CssClass="Textbox_Display" runat="server"></asp:TextBox>
            </td>
            <td style="width: 75px">
                <asp:Label ID="lblTeamStatus" runat="server" Text="Status:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamStatus" BorderStyle="None" ReadOnly="True" Width="185px"
                    MaxLength="1" CssClass="Textbox_Display" runat="server"></asp:TextBox>
            </td>
        </tr>
    </table>
    <table id="Table8" cellpadding="0" cellspacing="0">
        <tr>
            <td align="left" valign="top" colspan="2">
                <asp:Label ID="lblTeamMeetingAttendance" runat="server" Text="Team Meeting Attendance:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
    </table>
    <table id="Table2" cellpadding="0" cellspacing="0">
        <tr>
            <td align="left" valign="top" style="width: 142px">
                <asp:GridView ID="gvTeamMeetingAttendance" runat="server" AutoGenerateColumns="False"
                    BorderStyle="None" Width="130px" CellPadding="0" CellSpacing="0" BorderColor="#999999"
                    BackColor="White" BorderWidth="1px" GridLines="Vertical">
                    <SelectedRowStyle Font-Bold="true" ForeColor="White" BackColor="#008A8C" />
                    <AlternatingRowStyle Height="20px" BackColor="#E7E7E7" HorizontalAlign="Left" />
                    <RowStyle Height="20px" ForeColor="Black" BackColor="#f5f5f5" HorizontalAlign="Left" />
                    <HeaderStyle Font-Bold="true" Height="38px" ForeColor="White" BackColor="#41519A" />
                    <EmptyDataRowStyle Wrap="False" />
                    <Columns>
                        <asp:BoundField DataField="UserName" HeaderText="User Name" ReadOnly="True" ItemStyle-Wrap="False" />
                        <asp:BoundField DataField="Title" HeaderText="Title" ReadOnly="True" ItemStyle-Wrap="False" />
                        <asp:BoundField DataField="Role" HeaderText="Role" ReadOnly="True" ItemStyle-Wrap="False" />
                    </Columns>
                </asp:GridView>
            </td>
            <td align="left" valign="top">
                <asp:Panel ID="Panel1" runat="server" Width="541" ScrollBars="Horizontal" Wrap="False"
                    CssClass="DataGridPanel">
                    <asp:GridView ID="gvTeamMeetingAttendance2" runat="server" AutoGenerateColumns="False"
                        BorderStyle="None" GridLines="Vertical" BorderWidth="1px" BackColor="White" BorderColor="#999999"
                        CellPadding="3">
                        <SelectedRowStyle Font-Bold="True" ForeColor="White" BackColor="#008A8C" />
                        <AlternatingRowStyle BackColor="#E7E7E7" />
                        <RowStyle ForeColor="Black" BackColor="#f5f5f5" />
                        <HeaderStyle Font-Bold="True" Height="38px" ForeColor="White" BackColor="#41519A" />
                        <Columns>
                        </Columns>
                    </asp:GridView>
                </asp:Panel>
            </td>
        </tr>
    </table>
    <table>
        <tr>
            <td class="style1">
                <asp:CheckBox ID="chkAttendance" runat="server" AutoPostBack="True" Text="Show Team Members Only"
                    CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
            <td class="style1">
                <asp:CheckBox ID="chkLatestMeetings" runat="server" AutoPostBack="True" Text="Show Last 15 Meetings Only"
                    CssClass="Checkbox_Default" Checked="True"></asp:CheckBox>
            </td>
            <td>
                <asp:HyperLink ID="lnkPrintPage" runat="server" NavigateUrl="~/UI/Pages/DataCollectionPrograms/TeamMeetingAttendance3.aspx"
                    Target="_blank" Text="Printer Friendly Version" CssClass="Link_Default"></asp:HyperLink>
            </td>
        </tr>
    </table>
    <br />
    <table id="Table3" style="width: 100%">
        <tr>
            <td valign="top">
                <asp:Label ID="lblTeamActionPlan" runat="server" Text="Team Action Plan:" CssClass="Label_Left_8PT"></asp:Label>
                <asp:GridView runat="server" ID="gvTeamActionPlan" AutoGenerateColumns="False" BorderStyle="None"
                    CellPadding="3" bordecolor="#999999" BackColor="White" BorderWidth="1px" GridLines="Vertical"
                    DataKeyNames="Cancelled,ActionItemDefinition">
                    <SelectedRowStyle Font-Bold="True" ForeColor="White" BackColor="#008A8C" />
                    <AlternatingRowStyle BackColor="#E7E7E7" />
                    <RowStyle ForeColor="Black" BackColor="#f5f5f5" />
                    <HeaderStyle Font-Bold="True" ForeColor="White" BackColor="#41519A"></HeaderStyle>
                    <Columns>
                        <asp:BoundField DataField="ActionNumber" HeaderText="No.">
                            <ItemStyle />
                        </asp:BoundField>
                        <asp:BoundField DataField="Stepno" HeaderText="Step"></asp:BoundField>
                        <asp:BoundField DataField="UserName" HeaderText="Who">
                            <ItemStyle Wrap="False"></ItemStyle>
                        </asp:BoundField>
                        <asp:BoundField DataField="AssignedToOther" HeaderText="Others"></asp:BoundField>
                        <asp:BoundField DataField="ActionItem" HeaderText="Action Item">
                            <ItemStyle Wrap="False"></ItemStyle>
                        </asp:BoundField>
                        <asp:BoundField DataField="TargetDate" HeaderText="By When" DataFormatString="{0:yyyy/MM/dd}">
                            <ItemStyle Wrap="False"></ItemStyle>
                        </asp:BoundField>
                        <asp:BoundField DataField="ClosedDate" HeaderText="Closed" DataFormatString="{0:yyyy/MM/dd}">
                            <ItemStyle Wrap="False"></ItemStyle>
                        </asp:BoundField>
                        <asp:BoundField DataField="Cancelled" HeaderText="Cancelled" Visible="false" />
                        <asp:BoundField DataField="ActionItemDefinition" HeaderText="ActionItemDefinition" Visible="false" />
                    </Columns>
                </asp:GridView>
                <table>
                    <tr>
                        <td style="width: 209px">
                            <asp:CheckBox ID="chkDisplayClosedTeamActions" runat="server" Width="176px" AutoPostBack="True"
                                Text="Include Closed Team Actions" Checked="True"></asp:CheckBox>
                        </td>
                        <td>
                            <asp:HyperLink ID="lnkPrintPage1" runat="server" NavigateUrl="~/UI/Pages/DataCollectionPrograms/TeamActionPlan3.aspx"
                                Target="_blank" Text="Printer Friendly Version"></asp:HyperLink>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table5" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td style="width: 110px">
                    <asp:Button ID="btnTeamInquiry" runat="server" CssClass="Button_Variable" Text="Team Inquiry"
                        CausesValidation="False"></asp:Button>
                </td>
                <td style="width: 120px">
                    <asp:Button ID="btnTeamMeeting" runat="server" CssClass="Button_Variable" Text="Team Meetings"
                        CausesValidation="False"></asp:Button>
                </td>
                <td style="width: 130px">
                    <asp:Button ID="btnTeamActionPlan" runat="server" CssClass="Button_Variable" Text="Team Action Plan"
                        CausesValidation="False"></asp:Button>
                </td>
                <td style="width: 140px">
                    <asp:Button ID="btnTeamMasterPlan" runat="server" CssClass="Button_Variable" Text="Team Master Plan"
                        CausesValidation="False"></asp:Button>
                </td>
                <td style="width: 110px">
                    <asp:Button ID="btnTeamLog" runat="server" CssClass="Button_Default" Text="Team Log"
                        CausesValidation="False"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnTeamBoard" runat="server" CssClass="Button_Default" Text="Team Board"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
