<%@ Control Language="VB" AutoEventWireup="false" CodeFile="TransactionHistory.ascx.vb"
    Inherits="WebApp.APlus.UI.UserControls.TransactionHistory" %>
<table id="tblExpandCollapse" cellpadding="0" cellspacing="0" width="100%" runat="server"
    style="margin-top: 10px; margin-bottom: 3px;">
    <tr>
        <td style="width: 18px; vertical-align: bottom; text-align: left; text-indent: 3px;">
            <asp:ImageButton ID="ibExpandAll" runat="server" ToolTip="Show Transaction Information"
                ImageUrl="~/images/plus.gif" CausesValidation="False"></asp:ImageButton>
            <asp:ImageButton ID="ibCollapseAll" runat="server" ToolTip="Hide Transaction Information"
                ImageUrl="~/images/minus.gif" CausesValidation="False"></asp:ImageButton>
        </td>
        <td style="text-align: left; vertical-align: middle">
            <asp:Label runat="server" ID="lblText" Text="Transaction History"></asp:Label>
        </td>
    </tr>
</table>
<asp:Panel runat="server" ID="pnlHistory" CssClass="Panel_History">
    <asp:GridView runat="server" ID="grdHistory" Width="100%" AutoGenerateColumns="False"
        EmptyDataText="No Transaction History" SkinID="GridView">
        <RowStyle HorizontalAlign="Left" VerticalAlign="Top" />
        <AlternatingRowStyle HorizontalAlign="Left" VerticalAlign="Top" />
        <Columns>
            <asp:BoundField DataField="TransactionDateTime" HeaderText="Timestamp">
                <ItemStyle Width="150px" />
            </asp:BoundField>
            <asp:BoundField DataField="UserName" HeaderText="User">
                <ItemStyle Width="150px" />
            </asp:BoundField>
            <asp:BoundField DataField="RecordInformation" HeaderText="Record History" />
        </Columns>
        <EmptyDataRowStyle HorizontalAlign="Left" VerticalAlign="Middle" />
    </asp:GridView>
</asp:Panel>
