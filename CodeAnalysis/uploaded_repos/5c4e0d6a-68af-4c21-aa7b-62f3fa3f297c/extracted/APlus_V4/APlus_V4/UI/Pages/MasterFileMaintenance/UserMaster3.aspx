<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserMaster3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserMaster3"
    Title="User Information" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Namespace="WebApp.APlus.UI.CustomControls" TagPrefix="CC1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script language="javascript" type="text/javascript">
        defaultStatus = "User Profile"

        function NewPassword() {
            var msg = "\nThis will create a new Password.\n" + "\n\n";
            if (confirm(msg)) { document.Form1.btnF7.click(); return true; } else return false;
        } 	
    </script>
    <table cellspacing="2" cellpadding="2" border="0" class="Table_Default" id="Table1">
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblUserName" runat="server" CssClass="Label_Left_8PT" Text="User Name:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUserID" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="195px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblName" runat="server" CssClass="Label_Left_8PT" Text="Name:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUserName" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="195px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblDepartment" runat="server" EnableViewState="False" CssClass="Label_Left_8PT"
                    Text="Department:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDepartment" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="195px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblUserTitle" runat="server" EnableViewState="False" CssClass="Label_Left_8PT"
                    Text="Title:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTitle" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="195px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblInitialProgram" runat="server" CssClass="Label_Left_8PT" Text="Initial Program:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtInitialProgram" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="195px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblSite" runat="server" CssClass="Label_Left_8PT" Text="Site:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="195px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblCulture" runat="server" CssClass="Label_Left_8PT" Text="Culture:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUserCulture" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="195px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblWorkingSite" runat="server" CssClass="Label_Left_8PT" Text="Working Site:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtWorkingSite" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="195px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblShowMenuOptionNumbers" runat="server" CssClass="Label_Left_8PT"
                    Text="Show Menu Option Numbers:"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="chkShowMenuOptionNumbers" runat="server" Enabled="False" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblShowAllMenuOptions" runat="server" CssClass="Label_Left_8PT" Text="Show All Menu Options"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="chkShowAllMenuOptions" runat="server" CssClass="Checkbox_Default"
                    Enabled="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblAllTeamView" runat="server" CssClass="Label_Left_8PT" Text="All Team View:"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllTeamView" runat="server" CssClass="Checkbox_Default" Enabled="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblAllTeamEdit" runat="server" CssClass="Label_Left_8PT" Text="All Team Edit:"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllTeamEdit" runat="server" CssClass="Checkbox_Default" Enabled="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblAllKPIView" runat="server" CssClass="Label_Left_8PT" Text="All KPI View:"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllKPIView" runat="server" CssClass="Checkbox_Default" Enabled="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblAllKPIEdit" runat="server" CssClass="Label_Left_8PT" Text="All KPI Edit:"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllKPIEdit" runat="server" CssClass="Checkbox_Default" Enabled="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblNewCulture" runat="server" EnableViewState="False" Visible="False"
                    CssClass="Label_Left_8PT" Text="New Culture:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlCulture" runat="server" CssClass="DropdownList_Entry" Width="232px"
                    Visible="False">
                </asp:DropDownList>
                <asp:RequiredFieldValidator ID="reqCulture" runat="server" ControlToValidate="ddlCulture"
                    CssClass="Label_Left_8PT" Display="None" Enabled="False" ErrorMessage="Select Culture"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblNewWorkingSite" runat="server" EnableViewState="False" Visible="False"
                    CssClass="Label_Left_8PT" Text="New Working Site:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlWorkingSite" runat="server" CssClass="DropdownList_Entry"
                    Width="232px" Visible="False">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblNewDepartment" runat="server" EnableViewState="False" Visible="False"
                    CssClass="Label_Left_8PT" Text="New Department:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtNewDepartmentNumber" runat="server" Width="60px" MaxLength="5"
                    CssClass="Textbox_Entry" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 164px">
                <asp:Label ID="lblNewTitle" runat="server" EnableViewState="False" Visible="False"
                    CssClass="Label_Left_8PT" Text="New Title:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtNewTitle" runat="server" Width="320px" MaxLength="50" CssClass="Textbox_Entry"
                    Wrap="False" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTitle" runat="server" ControlToValidate="txtTitle"
                    CssClass="Label_Left_8PT" Display="None" ErrorMessage="Enter Title"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <br />
    <table id="Table3" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnChangeCulture" runat="server" CssClass="Button_Variable" Text="Change Culture"
                    EnableViewState="False"></asp:Button>
            </td>
            <td style="width: 140px">
                <asp:Button ID="btnChangeMenuOption" runat="server" EnableViewState="False" CssClass="Button_Variable"
                    Text="Change Menu Style"></asp:Button>
            </td>
            <td style="width: 120px">
                <asp:Button ID="btnChangeDepartment" runat="server" Text="Change Department" CssClass="Button_Variable"
                    EnableViewState="False"></asp:Button>
            </td>
            <td style="width: 110px">
                <asp:Button ID="btnChangeTitle" runat="server" Text="Change Title" CssClass="Button_Default"
                    EnableViewState="False"></asp:Button>
            </td>
            <td style="width: 160px">
                <asp:Button ID="btnChangeWorkingSite" runat="server" CssClass="Button_Variable" Text="Change Working Site"
                    EnableViewState="False"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnChangePassword" runat="server" Text="Change Password" CssClass="Button_Variable"
                    EnableViewState="False"></asp:Button>
            </td>
        </tr>
        <tr>
            <td colspan="6">
                &nbsp;
            </td>
        </tr>
        <tr>
            <td colspan="6">
                <asp:Button ID="btnExit" runat="server" Text="Exit" CssClass="Button_Default"></asp:Button>
            </td>
        </tr>
    </table>
    <table id="tblNewPwd" class="Table_Default">
        <tr>
            <td style="width: 113px; height: 8px">
                <asp:Label ID="lblNewPwd" runat="server" EnableViewState="False" Visible="False"
                    CssClass="Label_Left_8PT" Text="New Password:"></asp:Label>
            </td>
            <td style="height: 8px">
                <asp:TextBox ID="txtNewPwd" runat="server" CssClass="Textbox_Entry" EnableViewState="False"
                    Visible="False" TextMode="Password" MaxLength="10" Font-Size="8pt"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqNewPwd" runat="server" ErrorMessage="Enter a new password"
                    ControlToValidate="txtNewPwd" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 113px">
                <asp:Label ID="lblConfPwd" runat="server" EnableViewState="False" Visible="False"
                    CssClass="Label_Left_8PT" Text="Confirm Password:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtConfNewPwd" AccessKey="1" runat="server" CssClass="Textbox_Entry"
                    EnableViewState="False" Visible="False" TextMode="Password" MaxLength="10" Font-Size="8pt"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqConfNewPwd" runat="server" ErrorMessage="Confirm the password"
                    ControlToValidate="txtConfNewPwd" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 113px">
            </td>
            <td>
                <asp:CompareValidator ID="comPwd" runat="server" ErrorMessage="The passwords are different"
                    ControlToValidate="txtConfNewPwd" Display="None" ControlToCompare="txtNewPwd"
                    CssClass="Label_Left_8PT"></asp:CompareValidator>
            </td>
        </tr>
    </table>
    <table id="Table4" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnOK" runat="server" Text="OK" CssClass="Button_Default" EnableViewState="False"
                    Visible="False" CausesValidation="True"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnCancel" runat="server" Text="Cancel" CssClass="Button_Default"
                    EnableViewState="False" Visible="False" CausesValidation="False"></asp:Button>
            </td>
        </tr>
    </table>
    <asp:Panel runat="server" ID="pnlGrids" Width="100%">
        <table style="width: 100%">
            <tr>
                <td>
                    <asp:Label ID="lblSecurityGroups" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Security Groups</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <CC1:MasterControl ID="mcSecurityGroups" runat="server" AlternatingRows="True" CommandText="spSelUserSecurityGroups"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="SecurityGroups"
                        RedirectProgramName="SecurityGroups" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                        ShowExit="False" ShowExport="False" ShowView="False" Translate="True" Width="100%">
                        <GridColumns>
                            <CC1:MasterControlField DataField="SecurityGroup" HeaderText="Security Group" ShowReturns="False">
                            </CC1:MasterControlField>
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <asp:Label ID="lblUserSites" runat="server" CssClass="HeaderTitleText" Font-Bold="True">User Site Master</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <CC1:MasterControl ID="mcUserSite" runat="server" AlternatingRows="True" CommandText="spSelUserSiteMaster"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="UserSiteMaster"
                        RedirectProgramName="UserSiteMaster" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                        ShowExit="False" ShowExport="False" ShowView="False" Translate="True" Width="100%">
                        <GridColumns>
                            <CC1:MasterControlField DataField="Site" HeaderText="Site" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowTeamView" HeaderText="Team View" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowTeamEdit" HeaderText="Team Edit" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowKPIView" HeaderText="KPI View" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowKPIEdit" HeaderText="KPI Edit" ShowReturns="False">
                            </CC1:MasterControlField>
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <asp:Label ID="lblAreaUsers" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Area User Master</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <CC1:MasterControl ID="mcAreaGroupUsers" runat="server" AlternatingRows="True" CommandText="spSelAreaGroupUserMasterByUserID"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="UserSiteMaster"
                        RedirectProgramName="UserSiteMaster" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                        ShowExit="False" ShowExport="False" ShowView="False" Translate="True" Width="100%">
                        <GridColumns>
                            <CC1:MasterControlField DataField="AreaGroup" HeaderText="Area Group" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowAnomalyEvaluate" HeaderText="Evaluate Anomaly" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowAnomalyEdit" HeaderText="Edit Anomaly" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowKPIView" HeaderText="KPI View" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowKPIEdit" HeaderText="KPI Edit" ShowReturns="False">
                            </CC1:MasterControlField>
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <asp:Label ID="lblKPINotifications" runat="server" CssClass="HeaderTitleText" Font-Bold="True">KPI Notifications</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <CC1:MasterControl ID="mcKPINotifications" runat="server" AlternatingRows="True"
                        CommandText="spSelKPIUserNotifications" DeleteLabel="" EditLabel="" PrimaryControl="False"
                        ProgramName="KPIUserNotifications1" RedirectProgramName="KPIUserNotifications1"
                        ShowAdd="False" ShowDelete="False" ShowEdit="False" ShowExit="False" ShowExport="False"
                        ShowView="False" Translate="True" Width="100%">
                        <GridColumns>
                            <CC1:MasterControlField DataField="KPI" HeaderText="KPI" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="KPIValueEntry" HeaderText="Value Entry" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="KPIValueEntryReminder" HeaderText="Reminder" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="KPITargetEntry" HeaderText="Target Entry" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="KPITargetEntryReminder" HeaderText="Reminder"
                                ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="KPIDeviation" HeaderText="Deviation" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AnomalyPending" HeaderText="Pending Anomalies"
                                ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AnomalyPendingReminder" HeaderText="Reminder"
                                ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AnomalyActions" HeaderText="Anomaly Actions" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AnomalyActionsReminder" HeaderText="Reminder"
                                ShowReturns="False">
                            </CC1:MasterControlField>
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:ValidationSummary ID="Validationsummary1" runat="server" CssClass="Label_Left_8PT"
        DisplayMode="List" ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
