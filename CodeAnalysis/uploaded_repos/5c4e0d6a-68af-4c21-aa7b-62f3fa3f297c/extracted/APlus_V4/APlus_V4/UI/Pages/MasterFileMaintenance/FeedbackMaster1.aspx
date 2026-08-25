<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="FeedbackMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.FeedbackMaster1"
    Title="Feedback" %>

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
    <asp:UpdatePanel ID="UpdatePanel1" runat="server" UpdateMode="Conditional">
        <ContentTemplate>
            <table id="Table1">
                <tr>
                    <td style="width: 172px">
                        <asp:CheckBox ID="chkDisplayProcessed" runat="server" Text="Include Processed Feedback"
                            AutoPostBack="true"></asp:CheckBox>
                    </td>
                </tr>
            </table>
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="False" ShowDelete="False"
                ShowView="False" CommandText="spSelFeedbackMaster" FormName="Feedback Master Maintenance"
                ProgramName="FeedbackMasterMaintenance" RedirectProgramName="FeedbackMasterMaintenance"
                AlternatingRows="True" ShowRowCount="True" ShowExport="true">
                <GridColumns>
                    <CC1:MasterControlField DataField="ID" HeaderText="ID" ShowReturns="False" SortExpression="ID">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="CreateDateTime" HeaderText="Date/Time" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Feedback" HeaderText="Feedback" ShowReturns="True"
                        SortExpression="Feedback">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="UserID" HeaderText="UserID" ShowReturns="False"
                        SortExpression="UserID">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Processed" HeaderText="Processed" ShowReturns="False"
                        SortExpression="Processed">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Comments" HeaderText="Comments" ShowReturns="True"
                        SortExpression="Comments">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="FeedbackType" HeaderText="Type" ShowReturns="False"
                        SortExpression="FeedbackTypeID">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="FeedbackPriority" HeaderText="Priority" ShowReturns="False"
                        SortExpression="FeedbackPriorityID">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="DevComments" HeaderText="Dev Comments" ShowReturns="True"
                        SortExpression="DevComments">
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
