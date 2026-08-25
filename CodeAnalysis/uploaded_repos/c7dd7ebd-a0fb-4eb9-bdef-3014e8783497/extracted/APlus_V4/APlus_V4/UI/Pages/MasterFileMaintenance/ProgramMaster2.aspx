<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="ProgramMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.ProgramMaster2"
    Title="Program Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="Label1" runat="server" Text="Program:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtProgram" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="300px"></asp:TextBox><asp:RequiredFieldValidator ID="reqProgram" runat="server"
                        ErrorMessage="Enter a Program" ControlToValidate="txtProgram" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="Label2" runat="server" Text="Program URL:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtProgramURL" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="500px"></asp:TextBox><asp:RequiredFieldValidator ID="reqProgramURL" runat="server"
                        ErrorMessage="Enter a ProgramURL" ControlToValidate="txtProgramURL" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="Label3" runat="server" Text="Help File:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtHelpFile" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="500px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="Label4" runat="server" Text="Program Shortcut:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtProgramShortcut" runat="server" Width="72px" MaxLength="50" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <asp:CheckBox ID="chkMenu" runat="server" Text="Menu" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <asp:CheckBox ID="chkInitialProgram" runat="server" Text="Initial Program" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <asp:CheckBox ID="ckTeamSelectionRequired" runat="server" Text="Team Selection Required"
                    CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <asp:CheckBox ID="ckTeamBoardSelection" runat="server" Text="Team Board Menu Option Master Selection"
                    CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="Label5" runat="server" Text="Team Board Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDescription" runat="server" Width="312px" MaxLength="50" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="Label6" runat="server" Text="Link Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlLinkTypes" runat="server" Width="56px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="F">F</asp:ListItem>
                    <asp:ListItem Value="P">P</asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtLinkType" runat="server" Width="24px" MaxLength="50" CssClass="Textbox_Display"
                    Visible="False"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td>
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
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
