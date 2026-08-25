<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrainingDocumentAttachments1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrainingDocumentAttachments1"
    Title="Training Document Attachments" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:UpdateProgress ID="UpdateProgress1" runat="server" DisplayAfter="50">
        <ProgressTemplate>
            <div style="position: absolute; z-index: 1;">
                <asp:Image runat="server" ID="imgWait" Height="48" Width="48" ImageUrl="~/images/barcircle.gif" />
                <asp:AlwaysVisibleControlExtender ID="imgWait_AlwaysVisibleControlExtender" runat="server"
                    Enabled="True" TargetControlID="imgWait" VerticalSide="Middle" HorizontalSide="Center">
                </asp:AlwaysVisibleControlExtender>
            </div>
        </ProgressTemplate>
    </asp:UpdateProgress>
    <asp:UpdatePanel ID="UpdatePanel1" runat="server">
        <ContentTemplate>
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowExport="True" CommandText="spSelAttachmentsMaster"
                ProgramName="TrainingDocumentAttachments1" FormName="Training Attachments" RedirectProgramName="TrainingDocumentAttachments2"
                NewLinkCaption="Training Attachment" ShowView="True" ShowEdit="False" ShowDelete="True"
                ShowAdd="True" ProgramMode="TrainingAttachmentMode" AlternatingRows="true">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" ShowReturns="False" DataField="AttachmentID"
                        HeaderText="AttachmentID" />
                    <CC1:MasterControlField ShowReturns="False" DataField="AttachmentCategory" SortExpression="AttachmentCategory|Attachment"
                        HeaderText="Category" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Attachment" SortExpression="Attachment|AttachmentCategory"
                        HeaderText="Attachment" />
                    <CC1:MasterControlField ShowReturns="False" DataField="MasterAttachment" SortExpression="MasterPage|Attachment"
                        HeaderText="Master Attachment" />
                    <CC1:MasterControlField Visible="False" ShowReturns="False" DataField="AttachmentCategoryID"
                        HeaderText="AttachmentCategoryID" />
                </GridColumns>
            </CC1:MasterControl>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
</asp:Content>
