<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="JobMaster3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.JobMaster3"
    Title="Job Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblJobID" runat="server" Text="Job ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtJobID" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="40px" ReadOnly="True"></asp:TextBox>
                <asp:TextBox ID="txtOldJobName" ReadOnly="True" Width="40px" MaxLength="50" CssClass="Textbox_Display"
                    runat="server" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblJob" runat="server" Text="Job:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtJob" Width="313px" MaxLength="50" CssClass="Textbox_Entry" runat="server"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqJob" runat="server" ControlToValidate="txtJob"
                    ErrorMessage="Enter Job Name" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label6" runat="server" Text="Rating Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlRatingType" runat="server" Width="168px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:RequiredFieldValidator ID="reqRatingType" runat="server" Display="None" ErrorMessage="Select Rating Type"
                    ControlToValidate="ddlRatingType" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <asp:Panel ID="pnlTeam" runat="server" Visible="True">
            <tr>
                <td>
                    <asp:Label ID="Label3" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlTeam" runat="server" Width="313" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:RequiredFieldValidator ID="reqTeam" runat="server" Display="None" ErrorMessage="Select Team"
                        ControlToValidate="ddlTeam" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                </td>
            </tr>
        </asp:Panel>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
