<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyActions2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyActions2"
    Title="Anomaly Actions" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="CC1" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC2" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <CC2:MasterControl ID="mcAnomaly" runat="server" ShowAdd="false" ShowDelete="false"
        Translate="true" ShowView="false" ShowEdit="false" NewLinkCaption="Anomaly" RedirectProgramName="AnomalyMaster2"
        FormName="Anomaly Maintenance" ProgramName="AnomalyMaster1" CommandText="spSelAnomalyMasterByID"
        ProgramMode="AnomalyMode" AlternatingRows="True" PrimaryControl="false">
        <GridColumns>
            <CC2:MasterControlField DataField="AnomalyID" HeaderText="ID" />
            <CC2:MasterControlField DataField="Site" HeaderText="Site" />
            <CC2:MasterControlField DataField="AnomalyType" HeaderText="Type" />
            <CC2:MasterControlField DataField="Anomaly" HeaderText="Anomaly" />
            <CC2:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
            <CC2:MasterControlField DataField="Observations" HeaderText="Observations" />
            <CC2:MasterControlField DataField="ClosedDateTime" HeaderText="Closed" />
            <CC2:MasterControlField DataField="CreatedUser" HeaderText="Created By" />
            <CC2:MasterControlField DataField="CreatedDateTime" HeaderText="Created" />
        </GridColumns>
    </CC2:MasterControl>
    <hr width="100%" />
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAnomalyActionID" runat="server" Text="Anomaly Action ID:" CssClass="Label_Left_8PT"
                    Visible="False"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAnomalyActionID" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="31px" ReadOnly="True" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAnomalyCause" runat="server" Text="Anomaly Cause:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlAnomalyCause" runat="server" Width="325px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtAnomalyCause" runat="server" Width="325px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAnomalyCause" runat="server" ErrorMessage="Select Anomaly Cause"
                    ControlToValidate="ddlAnomalyCause" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActionWhat" runat="server" Text="Action What:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandActionWhat" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="400px" Height="28px" TextMode="MultiLine"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqActionWhat" runat="server" ErrorMessage="Enter Action What"
                    ControlToValidate="txtExpandActionWhat" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActionWhere" runat="server" Text="Action Where:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtActionWhere" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="259px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActionWhy" runat="server" Text="Action Why:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandActionWhy" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="400px" Height="28px" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblTargetDate" runat="server" Text="Target Date (When):" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTargetDate" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="81px"></asp:TextBox>
                <CC1:CalendarExtender ID="txtTargetDate_CalendarExtender" runat="server" Enabled="True"
                    PopupButtonID="imgTargetDate" TargetControlID="txtTargetDate" CssClass="APlus_Calendar">
                </CC1:CalendarExtender>
                <asp:ImageButton ID="imgTargetDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqTargetDate" runat="server" ErrorMessage="Enter Target Date"
                    ControlToValidate="txtTargetDate" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActionHow" runat="server" Text="Action How:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandActionHow" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="400px" Height="28px" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                &nbsp;
            </td>
        </tr>
        <div runat="server" id="pnlSGI" visible="false">
            <tr>
                <td style="width: 120px" valign="middle">
                    <asp:Label ID="lblContention" runat="server" Text="Contention Action:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:CheckBox ID="ckContention" runat="server" />
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    &nbsp;
                </td>
            </tr>
        </div>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblResponsibleUser" runat="server" Text="Responsible User:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlResponsibleUser" runat="server" CssClass="DropdownList_Entry"
                    Width="194px">
                </asp:DropDownList>
                <CC1:ListSearchExtender ID="ddlResponsibleUser_ListSearchExtender" runat="server"
                    Enabled="True" TargetControlID="ddlResponsibleUser">
                </CC1:ListSearchExtender>
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
            <td style="width: 120px" valign="top">
                <asp:Label ID="lblActions" runat="server" Text="Actions:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandActions" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="400px" Height="28px" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px" valign="top">
                <asp:Label ID="lblClosed" runat="server" Text="Closed Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtClosedDate" runat="server" Width="81" CssClass="Textbox_Entry"></asp:TextBox>
                <CC1:CalendarExtender ID="txtClosedDate_CalendarExtender" runat="server" PopupButtonID="imgClosedDate"
                    TargetControlID="txtClosedDate" CssClass="APlus_Calendar">
                </CC1:CalendarExtender>
                <asp:ImageButton ID="imgClosedDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 120px" valign="top">
                &nbsp;
            </td>
            <td>
                <asp:RadioButtonList ID="rblCancelled" runat="server" RepeatDirection="Horizontal"
                    Width="200px">
                    <asp:ListItem Value="0">Completed</asp:ListItem>
                    <asp:ListItem Value="1">Cancelled</asp:ListItem>
                </asp:RadioButtonList>
            </td>
        </tr>
    </table>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
