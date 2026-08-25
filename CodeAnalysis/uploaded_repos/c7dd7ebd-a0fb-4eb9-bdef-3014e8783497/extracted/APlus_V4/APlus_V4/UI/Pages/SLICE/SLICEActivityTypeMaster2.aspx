<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEActivityTypeMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityTypeMaster2"
    Title="Slice Type Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td class="style1">
                <asp:Label ID="Label2" runat="server" Text="SLICE Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSLICEType" runat="server" CssClass="DropdownList_Entry"
                    Width="232px">
                </asp:DropDownList>
                <asp:TextBox ID="txtSLICEType" runat="server" MaxLength="50" ReadOnly="True" Visible="false"
                    CssClass="Textbox_Display" Width="256px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSliceType" runat="server" Display="None" ErrorMessage="Select Slice Type"
                    ControlToValidate="ddlSLICEType"></asp:RequiredFieldValidator>
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
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 98px;
        }
    </style>
</asp:Content>
