<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerVariables2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerVariables2"
    Title="Tracker Variables Maintenance" ValidateRequest="false" %>

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
            <td style="width: 120px">
                <asp:Label ID="lblVariableID" runat="server" Text="Tracker Variable ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTrackerVariableID" runat="server" CssClass="Textbox_Display"
                    MaxLength="3" Width="31px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblTrackerVariable" runat="server" Text="Tracker Variable:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTrackerVariable" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="180px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTrackerVariable" runat="server" ErrorMessage="Enter Tracker Variable"
                    ControlToValidate="txtTrackerVariable" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblValue" runat="server" Text="Variable Value:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtVariableValue" runat="server" CssClass="Textbox_Entry" MaxLength="13"
                    Width="180px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqVariableValue" runat="server" ErrorMessage="Enter Variable Value"
                    ControlToValidate="txtVariableValue" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" Width="258px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSite" runat="server" ErrorMessage="Select Site"
                    ControlToValidate="ddlSite" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblInterface" runat="server" Text="Interface:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckInterface" runat="server"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px" valign="top">
                <asp:Label ID="lblFormula" runat="server" Text="Formula:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:TextBox ID="txtExpandFormula" runat="server" CssClass="Textbox_Entry" Width="400px"
                    MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
                &nbsp;<img alt="Show Data Elements Listing..." id="imgElements" style="cursor: hand;"
                    src="~/images/MoreInformation.jpg" name="imgElements" border="0" runat="server" />
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblScheduleCode" runat="server">Schedule Code:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtScheduleCode" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="174px"></asp:TextBox>
                &nbsp;(ex. 1,2,3,5,10)
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblScheduleTime" runat="server">Schedule Time:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtScheduleTime" runat="server" CssClass="Textbox_Entry" Width="43px"
                    MaxLength="4"></asp:TextBox>
                &nbsp;<asp:Label ID="Label16" runat="server"> (HHMM ie: 5:00 PM GMT = 1700)</asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblNextExecution" runat="server">Next Execution:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtNextExecution" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="178px"></asp:TextBox>
                &nbsp;(GMT)
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblLastExecution" runat="server">Last Execution:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLastExecution" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="178px"></asp:TextBox>
                &nbsp;(GMT)
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblLastExecutionSuccessful" runat="server">Last Execution Successful:</asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckLastSuccessful" runat="server" Enabled="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 155px">
                <asp:Label ID="lblOnDemandExecute" runat="server">On Demand Execute:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOnDemandExecute" runat="server" CssClass="Textbox_Entry" Width="173px"></asp:TextBox>
                &nbsp;<asp:Label ID="Label22" runat="server"> (yyyy/mm/dd HH:MM ie: 5:00 PM GMT= 17:00)</asp:Label>
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
                        FormName="Tracker Maintenance" ProgramName="TrackerCollection1" CommandText="spSelTrackerCollectionsByVariable"
                        ProgramMode="TrackerCollectionMode" AlternatingRows="True" FunctionButtonOneLabel="Edit Collection"
                        PrimaryControl="False" ShowExit="False" ShowExport="False" ShowView="False" Translate="True">
                        <GridColumns>
                            <CC1:MasterControlField DataField="Tracker" HeaderText="Savings Tracker" />
                            <CC1:MasterControlField DataField="TrackerType" HeaderText="Savings Type" />
                            <CC1:MasterControlField DataField="Formula" HeaderText="Formula" />
                        </GridColumns>
                    </CC1:MasterControl>
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
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
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
