<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="PositionMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.PositionMaster2"
    Title="Position Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 110px;">
                <asp:Label ID="Label1" runat="server" Text="Position ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPositionID" runat="server" CssClass="Textbox_Display" MaxLength="5"
                    Width="56px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px;">
                <asp:Label ID="Label2" runat="server" Text="Workcenter:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlWorkcenter" runat="server" Width="200px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtWorkcenter" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="200px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label3" runat="server" Text="Position:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPosition" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="577px"></asp:TextBox><asp:RequiredFieldValidator ID="reqPosition" runat="server"
                        Display="None" ControlToValidate="txtPosition" ErrorMessage="Enter Position"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <div>
        <div>
            <asp:Panel ID="pnlOKCancel" runat="server">
                <table id="tbButtons" class="Table_Default">
                    <tr>
                        <td style="width: 110px">
                            <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                            </asp:Button>
                        </td>
                        <td>
                            <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                                CausesValidation="False"></asp:Button>
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <div>
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
            </div>
        </div>
        <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
        <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
            ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
    </div>
</asp:Content>
