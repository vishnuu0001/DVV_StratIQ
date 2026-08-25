<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TemplateAttachments2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TemplateAttachments2"
    Title="Template Attachments" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 113px; height: 12px">
                <asp:Label ID="Label1" runat="server" Text="File:" CssClass="Label_Left_8PT">
                </asp:Label>
            </td>
            <td style="height: 12px">
                <input id="fil" type="file" size="45" name="fil" runat="server" />
                <asp:TextBox ID="txtAttachment" runat="server" CssClass="Textbox_Display" MaxLength="100"
                    Width="250px" Visible="False" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 113px">
                <asp:Label ID="Label2" runat="server" Text="Category Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlCategory" runat="server" Width="192px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtCategory" runat="server" CssClass="Textbox_Display" MaxLength="100"
                    Width="200px" Visible="False" ReadOnly="True"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqCategoryType" runat="server" ErrorMessage="Select Category Type" ControlToValidate="ddlCategory"
                        Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr runat="server" id="trMasterAttachment">
            <td style="width: 113px">
                <asp:Label ID="Label4" runat="server" Text="Master Attachment:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlMasterAttachment" runat="server" Width="250px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtMasterAttachment" runat="server" CssClass="Textbox_Display" MaxLength="100"
                    Width="250px" Visible="False" ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqMasterAttachment" runat="server" ErrorMessage="Select Master Attachment"
                    ControlToValidate="ddlMasterAttachment" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
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
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
