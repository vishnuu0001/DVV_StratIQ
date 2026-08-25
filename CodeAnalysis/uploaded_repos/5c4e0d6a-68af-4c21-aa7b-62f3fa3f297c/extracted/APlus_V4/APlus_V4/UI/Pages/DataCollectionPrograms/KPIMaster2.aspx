<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIMaster2"
    Title="KPI Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1">
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPI" runat="server" Text="KPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtKPI" runat="server" CssClass="Textbox_Entry" MaxLength="50" Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqKPI" runat="server" ErrorMessage="Enter KPI" ControlToValidate="txtKPI"
                    Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPIEnglish" runat="server" Text="KPI (English):" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtKPIOther" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqKPIOther" runat="server" ErrorMessage="Enter KPI (English)"
                    ControlToValidate="txtKPIOther" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1" valign="top">
                <asp:Label ID="lblDescription" runat="server" Text="Description (English):" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandDescription" runat="server" CssClass="Textbox_Entry" Width="400px"
                    MaxLength="500" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblUOM" runat="server" Text="UOM:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUOM" runat="server" CssClass="Textbox_Entry" MaxLength="15" Width="101px"
                    Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUOM" runat="server" ErrorMessage="Enter UOM" ControlToValidate="txtUOM"
                    Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblTargetUp" runat="server" Text="Target Up:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckTargetUp" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSite" runat="server" ErrorMessage="Select Site"
                    ControlToValidate="ddlSite" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblCategory" runat="server" Text="Category:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlCategory" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtCategory" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqCategory" runat="server" ErrorMessage="Select Category"
                    ControlToValidate="ddlCategory" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblSortSequence" runat="server" Text="Sort Sequence:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSortSequence" runat="server" CssClass="Textbox_Entry" MaxLength="3"
                    Width="37px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSortSequence" runat="server" ErrorMessage="Enter Sort Sequence"
                    ControlToValidate="txtSortSequence" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblPillar" runat="server" Text="Pillar:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlPillar" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtPillar" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqPillar" runat="server" ErrorMessage="Select Pillar"
                    ControlToValidate="ddlPillar" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblBusinessArea" runat="server" Text="Business Area:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessArea" runat="server" CssClass="DropdownList_Entry"
                    Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtBusinessArea" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblBusinessUnit" runat="server" Text="Business Unit:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlBusinessUnit" runat="server" CssClass="DropdownList_Entry"
                    Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtBusinessUnit" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblReportingLevel" runat="server" Text="Reporting Level:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlReportingLevel" runat="server" CssClass="DropdownList_Entry"
                    Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtReportingLevel" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqReportingLevel" runat="server" ErrorMessage="Select Reporting Level"
                    ControlToValidate="ddlReportingLevel" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblSummaryType" runat="server" Text="Summary Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSummaryType" runat="server" CssClass="Textbox_Entry_UpperCase"
                    MaxLength="1" Width="38px" Height="16px"></asp:TextBox>
                &nbsp;<asp:Label ID="label13" runat="server" Text="(S = Sum; A = Average; N = Not Applicable)"
                    CssClass="Label_Left_8PT"></asp:Label><asp:RequiredFieldValidator ID="reqSummaryType"
                        runat="server" ErrorMessage="Enter Summary Type" ControlToValidate="txtSummaryType"
                        Display="None"></asp:RequiredFieldValidator><asp:RegularExpressionValidator ID="reqValidSummaryType"
                            runat="server" ControlToValidate="txtSummaryType" Display="None" ErrorMessage="Invalid Summary Type (S, A or N)"
                            ValidationExpression="[aAsSnN]"></asp:RegularExpressionValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblResponsibleUser" runat="server" Text="Responsible User:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlResponsibleUser" runat="server" CssClass="DropdownList_Entry"
                    Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtResponsibleUser" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqResponsibleUser" runat="server" ErrorMessage="Select Responsible User"
                    ControlToValidate="ddlResponsibleUser" Display="None"></asp:RequiredFieldValidator>
                &nbsp;<asp:DropDownList ID="ddlUserSite" runat="server" CssClass="DropdownList_Entry"
                    Width="194px" AutoPostBack="True">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblArea" runat="server" Text="Area:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlArea" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtArea" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqArea" runat="server" ErrorMessage="Select Area"
                    ControlToValidate="ddlArea" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblInterface" runat="server" Text="Interface:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckInterface" runat="server"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td valign="top" class="style1">
                <asp:Label ID="lblFormula" runat="server" Text="Formula:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:TextBox ID="txtExpandFormula" runat="server" CssClass="Textbox_Entry" Width="400px"
                    MaxLength="500" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>&nbsp;<img
                        alt="Show Data Elements Listing..." id="imgElements" style="cursor: hand;" src="~/images/MoreInformation.jpg"
                        name="imgElements" border="0" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblScheduleCode" runat="server">Schedule Code:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtScheduleCode" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="174px"></asp:TextBox>&nbsp;(ex. 1,2,3,5,10)
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblScheduleTime" runat="server">Schedule Time:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtScheduleTime" runat="server" CssClass="Textbox_Entry" Width="43px"
                    MaxLength="4"></asp:TextBox>
                &nbsp;<asp:Label ID="Label16" runat="server"> (HHMM ie: 5:00 PM GMT = 1700)</asp:Label>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblNextExecution" runat="server">Next Execution:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtNextExecution" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="178px"></asp:TextBox>&nbsp;(GMT)
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblLastExecution" runat="server">Last Execution:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLastExecution" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="178px"></asp:TextBox>&nbsp;(GMT)
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblLastExecutionSuccessful" runat="server">Last Execution Successful:</asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckLastSuccessful" runat="server" Enabled="False" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblOnDemandExecute" runat="server">On Demand Execute:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOnDemandExecute" runat="server" CssClass="Textbox_Entry" Width="173px"></asp:TextBox>
                &nbsp;<asp:Label ID="Label22" runat="server"> (yyyy/mm/dd HH:MM ie: 5:00 PM GMT = 17:00)</asp:Label>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblNoNotification" runat="server" Text="Supress Email Notifications:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckNoNotifications" runat="server"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblActive" runat="server" Text="Active:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckActive" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblPrimaryKPI" runat="server" Text="Primary KPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlPrimaryKPI" runat="server" CssClass="DropdownList_Entry"
                    Width="260px">
                </asp:DropDownList>
                <asp:TextBox ID="txtPrimaryKPI" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="250px" Visible="False" Height="16px"></asp:TextBox>
                &nbsp;<asp:DropDownList ID="ddlPrimaryKPISite" runat="server" CssClass="DropdownList_Entry"
                    Width="194px" AutoPostBack="True">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblAutoMonth" runat="server" Text="Automatic Monthly Anomaly:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAutoMonth" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblAutoYTD" runat="server" Text="Automatic YTD Anomaly:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAutoYTD" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblAnomalyResponsibleUser" runat="server" Text="Anomaly Responsible User:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlAnomalyResponsibleUser" runat="server" CssClass="DropdownList_Entry"
                    Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtAnomalyResponsibleUser" runat="server" CssClass="Textbox_Display"
                    ReadOnly="True" Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAnomalyResponsibleUser" runat="server" ErrorMessage="Select Anomaly Responsible User"
                    ControlToValidate="ddlAnomalyResponsibleUser" Display="None"></asp:RequiredFieldValidator>
                &nbsp;<asp:DropDownList ID="ddlAnomalyUserSite" runat="server" CssClass="DropdownList_Entry"
                    Width="194px" AutoPostBack="True">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblDailyKPI" runat="server" Text="Daily KPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckDailyKPI" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblDailyInterface" runat="server" Text="Daily Interface:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckDailyInterface" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblDailyCompare" runat="server" Text="Compare Daily Values:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckDailyCompare" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblElement" runat="server" Text="Data Element:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtElement" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="100px"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel runat="server" ID="pnlGrids" Width="100%">
        <table style="width: 100%">
            <tr>
                <td>
                    <asp:Label ID="lblKPITeamsHeader" runat="server" CssClass="HeaderTitleText" Font-Bold="True">KPI Teams</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <CC1:MasterControl ID="mcKPITeams" runat="server" AlternatingRows="True" CommandText="spSelKPITeamMasterByKPI"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="KPITeams" RedirectProgramName="KPITeams"
                        ShowAdd="False" ShowDelete="False" ShowEdit="False" ShowExit="False" ShowExport="False"
                        ShowView="False" Translate="True" Width="100%">
                        <GridColumns>
                            <CC1:MasterControlField DataField="Team" HeaderText="Team" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowKPIView" HeaderText="View" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="AllowKPIEdit" HeaderText="Edit" ShowReturns="False">
                            </CC1:MasterControlField>
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <asp:Label ID="lblKPINotification" runat="server" CssClass="HeaderTitleText" Font-Bold="True">KPI Notifications</asp:Label>
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
                            <CC1:MasterControlField DataField="UserName" HeaderText="User" ShowReturns="False">
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
            <tr>
                <td>
                    <asp:Label ID="lblKPIDataElements" runat="server" CssClass="HeaderTitleText" Font-Bold="True">KPI Data Elements</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <CC1:MasterControl ID="mcKPIDataElements" runat="server" AlternatingRows="True" CommandText="spSelKPIDateElementsByKPIID"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="KPITeams" RedirectProgramName="KPITeams"
                        ShowAdd="False" ShowDelete="False" ShowEdit="False" ShowExit="False" ShowExport="False"
                        ShowView="False" Translate="True" Width="100%">
                        <GridColumns>
                            <CC1:MasterControlField DataField="DataElement" HeaderText="Data Element" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="KPIOther" HeaderText="KPI" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="UOM" HeaderText="UOM" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="InterfaceFormula" HeaderText="Formula" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="Interface" HeaderText="Interface" ShowReturns="False">
                            </CC1:MasterControlField>
                            <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User"
                                ShowReturns="False">
                            </CC1:MasterControlField>
                        </GridColumns>
                    </CC1:MasterControl>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons">
            <tr>
                <td class="style2">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left" class="style2">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td align="left" class="style3">
                    <asp:Button ID="btnTeamKPI" runat="server" CssClass="Button_Variable" Text="KPI Team Master" />
                </td>
                <td align="left">
                    <asp:Button ID="btnKPINotifications" runat="server" CssClass="Button_Variable" Text="KPI Notifications" />
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 170px;
        }
        .style2
        {
            width: 125px;
        }
        .style3
        {
            width: 150px;
        }
    </style>
</asp:Content>
