<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserMaster2"
    Title="User Master" %>

<%@ Register Src="~/UI/UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Namespace="WebApp.APlus.UI.CustomControls" TagPrefix="CC1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:Panel ID="pnlUser" runat="server">
        <table class="Table_Default" id="Table1">
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblUserName" runat="server" CssClass="Label_Left_8PT" Text="User Name:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtUserID" runat="server" Width="255px" MaxLength="50" CssClass="Textbox_Entry"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqUserID" runat="server" Display="None" ControlToValidate="txtUserID"
                        ErrorMessage="Enter a User Name" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblPassword" runat="server" CssClass="Label_Left_8PT" Text="Password:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtPwd" runat="server" Width="151px" MaxLength="10" CssClass="Textbox_Entry"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqPwd" runat="server" Display="None" ControlToValidate="txtPwd"
                        ErrorMessage="Enter a password" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblFirstName" runat="server" CssClass="Label_Left_8PT" Text="First Name:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtFirstName" runat="server" MaxLength="25" CssClass="Textbox_Entry"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqFirstName" runat="server" Display="None" ControlToValidate="txtFirstName"
                        ErrorMessage="Enter a First Name" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblLastName" runat="server" CssClass="Label_Left_8PT" Text="Last Name:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtLastName" runat="server" MaxLength="25" CssClass="Textbox_Entry"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqLastName" runat="server" Display="None" ControlToValidate="txtLastName"
                        ErrorMessage="Enter a Name" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblMiddleInitial" runat="server" CssClass="Label_Left_8PT" Text="Middle Initial:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtMiddleInitial" runat="server" Width="55px" MaxLength="5" CssClass="Textbox_Entry"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblSuffix" runat="server" CssClass="Label_Left_8PT" Text="Suffix:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtSuffix" runat="server" Width="55px" MaxLength="5" CssClass="Textbox_Entry"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblDepartmentNumber" runat="server" CssClass="Label_Left_8PT" Text="Department Number:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtDepartmentNumber" runat="server" Width="60px" MaxLength="5" CssClass="Textbox_Entry"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblInitialProgram" runat="server" CssClass="Label_Left_8PT" Text="Initial Program:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtInitialProgram" runat="server" Width="184px" MaxLength="50" CssClass="Textbox_Display"
                        Visible="False" ReadOnly="True"></asp:TextBox>
                    <asp:DropDownList ID="ddlInitialProgram" runat="server" Width="191px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:RequiredFieldValidator ID="reqProg" runat="server" ControlToValidate="ddlInitialProgram"
                        CssClass="Label_Left_8PT" Display="None" ErrorMessage="Select Intital Program"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblSite" runat="server" CssClass="Label_Left_8PT" Text="Site:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtSite" runat="server" Width="184px" MaxLength="50" CssClass="Textbox_Display"
                        Visible="False" ReadOnly="True"></asp:TextBox>
                    <asp:DropDownList ID="ddlSite" runat="server" Width="191px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblCulture" runat="server" CssClass="Label_Left_8PT" Text="Culture:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtCulture" runat="server" Width="184px" MaxLength="50" CssClass="Textbox_Display"
                        Visible="False" ReadOnly="True"></asp:TextBox>
                    <asp:DropDownList ID="ddlCulture" runat="server" Width="191px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:RequiredFieldValidator ID="reqCulture" runat="server" Display="None" ControlToValidate="ddlCulture"
                        ErrorMessage="Enter Culture" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblTitle" runat="server" CssClass="Label_Left_8PT" Text="Title:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtTitle" runat="server" Width="320px" MaxLength="50" CssClass="Textbox_Entry"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqTitle" runat="server" Display="None" ControlToValidate="txtTitle"
                        ErrorMessage="Enter Title" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 108px">
                    <asp:Label ID="lblEmailAddress" runat="server" CssClass="Label_Left_8PT" Text="Email Address:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtEmailAddress" runat="server" Width="320px" MaxLength="50" CssClass="Textbox_Entry"></asp:TextBox>
                    <asp:RegularExpressionValidator ID="regEmailAddress" runat="server" Display="None"
                        ControlToValidate="txtEmailAddress" ErrorMessage="Email not in correct format"
                        ValidationExpression="\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*" CssClass="Label_Left_8PT"></asp:RegularExpressionValidator>
                </td>
            </tr>
            <tr>
                <td align="left" colspan="2" style="width: 167px">
                    <asp:CheckBox ID="chkAdmin" runat="server" CssClass="Checkbox_Default" Text="Administrator">
                    </asp:CheckBox>
                </td>
            </tr>
            <tr>
                <td align="left" colspan="2" style="width: 167px">
                    <asp:CheckBox ID="chkRegTemp" runat="server" CssClass="Checkbox_Default" Text="Temp"
                        Checked="False"></asp:CheckBox>
                </td>
            </tr>
            <tr>
                <td align="left" colspan="2" style="width: 167px">
                    <asp:CheckBox ID="chkActive" runat="server" CssClass="Checkbox_Default" Text="Active">
                    </asp:CheckBox>
                </td>
            </tr>
            <tr>
                <td align="left" colspan="2" style="width: 167px">
                    <asp:CheckBox ID="ckAllTeamView" runat="server" CssClass="Checkbox_Default" Text="All Team View" />
                </td>
            </tr>
            <tr>
                <td align="left" colspan="2" style="width: 167px">
                    <asp:CheckBox ID="ckAllTeamEdit" runat="server" CssClass="Checkbox_Default" Text="All Team Edit" />
                </td>
            </tr>
            <tr>
                <td align="left" colspan="2" style="width: 167px">
                    <asp:CheckBox ID="ckAllKPIView" runat="server" CssClass="Checkbox_Default" Text="All KPI View" />
                </td>
            </tr>
            <tr>
                <td align="left" colspan="2" style="width: 167px">
                    <asp:CheckBox ID="ckAllKPIEdit" runat="server" CssClass="Checkbox_Default" Text="All KPI Edit" />
                </td>
            </tr>
        </table>
        <br />
        <asp:Panel runat="server" ID="pnlGrids" Width="100%">
            <table style="width: 100%">
                <tr>
                    <td>
                        <asp:Label ID="lblGradeBOMHeader" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Security Groups</asp:Label>
                    </td>
                </tr>
                <tr>
                    <td>
                        <CC1:MasterControl ID="dgSecurityGroups" runat="server" AlternatingRows="True" CommandText="spSelUserSecurityGroups"
                            DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="SecurityGroups"
                            RedirectProgramName="SecurityGroups" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                            ShowExit="False" ShowExport="False" ShowView="False" Translate="False" Width="100%">
                            <GridColumns>
                                <CC1:MasterControlField DataField="SecurityGroup" HeaderText="Security Group" ShowReturns="False">
                                </CC1:MasterControlField>
                            </GridColumns>
                        </CC1:MasterControl>
                    </td>
                </tr>
                <tr>
                    <td>
                        <asp:Label ID="Label1" runat="server" CssClass="HeaderTitleText" Font-Bold="True">User Site Master</asp:Label>
                    </td>
                </tr>
                <tr>
                    <td>
                        <CC1:MasterControl ID="mcUserSite" runat="server" AlternatingRows="True" CommandText="spSelUserSiteMaster"
                            DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="UserSiteMaster"
                            RedirectProgramName="UserSiteMaster" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                            ShowExit="False" ShowExport="False" ShowView="False" Translate="False" Width="100%">
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
                        <asp:Label ID="Label2" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Area User Master</asp:Label>
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
                            ShowView="False" Translate="false" Width="100%">
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
        <br />
    </asp:Panel>
    <asp:Panel ID="pnlChangePassword" runat="server" Visible="False">
        <table id="tblNewPwd" class="Table_Default">
            <tr>
                <td style="width: 113px">
                    <asp:Label ID="lblNewPwd" runat="server" EnableViewState="False" CssClass="Label_Left_8PT"
                        Text="New Password:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtNewPwd" runat="server" MaxLength="15" CssClass="Textbox_Entry"
                        Visible="True" EnableViewState="False" TextMode="Password"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqNewPwd" runat="server" Display="None" ControlToValidate="txtNewPwd"
                        ErrorMessage="Enter a new password" Visible="False" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
            <tr>
                <td style="width: 113px">
                    <asp:Label ID="lblConfPwd" runat="server" EnableViewState="False" CssClass="Label_Left_8PT"
                        Text="Confirm Password:"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtConfNewPwd" AccessKey="1" runat="server" MaxLength="15" CssClass="Textbox_Entry"
                        Visible="True" EnableViewState="False" TextMode="Password"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqConfNewPwd" runat="server" Display="None" ControlToValidate="txtConfNewPwd"
                        ErrorMessage="Confirm the password" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                    <asp:CompareValidator ID="comPwd" runat="server" ControlToCompare="txtNewPwd" ControlToValidate="txtConfNewPwd"
                        CssClass="Label_Left_8PT" Display="None" ErrorMessage="The passwords are different"></asp:CompareValidator>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td style="width: 110px">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td style="width: 182px">
                    <asp:Button ID="btnF7" runat="server" CssClass="Button_Variable" Visible="False"
                        Text="F7-Change Password" EnableViewState="False"></asp:Button>
                </td>
                <td style="width: 150px">
                    <asp:Button ID="btnSecurityGroups" runat="server" CssClass="Button_Variable" Visible="False"
                        Text="Security Groups" EnableViewState="False"></asp:Button>
                </td>
                <td class="style1">
                    <asp:Button ID="btnUserSiteMaster" runat="server" CssClass="Button_Variable" EnableViewState="False"
                        Text="User Site Master" Visible="False" />
                </td>
                <td class="style1">
                    <asp:Button ID="btnAreaUser" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="Area User" Visible="False" />
                </td>
                <td>
                    <asp:Button ID="btnKPIUserNotification" runat="server" CssClass="Button_Variable"
                        EnableViewState="False" Text="KPI Notifications" Visible="False" />
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
    <asp:ValidationSummary ID="Validationsummary1" runat="server" CssClass="Label_Left_8PT"
        DisplayMode="List" ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 150px;
        }
    </style>
</asp:Content>
