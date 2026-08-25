<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEActivityGroupMaster2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityGroupMaster2"
    Title="SLICE Activity Group Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table>
        <tr>
            <td>
                <asp:Label ID="Label1" runat="server" Text="Checksheet Template ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEActivityGroupID" runat="server" CssClass="Textbox_Display"
                    MaxLength="5" Width="56px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label2" runat="server" Text="Checksheet Template:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEActivityGroup" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="256px"></asp:TextBox><asp:RequiredFieldValidator ID="reqSLICEActivityGroup"
                        runat="server" ErrorMessage="Enter SLICE Activity Group" ControlToValidate="txtSLICEActivityGroup"
                        Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label3" runat="server" Text="Checksheet Template Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSLICEActivityGroupDescription" runat="server" CssClass="Textbox_Entry"
                    MaxLength="50" Width="577px"></asp:TextBox><asp:RequiredFieldValidator ID="reqSLICEActivityGroupDescription"
                        runat="server" ErrorMessage="Enter SLICE Activity Group Description" ControlToValidate="txtSLICEActivityGroupDescription"
                        Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label4" runat="server" Text="Workcenter:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlWorkcenter" runat="server" Width="250px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtWorkcenter" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="237px" ReadOnly="True" Height="16px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="Label5" runat="server" Text="Target Deviation:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTargetDeviation" runat="server" CssClass="Textbox_Entry" MaxLength="4"
                    Width="72px"></asp:TextBox><asp:RequiredFieldValidator ID="reqTargetDeviation" runat="server"
                        ErrorMessage="Enter Target Deviation" ControlToValidate="txtTargetDeviation"
                        Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td>
            </td>
            <td>
            </td>
        </tr>
    </table>
    <table id="Table2" style="width: 321px; height: 26px" cellspacing="2" cellpadding="2"
        width="321" border="0">
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table>
            <tr>
                <td class="style1">
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
        <table>
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
<asp:Content ID="Content2" runat="server" contentplaceholderid="ContentHeader">

    <style type="text/css">
        .style1
        {
            width: 150px;
        }
    </style>

</asp:Content>

