<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="JobSkillAttachments1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.JobSkillAttachments1"
    Title="Job Skill Documents" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="[spSelJobSkillAttachmentsMaster]"
                ProgramName="JobSkillAttachments1" FormName="Job Skill Attachments" RedirectProgramName="JobSkillAttachments2"
                NewLinkCaption="Job Skill Attachment" ShowView="True" ShowEdit="True" ShowDelete="True"
                ShowAdd="True" ProgramMode="JobSkillAttachmentsMode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="JobSkillID">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="SkillCategory" SortExpression="SkillCategory"
                        HeaderText="Skill Category">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Skill" SortExpression="Skill" HeaderText="Skill">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Attachment" SortExpression="Attachment" HeaderText="Document">
                    </CC1:MasterControlField>
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
