<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TemplateAttachments.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TemplateAttachments"
    Title="Attachments" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>

<%@ Register TagPrefix="ApplicationControls" TagName="Attachments" Src="../../UserControls/Attachments.ascx" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <ApplicationControls:Attachments ID="ucTemplateAttachments" runat="server"></ApplicationControls:Attachments>
    <br />
    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" CausesValidation="False"
        Text="Exit"></asp:Button>
</asp:Content>
