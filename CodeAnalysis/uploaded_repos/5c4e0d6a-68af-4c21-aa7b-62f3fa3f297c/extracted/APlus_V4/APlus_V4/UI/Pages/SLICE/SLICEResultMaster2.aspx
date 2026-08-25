<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEResultMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEResultMaster2"
    Title="Slice Result Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 125px; height: 32px">
                <asp:Label ID="Label1" runat="server" Text="SLICE Result ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 32px">
                <asp:TextBox ID="txtSLICEResultID" runat="server" Width="88px" MaxLength="5" CssClass="Textbox_Display"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 125px">
                <asp:Label ID="Label2" runat="server" Text="SLICE Result Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEResultText" runat="server" Width="577px" MaxLength="50"
                    CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator ID="reqSLICEResultText"
                        runat="server" Display="None" ControlToValidate="txtSLICEResultText" ErrorMessage="Enter a SLICE Result Description."></asp:RequiredFieldValidator>
            </td>
            <td>
            </td>
        </tr>
        <tr>
            <td style="width: 125px">
            </td>
            <td>
                <asp:CheckBox ID="chkPass" runat="server" CssClass="Checkbox_Default" Text="Pass">
                </asp:CheckBox>
            </td>
            <td>
            </td>
        </tr>
        <tr>
            <td style="width: 125px">
                <asp:Label ID="Label3" runat="server" Text="Presentation Sequence:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPresentationSequence" runat="server" Width="40px" MaxLength="5"
                    CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator ID="reqPresentationSequence"
                        runat="server" Display="None" ControlToValidate="txtPresentationSequence" ErrorMessage="Enter a Presentation Sequence."></asp:RequiredFieldValidator>
            </td>
            <td>
            </td>
        </tr>
    </table>
    <table id="Table2" style="width: 321px; height: 26px" cellspacing="2" cellpadding="2"
        width="321" border="0">
    </table>
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
