<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICECheckSheetMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICECheckSheetMaster2"
    Title="SLICE Checksheet Master" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/WorkcenterSubHeader.ascx" TagName="WorkcenterSubHeader"
    TagPrefix="uc1" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc2" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <uc1:WorkcenterSubHeader ID="WorkcenterSubHeader1" runat="server"></uc1:WorkcenterSubHeader>
    <br />
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 150px;">
                <asp:Label ID="lblSLICEChecksheetID" runat="server" CssClass="Label_Left_8PT" Text="Checksheet ID:"> </asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEChecksheetID" runat="server" Width="120px" CssClass="Textbox_Display"
                    ReadOnly="True" MaxLength="10"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px;">
                <asp:Label ID="lblSLICEActivityGrpID" runat="server" CssClass="Label_Left_8PT" Text="Checksheet Template:"> </asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlCheckSheetTemplates" runat="server" Width="350px" CssClass="DropdownList_Entry"
                    Visible="False">
                </asp:DropDownList>
                <asp:TextBox ID="txtSLICEActivityGroup" runat="server" Width="350px" CssClass="Textbox_Display"
                    ReadOnly="True" MaxLength="50"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTemplateSelection" runat="server" ControlToValidate="ddlCheckSheetTemplates"
                    ErrorMessage="Select Checksheet Template!" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px;" valign="top">
                <asp:Label ID="lblReleaseDate" runat="server" CssClass="Label_Left_8PT" Text="Release Date:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtReleaseDate" runat="server" Width="76px" CssClass="Textbox_Entry"
                    MaxLength="20"></asp:TextBox>
                <cc1:CalendarExtender ID="txtReleaseDate_CalendarExtender" runat="server" PopupButtonID="imgReleaseDate"
                    TargetControlID="txtReleaseDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgReleaseDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqReleaseDate" runat="server" ControlToValidate="txtReleaseDate"
                    ErrorMessage="Enter a Release Date!" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 16px" valign="top">
                <asp:Label ID="lblDueDate" runat="server" CssClass="Label_Left_8PT" Text="Due Date:"></asp:Label>
            </td>
            <td style="height: 16px">
                <asp:TextBox ID="txtDueDate" runat="server" Width="76px" CssClass="Textbox_Entry"
                    MaxLength="20" EnableViewState="False"></asp:TextBox>
                <cc1:CalendarExtender ID="txtDueDate_CalendarExtender" runat="server" PopupButtonID="imgDueDate"
                    TargetControlID="txtDueDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgDueDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqDueDate" runat="server" ControlToValidate="txtDueDate"
                    ErrorMessage="Enter a Due Date!" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px; height: 20px" valign="top">
                <asp:Label ID="lblChecksheetStatus" runat="server" CssClass="Label_Left_8PT" Text="Status:"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlCheckSheetStatus" runat="server" Width="128px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSheetStatus" runat="server" Width="120px" CssClass="Textbox_Display"
                    MaxLength="50" ReadOnly="True" Visible="false"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblCreateUser" runat="server" CssClass="Label_Left_8PT" Text="Created By:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtCreatedUserId" runat="server" Width="120px" CssClass="Textbox_Display"
                    MaxLength="8" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px;" valign="top">
                <asp:Label ID="lblCreationDate" runat="server" CssClass="Label_Left_8PT" Text="Creation Date:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtCreateDate" runat="server" Width="76px" CssClass="Textbox_Display"
                    MaxLength="20" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px;" valign="top">
                <asp:Label ID="lblNumberPrinted" runat="server" CssClass="Label_Left_8PT" Text="Number Printed:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtNumPrinted" runat="server" Width="55px" CssClass="Textbox_Display"
                    MaxLength="4" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px;" valign="top">
                <asp:Label ID="lblLastPrintDate" runat="server" CssClass="Label_Left_8PT" Text="Last Printing:"></asp:Label>
            </td>
            <td valign="top">
                <asp:TextBox ID="txtLastPrintDate" runat="server" Width="76px" CssClass="Textbox_Display"
                    MaxLength="20" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px;">
                <asp:Label ID="lblLastUserToPrint" runat="server" CssClass="Label_Left_8PT" Text="Last User To Print:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLastUserToPrint" runat="server" Width="120px" CssClass="Textbox_Display"
                    MaxLength="8" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="OK"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <asp:Panel ID="pnlExit" runat="server">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc2:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
