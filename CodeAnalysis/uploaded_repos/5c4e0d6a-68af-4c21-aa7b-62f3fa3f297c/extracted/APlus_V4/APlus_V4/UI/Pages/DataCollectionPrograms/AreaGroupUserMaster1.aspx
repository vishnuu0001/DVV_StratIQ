<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AreaGroupUserMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AreaGroupUserMaster1"
    Title="Area User Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelAreaGroupUserMasterBySite"
                FormName="Area User Master" NewLinkCaption="Area User" ProgramMode="Mode" ProgramName="AreaGroupUserMaster1"
                RedirectProgramName="AreaGroupUserMaster2" ShowEdit="True" ShowExport="True"
                Translate="True" AlternatingRows="True" ShowView="false" ShowDelete="true" ShowAdd="true">
                <GridColumns>
                    <CC1:MasterControlField DataField="AreaGroupID" HeaderText="AreaGroupID" Visible="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="UserID" HeaderText="User ID" Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AreaGroup" HeaderText="Area" ShowReturns="False"
                        SortExpression="AreaGroup">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="UserName" HeaderText="User" ShowReturns="False"
                        SortExpression="UserName">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowAnomalyEvaluate" HeaderText="Evaluate Anomaly"
                        SortExpression="AllowAnomalyEvaluate">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowAnomalyEdit" HeaderText="Edit Anomaly" SortExpression="AllowAnomalyEdit">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowKPIView" HeaderText=" KPI View" SortExpression="AllowKPIView">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowKPIEdit" HeaderText="KPI Edit" SortExpression="AllowKPIEdit">
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
