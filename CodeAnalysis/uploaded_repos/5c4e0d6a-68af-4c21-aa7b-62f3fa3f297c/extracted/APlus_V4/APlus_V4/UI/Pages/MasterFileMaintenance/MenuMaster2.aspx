<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MenuMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MenuMaster2"
    Title="Menu Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label2" runat="server" CssClass="Label_Left_8PT">Menu:</asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlMenu" runat="server" Width="325px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtMenu" Width="328px" runat="server" CssClass="Textbox_Display"
                    MaxLength="50" ReadOnly="True" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqMenu" runat="server" ErrorMessage="Enter Menu Name"
                    ControlToValidate="ddlMenu" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <asp:Panel runat="server" ID="pnlUser" Visible="False">
        </asp:Panel>
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label1" runat="server" CssClass="Label_Left_8PT">Menu Text:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMenuText" MaxLength="50" CssClass="Textbox_Entry" runat="server"
                    Width="328px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqMenuText" CssClass="Label_Left_8PT" runat="server"
                    Display="None" ControlToValidate="txtMenuText" ErrorMessage="Enter Menu Name"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label5" CssClass="Label_Left_8PT" runat="server">Menu Type:</asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlMenuType" runat="server" Width="347px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtMenuType" Width="312px" ReadOnly="True" MaxLength="50" CssClass="Textbox_Display"
                    runat="server" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqMenuType" CssClass="Label_Left_8PT" runat="server"
                    Display="None" ControlToValidate="ddlMenuType" ErrorMessage="Enter Menu Type"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label4" CssClass="Label_Left_8PT" runat="server">Show Program Groups:</asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckShowProgramGroups" runat="server" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label6" CssClass="Label_Left_8PT" runat="server">Allow Program Shortcuts:</asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowProgramShortcuts" runat="server" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label3" CssClass="Label_Left_8PT" runat="server">Show Program Shortcuts:</asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckShowProgramShortcuts" runat="server" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label9" CssClass="Label_Left_8PT" runat="server">Hide Option Numbers:</asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="chkHideOptionNumbers" runat="server" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label8" CssClass="Label_Left_8PT" runat="server">Allow User Specified Columns:</asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowUserSpecifiedColumns" runat="server" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 146px">
                <asp:Label ID="Label7" CssClass="Label_Left_8PT" runat="server">Max Columns:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMaxColumns" MaxLength="2" CssClass="Textbox_Entry" runat="server"
                    Width="23px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqColumns" CssClass="Label_Left_8PT" runat="server"
                    Display="None" ControlToValidate="txtMaxColumns" ErrorMessage="Enter Max Columns"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
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
                <td style="width: 125px">
                    <asp:Button ID="btnProgramGroups" runat="server" CssClass="Button_Variable" Text="Program Groups">
                    </asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnMenuOptionMaster" runat="server" CssClass="Button_Variable" Text="Menu Option Master">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnProgramGroups2" runat="server" CssClass="Button_Variable" Text="Program Groups"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory" runat="server" InitialStateExpanded="False"
        TableName="MenuMaster" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
