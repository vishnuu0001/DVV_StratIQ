<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEFrequencyMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEFrequencyMaster2"
    Title="Slice Frequency Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 150px; height: 32px">
                <asp:Label ID="Label1" runat="server" Text="SLICE Frequency ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 32px">
                <asp:TextBox ID="txtSLICEFrequencyID" runat="server" CssClass="Textbox_Display" MaxLength="5"
                    Width="88px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="Label2" runat="server" Text="SLICE Frequency Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEFrequency" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="577px"></asp:TextBox><asp:RequiredFieldValidator ID="reqSLICEFrequency" runat="server"
                        ErrorMessage="Enter a SLICE Frequency Description" ControlToValidate="txtSLICEFrequency"
                        Display="None"></asp:RequiredFieldValidator>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
