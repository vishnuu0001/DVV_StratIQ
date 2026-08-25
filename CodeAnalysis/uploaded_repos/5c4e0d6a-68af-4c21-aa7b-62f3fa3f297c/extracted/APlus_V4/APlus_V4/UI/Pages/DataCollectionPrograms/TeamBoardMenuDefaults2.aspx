<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamBoardMenuDefaults2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamBoardMenuDefaults2"
    Title="Team Board Menu Defaults" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblTeamBoardMenuDefault" runat="server" Text="ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeamBoardMenuDefault" runat="server" CssClass="Textbox_Display"
                    MaxLength="3" Width="31px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="216px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblBoardColumn" runat="server" Text="Board Column:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtBoardColumn" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqBoardColumn" runat="server" ErrorMessage="Enter Board Column"
                    ControlToValidate="txtBoardColumn" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:RangeValidator ID="rngBoardColumn" runat="server" ErrorMessage="Enter 1-9" ControlToValidate="txtBoardColumn"
                    MaximumValue="9" CssClass="Label_Left_8PT" MinimumValue="1" Text="Enter 1-9"></asp:RangeValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblBoardRow" runat="server" Text="Board Row:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtBoardRow" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqBoardRow" runat="server" ErrorMessage="Enter Board Row"
                    ControlToValidate="txtBoardRow" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:RangeValidator ID="rngBoardRow" runat="server" ErrorMessage="Enter 1-9" ControlToValidate="txtBoardRow"
                    MaximumValue="9" CssClass="Label_Left_8PT" MinimumValue="1" Text="Enter 1-9"></asp:RangeValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblRCSequence" runat="server" Text="RC Sequence:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRCSequence" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqRCSequence" runat="server" ErrorMessage="Enter RC Sequence"
                    ControlToValidate="txtRCSequence" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:RangeValidator ID="rngRCSequence" runat="server" ErrorMessage="Enter 1-9" ControlToValidate="txtRCSequence"
                    MaximumValue="9" CssClass="Label_Left_8PT" MinimumValue="1" Text="Enter 1-9"></asp:RangeValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblDescription" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDescription" runat="server" CssClass="Textbox_Entry" MaxLength="55"
                    Width="350px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqDescription" runat="server" ErrorMessage="Enter Description"
                    ControlToValidate="txtDescription" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblProgram" runat="server" Text="Program:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlProgram" runat="server" CssClass="DropdownList_Entry" Width="194px"
                    AutoPostBack="True">
                </asp:DropDownList>
                <asp:TextBox ID="txtProgram" runat="server" CssClass="Textbox_Display" ReadOnly="true"
                    Width="184px" Visible="false"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblLinkFileURL" runat="server" Text="Link File URL:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td class="style2">
                <asp:TextBox ID="txtLinkFileURL" runat="server" CssClass="Textbox_Entry" MaxLength="150"
                    Width="350px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblDefault" runat="server" Text="Default" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckDefault" runat="server" />
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblTeamFolderDocument" runat="server" Text="Team Folder Document"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckTeamFolderDocument" runat="server" />
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
