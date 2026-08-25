<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="HelpAttachments2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.HelpAttachments2"
    Title="Help Attachments" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 113px; height: 12px">
                <asp:Label ID="Label1" runat="server">File:
                </asp:Label>
            </td>
            <td style="height: 12px">
                <input id="fil" type="file" size="45" name="fil" runat="server" class="Textbox_entry" />
                <asp:TextBox ID="txtAttachment" runat="server" CssClass="Textbox_Display" MaxLength="100"
                    Width="250px" Visible="False" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 113px">
                <asp:Label ID="Label2" runat="server">Category Type:</asp:Label>
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
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" cellspacing="2" cellpadding="2" width="321" border="0">
            <tr>
                <td style="width: 153px" align="right">
                    <p align="left">
                        <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                        </asp:Button></p>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" cellspacing="2" cellpadding="2" width="321" border="0">
            <tr>
                <td align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
