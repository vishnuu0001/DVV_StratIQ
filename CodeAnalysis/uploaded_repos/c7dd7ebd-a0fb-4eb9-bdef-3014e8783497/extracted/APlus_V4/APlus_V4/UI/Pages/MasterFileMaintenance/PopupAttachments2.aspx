<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="PopupAttachments2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.PopupAttachments2"
    Title="Popup Attachments" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 113px">
                <asp:Label ID="Label1" runat="server" Text="File:" CssClass="Label_Left_8PT"> 
                </asp:Label>
            </td>
            <td>
                <input id="fil" type="file" size="45" name="fil" runat="server" />
                <asp:TextBox ID="txtAttachment" runat="server" CssClass="Textbox_Display" MaxLength="100"
                    Width="250px" Visible="False" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 113px">
                <asp:Label ID="Label2" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" Width="192px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" MaxLength="100"
                    Width="200px" Visible="False" ReadOnly="True"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqSite" runat="server" ErrorMessage="Select Site" ControlToValidate="txtSite"
                        Display="None" Enabled="False" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 113px">
                <asp:Label ID="Label3" runat="server" Text="Popup Attempts:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPopupAttempts" runat="server" Width="40px" MaxLength="3" CssClass="Textbox_Entry"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqPopupAttempts" runat="server" Enabled="False"
                    Display="None" ControlToValidate="txtPopupAttempts" ErrorMessage="Enter Popup Attempts"
                    CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 113px">
                <asp:Label ID="Label4" runat="server" Text="Active:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="chkPopupActive" runat="server" CssClass="Checkbox_Default" Checked="False">
                </asp:CheckBox>
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
                <td style="width: 110px">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnClearUserLogins" runat="server" CssClass="Button_Variable" Text="Clear All User Login Counts"
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
</asp:Content>
