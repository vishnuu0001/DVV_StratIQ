<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerMaster2"
    Title="Savings Tracker Maintenance" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 150px;
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
    <table class="Table_Default" id="Table1">
        <tr>
            <td class="style1">
                <asp:Label ID="lblSavingsTracker" runat="server" Text="Savings Tracker:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTracker" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="325px" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTracker" runat="server" ErrorMessage="Enter Tracker"
                    ControlToValidate="txtTracker" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblTrackerOther" runat="server" Text="Savings Tracker (English):"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTrackerOther" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="325px" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTrackerOther" runat="server" ErrorMessage="Enter Tracker English"
                    ControlToValidate="txtTrackerOther" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblTeam" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlTeam" runat="server" Width="325px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtTeam" runat="server" Width="325px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTeam" runat="server" ErrorMessage="Select Team"
                    ControlToValidate="ddlTeam" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblSavingsCategory" runat="server" Text="Savings Category:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSavingsCategory" runat="server" Width="175px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSavingsCategory" runat="server" Width="175px" MaxLength="15"
                    CssClass="Textbox_Display" Visible="False" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSavingsCategory" runat="server" ErrorMessage="Select Savings Category"
                    ControlToValidate="ddlSavingsCategory" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblUOM" runat="server" Text="UOM:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUOM" runat="server" Width="97" MaxLength="15" CssClass="Textbox_Entry"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUOM" runat="server" Display="None" ControlToValidate="txtUOM"
                    ErrorMessage="Enter UOM"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblHistoric" runat="server" Text="Historic:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtHistoric" runat="server" Width="97" MaxLength="15" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqHistoric" runat="server" Display="None" ControlToValidate="txtHistoric"
                    ErrorMessage="Enter Historic"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblTarget" runat="server" Text="Target:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTarget" runat="server" Width="97px" MaxLength="15" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqTarget" runat="server" Display="None" ControlToValidate="txtTarget" ErrorMessage="Enter Target"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblStartPeriod" runat="server" Text="Start Period:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtStartDate" runat="server" Width="81" CssClass="Textbox_Entry"></asp:TextBox>
                <CC1:CalendarExtender ID="txtStartDate_CalendarExtender" runat="server" PopupButtonID="imgStartDate"
                    TargetControlID="txtStartDate" CssClass="APlus_Calendar">
                </CC1:CalendarExtender>
                <asp:ImageButton ID="imgStartDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqStartDate" runat="server" Display="None" ControlToValidate="txtStartDate"
                    ErrorMessage="Enter Start Date"></asp:RequiredFieldValidator><asp:CompareValidator
                        ID="cmpStartDate" runat="server" Display="None" ControlToValidate="txtStartDate"
                        ErrorMessage="Invalid Start Date" Type="Date" Operator="DataTypeCheck"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblDescription" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandDescription" runat="server" CssClass="Textbox_Entry" Width="400px"
                    MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
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
                    MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>&nbsp;<img
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
                    Width="174px"></asp:TextBox>
                &nbsp;(ex. 1,2,3,5,10)
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
                    ReadOnly="True" Width="178px"></asp:TextBox>
                &nbsp;(GMT)
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblLastExecution" runat="server">Last Execution:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLastExecution" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="178px"></asp:TextBox>
                &nbsp;(GMT)
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
                <asp:Label ID="lblActive" runat="server" Text="Active:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="cbActive" runat="server"></asp:CheckBox>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel runat="server" ID="pnlMasterControls">
        <table style="width: 100%">
            <tr>
                <td>
                    <asp:Label ID="lblSavingsTypesHeader" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Savings Types</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <CC1:MasterControl ID="mcCollection" runat="server" ShowAdd="False" ShowDelete="False"
                        ShowEdit="False" NewLinkCaption="Tracker Collection" RedirectProgramName="TrackerCollection2"
                        FormName="Tracker Maintenance" ProgramName="TrackerCollection1" CommandText="spSelTrackerCollections"
                        ProgramMode="TrackerCollectionMode" AlternatingRows="True" FunctionButtonOneLabel="Edit Collection"
                        PrimaryControl="False" ShowExit="False" ShowExport="False" ShowView="False" Translate="True">
                        <gridcolumns>
                            <CC1:MasterControlField DataField="Tracker" HeaderText="Savings Tracker" />
                            <CC1:MasterControlField DataField="TrackerType" HeaderText="Savings Type" />
                            <CC1:MasterControlField DataField="SavingsType" HeaderText="Savings" />
                            <CC1:MasterControlField DataField="Formula" HeaderText="Formula" />
                        </gridcolumns>
                    </CC1:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <asp:Label ID="lblTrackerVariables" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Variables associated with Tracker</asp:Label>
                </td>
            </tr>
            <tr>
                <td>
                    <CC1:MasterControl ID="mcVariables" runat="server" ShowAdd="False" ShowDelete="False"
                        ShowEdit="False" NewLinkCaption="Tracker Variable" RedirectProgramName="TrackerVariables2"
                        FormName="Tracker Variable Maintenance" ProgramName="TrackerVariables1" CommandText="spSelTrackerVariablesByTrackerID"
                        ProgramMode="TrackerVariableMode" AlternatingRows="True" PrimaryControl="False"
                        ShowExit="False" ShowExport="False" ShowView="False" Translate="True">
                        <gridcolumns>
                            <CC1:MasterControlField DataField="TrackerVariable" HeaderText="Variable" />
                            <CC1:MasterControlField DataField="VariableValue" HeaderText="Value" />
                            <CC1:MasterControlField DataField="Site" HeaderText="Site" />
                        </gridcolumns>
                    </CC1:MasterControl>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left" style="width: 142px">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td align="left" style="width: 142px">
                    <asp:Button ID="btnTrackerTypes" runat="server" CssClass="Button_Default" Text="Savings Types" />
                </td>
                <td align="left" style="width: 142px">
                    <asp:Button ID="btnVariables" runat="server" CssClass="Button_Default" Text="Variables" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3">
            <tr>
                <td style="width: 150px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td style="width: 150px">
                    <asp:Button ID="btnTrackerTypes2" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Savings Types" />
                </td>
                <td>
                    <asp:Button ID="btnVariables2" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Variables" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
