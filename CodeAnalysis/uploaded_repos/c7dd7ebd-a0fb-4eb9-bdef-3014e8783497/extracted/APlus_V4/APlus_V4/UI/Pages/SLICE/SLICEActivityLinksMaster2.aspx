<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEActivityLinksMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityLinksMaster2"
    Title="SLICE Activity Links Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/WorkcenterSubHeader.ascx" TagName="WorkcenterSubHeader"
    TagPrefix="uc1" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc2" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <uc1:WorkcenterSubHeader ID="WorkcenterSubHeader1" runat="server"></uc1:WorkcenterSubHeader>
    <br />
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 125px">
                <asp:Label ID="lblSLICEActivityLinkID" runat="server" Text="SLICE Activity Link ID:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEActivityLinkID" runat="server" MaxLength="10" ReadOnly="True"
                    CssClass="Textbox_Display" Width="48px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 125px">
                <asp:Label ID="lblSLICEActivityID" runat="server" CssClass="Label_Left_8PT" Text="SLICE Activity:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEActivityID" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="256px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 125px">
                <asp:Label ID="lblSLICEActivityLinkTypeID" runat="server" CssClass="Label_Left_8PT"
                    Text="SLICE Activity Link Type:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEActivityLinkTypeID" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="256px"></asp:TextBox><asp:DropDownList ID="ddlSLICEActivityLinkTypeID" runat="server"
                        CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                <asp:RequiredFieldValidator ID="reqActivityLinkTypeID" runat="server" ControlToValidate="txtSLICEActivityLinkTypeID"
                    Display="None" ErrorMessage="Enter SLICE Activity Link Type ID"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 125px">
                <asp:Label ID="lblLinkDescription" runat="server" CssClass="Label_Left_8PT" Text="Link Description:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandLinkDescription" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="256px"></asp:TextBox><asp:RequiredFieldValidator ID="reqLinkDescription" runat="server"
                        ControlToValidate="txtExpandLinkDescription" Display="None" ErrorMessage="Enter Link Description"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 125px">
                <asp:Label ID="lblLinkURL" runat="server" CssClass="Label_Left_8PT" Text="Link URL:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandLinkURL" runat="server" MaxLength="500" CssClass="Textbox_Entry"
                    Width="256px"></asp:TextBox><asp:RequiredFieldValidator ID="reqLinkURL" runat="server"
                        ControlToValidate="txtExpandLinkURL" Display="None" ErrorMessage="Enter Link URL"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 125px">
            </td>
            <td>
                <asp:TextBox ID="hdnSLICEActivityID" runat="server" MaxLength="10" ReadOnly="True"
                    CssClass="Textbox_Display" Width="48px" Visible="False"></asp:TextBox><asp:TextBox
                        ID="hdnSLICEActivityLinkTypeID" runat="server" MaxLength="10" ReadOnly="True"
                        CssClass="Textbox_Display" Width="48px" Visible="False"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <br />
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
    <uc2:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
