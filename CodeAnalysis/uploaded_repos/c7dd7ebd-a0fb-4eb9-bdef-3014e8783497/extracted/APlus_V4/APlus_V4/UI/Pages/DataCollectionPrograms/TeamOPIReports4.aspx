<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/PrinterFriendly.master"
    AutoEventWireup="false" CodeFile="TeamOPIReports4.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIReports4"
    Title="OPI Reports" %>

<%@ Register TagPrefix="uc1" TagName="TeamOPIGraph" Src="~/UI/UserControls/TeamOPIGraph.ascx" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.PrinterFriendly" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript" src="../../../Scripts/CommonFunctions.js"></script>

    <table id="Table1" class="Table_Default">
        <tr>
            <td style="width: 20%; text-align: left">
                <asp:Image runat="server" ID="Image2" ImageUrl="~/Images/company_logo.png">
                </asp:Image>
            </td>
            <td style="width: 60%">
                <table id="Table2" class="Table_Default">
                    <tr>
                        <td style="text-align: center">
                            <asp:Label runat="server" ID="lblTeamName" Text="Team Name Goes Here" CssClass="Label_Left_8PT"></asp:Label>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center">
                            <asp:Label runat="server" ID="lblTeam" Text="Team Goes Here" CssClass="Label_Left_8PT"></asp:Label>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center">
                            <asp:Label runat="server" ID="lblOPI"  CssClass="Label_Left_8PT"  Text="OPI Goes Here"></asp:Label>
                        </td>
                    </tr>
                </table>
            </td>
            <td style="width: 20%; text-align: right">
                <asp:Image runat="server" ID="Image1" ImageUrl="~/Images/APlus.jpg"></asp:Image>
            </td>
        </tr>
    </table>
    <table align="center">
        <tr>
            <td align="center">
                <uc1:TeamOPIGraph ID="TeamOPIGraph1" runat="server" />
            </td>
        </tr>
    </table>
</asp:Content>
