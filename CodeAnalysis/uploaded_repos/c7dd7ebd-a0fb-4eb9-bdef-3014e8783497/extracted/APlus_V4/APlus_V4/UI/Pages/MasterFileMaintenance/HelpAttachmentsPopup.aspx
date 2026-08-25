<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="HelpAttachmentsPopup.aspx.vb" Inherits="WebApp.APlus.UI.Pages.HelpAttachmentsPopup"
    Title="Help Attachments" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/AttachmentStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <br />
    <div class="grid">
        <div class="rounded">
            <div class="top-outer">
                <div class="top-inner">
                    <div class="top">
                        <h2>
                            <asp:Label ID="lblInfo" runat="server" Text="No Attachments Exist"></asp:Label></h2>
                    </div>
                </div>
            </div>
            <div class="mid-outer">
                <div class="mid-inner">
                    <div class="mid">
                        <asp:Table ID="tblAttachments" runat="server" Width="100%" BorderWidth="0" CssClass="datatable"
                            CellPadding="0" CellSpacing="0" GridLines="None">
                        </asp:Table>
                    </div>
                </div>
            </div>
            <div class="bottom-outer">
                <div class="bottom-inner">
                    <div class="bottom">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <br />
</asp:Content>
