<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEChecksheetMaster1.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEChecksheetMaster1"
    Title="SLICE Checksheet Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc2" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/WorkcenterSubHeader.ascx" TagName="WorkcenterSubHeader"
    TagPrefix="uc1" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <uc1:WorkcenterSubHeader ID="WorkcenterSubHeader1" runat="server"></uc1:WorkcenterSubHeader>
    <br />
    <table width="100%">
        <tr>
            <td style="width: 140px">
                <asp:Label ID="Label3" runat="server" Text="Include Closed Checksheets:"></asp:Label>
            </td>
            <td style="width: 20px">
                <asp:CheckBox ID="ckIncludeClosed" runat="server"></asp:CheckBox>
            </td>
            <td style="width: 65px; vertical-align: middle; text-align: left;">
                <asp:Label ID="Label1" runat="server" Text="Start Date:"></asp:Label>
            </td>
            <td style="width: 100px; vertical-align: middle; text-align: left;">
                <asp:TextBox ID="txtStartDate" runat="server" CssClass="Textbox_Entry" Width="76px"
                    MaxLength="20"></asp:TextBox><cc2:CalendarExtender ID="txtStartDate_CalendarExtender"
                        runat="server" PopupButtonID="imgStartDate" TargetControlID="txtStartDate" CssClass="APlus_Calendar">
                    </cc2:CalendarExtender>
                <asp:ImageButton ID="imgStartDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
            </td>
            <td style="width: 60px; vertical-align: middle; text-align: left;">
                <asp:Label ID="Label2" runat="server" Text="End Date:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEndDate" runat="server" CssClass="Textbox_Entry" Width="76px"
                    MaxLength="20"></asp:TextBox><cc2:CalendarExtender ID="txtEndDate_CalendarExtender"
                        runat="server" PopupButtonID="imgEndDate" TargetControlID="txtEndDate" CssClass="APlus_Calendar">
                    </cc2:CalendarExtender>
                <asp:ImageButton ID="imgEndDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
            </td>
        </tr>
    </table>
    <br />
    <table width="100%">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnApplyFilter" runat="server" Text="Apply Filter" CssClass="Button_Default">
                </asp:Button>
            </td>
            <td colspan="3">
                <asp:Button ID="btnClearFilter" runat="server" Text="Clear Filter" CssClass="Button_Default">
                </asp:Button>
            </td>
        </tr>
    </table>
    <br />
    <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelSLICECheckSheetMaster"
        FormName="SLICE Checksheet Maintenance" NewLinkCaption="SLICE Checksheet" ProgramMode="SLICEChecksheetMasterMode"
        ProgramName="SLICEChecksheetMaster1" RedirectProgramName="SLICECheckSheetMaster2"
        ShowExport="False" RaiseAddEvent="True" RaiseExitEvent="True" AlternatingRows="true">
        <GridColumns>
            <CC1:MasterControlField DataField="TemplateDesc" SortExpression="TemplateDesc" HeaderText="Checksheet"
                ShowReturns="true" />
            <CC1:MasterControlField DataField="SLICEChecksheetID" SortExpression="SLICEChecksheetID"
                HeaderText="ID" />
            <CC1:MasterControlField DataField="SLICEChecksheetReleaseDate" SortExpression="SLICEChecksheetReleaseDate"
                Visible="True" DataFormatString="{0:d}" HeaderText="Release Date" />
            <CC1:MasterControlField DataField="SLICEChecksheetDueDate" SortExpression="SLICEChecksheetDueDate"
                HeaderText="Due Date" DataFormatString="{0:d}" />
            <CC1:MasterControlField ShowReturns="False" DataField="SLICEChecksheetDesc" SortExpression="SLICEChecksheetDesc"
                HeaderText="Status" />
            <CC1:MasterControlField ShowReturns="True" DataField="CreateUserID" SortExpression="CreateUserID"
                HeaderText="Created By" />
            <CC1:MasterControlField ShowReturns="false" DataField="CreatedDateTime" SortExpression="CreatedDateTime"
                HeaderText="Created On" DataFormatString="{0:d}" />
            <CC1:MasterControlField ShowReturns="False" DataField="ClosedActivities" Visible="true"
                SortExpression="ClosedActivities" HeaderText="Activities w/Results" />
            <CC1:MasterControlField ShowReturns="False" DataField="OpenActivities" Visible="true"
                SortExpression="OpenActivities" HeaderText="Activites w/o Results" />
            <CC1:MasterControlField ShowReturns="False" DataField="SLICEActivityGroupID" Visible="false"
                SortExpression="SLICEActivityGroupID" HeaderText="Checksheet ID" />
        </GridColumns>
    </CC1:MasterControl>
</asp:Content>
