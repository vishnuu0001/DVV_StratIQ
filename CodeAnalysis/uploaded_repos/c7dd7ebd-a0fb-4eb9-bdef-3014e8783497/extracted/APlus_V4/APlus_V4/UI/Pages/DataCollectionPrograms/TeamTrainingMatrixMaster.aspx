<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamTrainingMatrixMaster.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamTrainingMatrixMaster"
    Title="My Teams Training Matrices" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelMyTeamsTrainingMatrices"
                ProgramName="TeamTrainingMatrixMaster" FormName="My Teams Training Matrices"
                RedirectProgramName="JobMaster3" NewLinkCaption="Training Matrix" ShowView="True"
                ShowEdit="True" ShowDelete="False" ShowAdd="True" ProgramMode="TrainingMatrixMode"
                RaiseAddEvent="True" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" ShowReturns="False" DataField="JobID" HeaderText="JobID" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Job" SortExpression="Job"
                        HeaderText="Job" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Site" SortExpression="Site"
                        HeaderText="Site" />
                    <CC1:MasterControlField ShowReturns="False" DataField="RatingType" SortExpression="RatingType"
                        HeaderText="Rating Type" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Team" SortExpression="Team"
                        HeaderText="Team" />
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
