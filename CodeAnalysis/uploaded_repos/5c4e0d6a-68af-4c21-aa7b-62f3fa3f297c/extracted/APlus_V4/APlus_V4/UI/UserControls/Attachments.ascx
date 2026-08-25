<%@ Control Language="VB" AutoEventWireup="false" CodeFile="Attachments.ascx.vb"
    Inherits="WebApp.APlus.UI.UserControls.Attachments" %>
<asp:GridView ID="gvAttachments" runat="server" AutoGenerateColumns="false" SkinID="GridView"
    Width="480px">
    <Columns>
        <asp:TemplateField HeaderText="Attachment">
            <HeaderStyle HorizontalAlign="left" />
            <ItemStyle HorizontalAlign="left" />
            <ItemTemplate>
                <asp:Image runat="server" ImageUrl="~/images/small_mail_attachment.gif" ID="imgAttach" />
                <asp:HyperLink runat="server" ID="hlAttachment" Style="cursor: hand; color: blue;
                    text-decoration: underline" Text='<%# DataBinder.Eval(Container.DataItem, "AttachmentsText") %>'
                    NavigateUrl='<%# DataBinder.Eval(Container.DataItem, "AttachmentsURL") %>' Target="_blank"></asp:HyperLink>
            </ItemTemplate>
        </asp:TemplateField>
        <asp:TemplateField HeaderText="Delete">
            <HeaderStyle HorizontalAlign="right" />
            <ItemStyle HorizontalAlign="right" />
            <ItemTemplate>
                <asp:ImageButton runat="server" CommandName="DeleteAttachment" ToolTip="Delete Attachment"
                    ID="btnDelete" ImageUrl="../../Images/delete.gif" />
            </ItemTemplate>
        </asp:TemplateField>
    </Columns>
</asp:GridView>
<asp:Panel ID="pnlOKCancel" Width="173px" runat="server">
    <table id="tbButtons" style="width: 480px" cellspacing="5" width="480" border="0">
        <tr>
            <td align="center">
                <input id="fil" style="font-size: 8pt; width: 386px; font-family: Verdana; height: 24px"
                    type="file" size="45" name="fil" runat="server" />
            </td>
            <td align="center">
                <asp:Button ID="btnAttach" Width="74px" runat="server" Font-Size="8pt" Font-Names="Microsoft Sans Serif"
                    EnableViewState="False" Text="Attach" Height="24px"></asp:Button>
            </td>
        </tr>
    </table>
</asp:Panel>
