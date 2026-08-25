<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="FeedbackMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.FeedbackMaster2"
    Title="Feedback" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label8" runat="server" Text="Feedback ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtID" runat="server" CssClass="Textbox_Display" MaxLength="15"
                    Width="80px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="lblRoute" runat="server" Text="Created Date/Time:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDateTime" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="175px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label1" runat="server" Text="Feedback:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandFeedback" runat="server" CssClass="Textbox_Display" MaxLength="100"
                    Width="464px" TextMode="MultiLine" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label2" runat="server" Text="User ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUserID" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="175px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label3" runat="server" Text="Program:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtProgram" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="224px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label5" runat="server" Text="Comments:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandComments" runat="server" CssClass="Textbox_Entry" MaxLength="1000"
                    Width="456px" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label6" runat="server" Text="Feedback Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlFeedbackType" runat="server" Width="128px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtFeedbackType" runat="server" ReadOnly="True" Width="112px" MaxLength="50"
                    CssClass="Textbox_Display" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label7" runat="server" Text="Feedback Priority:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlFeedbackPriority" runat="server" Width="128px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtFeedbackPriority" runat="server" ReadOnly="True" Width="112px"
                    MaxLength="50" CssClass="Textbox_Display" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 130px">
                <asp:Label ID="Label4" runat="server" Text="Developer Comments:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandDevComments" runat="server" Width="456px" MaxLength="1000"
                    CssClass="Textbox_Entry" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px" colspan="2">
                <asp:CheckBox ID="chkProcessed" runat="server" Text="Processed" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px" colspan="2">
                <asp:CheckBox ID="chkSendEmail" runat="server" Text="Send Email to User" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
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
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
