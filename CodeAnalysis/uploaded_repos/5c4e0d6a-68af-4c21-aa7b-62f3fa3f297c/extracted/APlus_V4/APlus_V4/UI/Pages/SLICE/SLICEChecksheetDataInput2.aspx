<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEChecksheetDataInput2.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEChecksheetDataInput2"
    Title="Edit SLICE Checksheet Data " %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td>
                <asp:Label ID="lblEntityNum" runat="server" Text="Entity #" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEntityNum" runat="server" MaxLength="10" ReadOnly="True" CssClass="Textbox_Display"
                    Width="104px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblCoLoc" runat="server" Text="Component/Location:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandCoLoc" runat="server" ReadOnly="True" CssClass="Textbox_Display"
                    Width="256px" TextMode="MultiLine" Height="28px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblPosition" runat="server" Text="Pos:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:TextBox ID="txtPosition" runat="server" MaxLength="50" ReadOnly="True" CssClass="Textbox_Display"
                    Width="256px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td valign="middle">
                <asp:Label ID="lblMeetsDesiredConditions" runat="server" Text="Meets Desired Condition:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <table cellspacing="1" cellpadding="1" border="0">
                    <tr>
                        <td>
                            <asp:RadioButtonList ID="rdoMeetsDesiredCon" runat="server" Width="64px">
                                <asp:ListItem Value="1">Yes</asp:ListItem>
                                <asp:ListItem Value="2">No</asp:ListItem>
                            </asp:RadioButtonList>
                        </td>
                        <td valign="middle">
                            <asp:Button ID="btnClear" runat="server" CssClass="Button_Variable" Text="Clear Desired Condition Selected"
                                Width="175px" />
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblElapsedTime" runat="server" Text="Elapsed Time:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtElapsedTime" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="256px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblComments" runat="server" Text="Comments:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:TextBox ID="txtExpandComments" runat="server" CssClass="Textbox_Entry" Width="256px"
                    TextMode="MultiLine" Height="28px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblWorkOrdNum" runat="server" Text="Workorder Number:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtWorkOrderNum" runat="server" MaxLength="50" CssClass="Textbox_Entry"
                    Width="256px"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table>
            <tr>
                <td class="style1">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
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
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 125px;
        }
    </style>
</asp:Content>
