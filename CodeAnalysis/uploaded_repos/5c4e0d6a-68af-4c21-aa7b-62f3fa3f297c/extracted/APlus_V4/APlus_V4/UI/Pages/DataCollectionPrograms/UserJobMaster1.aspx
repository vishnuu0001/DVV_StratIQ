<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserJobMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserJobMaster1"
    Title="User Job Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:UpdateProgress ID="UpdateProgress1" runat="server" DisplayAfter="50" AssociatedUpdatePanelID="UpdatePanel1">
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
            <CC1:MasterControl ID="MasterControl1" runat="server" ProgramMode="UserJobMode" ShowExport="True"
                NewLinkCaption="User Job" ShowAdd="True" ShowDelete="True" ShowEdit="False" ShowView="False"
                RedirectProgramName="UserJobMaster2" FormName="User Job Master" ProgramName="UserJobMaster1"
                CommandText="[spSelUserJobMasterByJob]" DeleteLabel="Remove" FunctionButtonOneLabel="Add All Team Members"
                ShowFunctionButtonOne="True" AlternatingRows="true">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="JobID" HeaderText="JobID" />
                    <CC1:MasterControlField Visible="False" DataField="UserID" HeaderText="UserID" />
                    <CC1:MasterControlField DataField="Job" HeaderText="Job" />
                    <CC1:MasterControlField DataField="UserName" HeaderText="User" />
                    <CC1:MasterControlField DataField="DeptNumber" SortExpression="DeptNumber" HeaderText="Dept" />
                    <CC1:MasterControlField DataField="SkillRating" HeaderText="Skill Rating" />
                    <CC1:MasterControlField DataField="EvaluationDate" HeaderText="Latest Evaluation Date" />
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
