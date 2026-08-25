<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyActionsSummary.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyActionsSummary"
    Title="Anomaly Actions Summary" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table>
        <tr>
            <td valign="top">
                <table>
                    <tr>
                        <td class="style6">
                            <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
                        </td>
                        <td>
                            <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" 
                                Width="250px" AutoPostBack="True">
                            </asp:DropDownList>
                        </td>
                    </tr>
                    <tr>
                        <td class="style6">
                            <asp:Label ID="lblAreaGroup" runat="server" Text="Area Group:" 
                                CssClass="Label_Left_8PT"></asp:Label>
                        </td>
                        <td>
                <asp:DropDownList ID="ddlAreaGroup" runat="server" 
                    CssClass="DropdownList_Entry" Width="250px">
                </asp:DropDownList>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    <asp:RequiredFieldValidator ID="reqSite" runat="server" ErrorMessage="Select Site"
        ControlToValidate="ddlSite" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table>
            <tr>
                <td class="style4">
                    <asp:Button ID="btnRunReport" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="Run Report" />
                </td>
                <td align="left" class="style4">
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
        .style4
        {
            width: 150px;
        }
        .style6
        {
            width: 75px;
        }
    </style>
</asp:Content>
