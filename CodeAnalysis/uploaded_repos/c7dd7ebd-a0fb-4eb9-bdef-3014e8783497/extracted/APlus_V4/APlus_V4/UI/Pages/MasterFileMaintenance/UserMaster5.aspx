<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserMaster5.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserMaster5"
    Title="User Master Active Directory Conflicts" EnableTheming="true" StylesheetTheme="APlus_Default" %>

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
            <CC1:MasterControl runat="server" ID="MasterControl1" ConnectionString="" RaiseAddEvent="False"
                RaiseExitEvent="False" ShowAdd="False" ShowDelete="False" ShowEdit="True" ShowExit="True"
                ShowExport="True" ShowView="False" StoredProcedureParams="(Collection)" Translate="False"
                Width="100%" DeleteLabel="Delete" EditLabel="Edit" ViewLabel="View" FormName="User Master AD Conflicts"
                NewLinkCaption="User" ProgramMode="UserMasterMode" ProgramName="UserMaster5"
                RedirectProgramName="UserMaster6" AlternatingRows="True" ShowRowCount="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="LastName" HeaderText="Last Name" ShowReturns="False"
                        SortExpression="LastName" />
                    <CC1:MasterControlField DataField="FirstName" HeaderText="First Name" ShowReturns="False"
                        SortExpression="FirstName" />
                    <CC1:MasterControlField DataField="UserID" HeaderText="UserID" ShowReturns="False"
                        SortExpression="UserID" />
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" ShowReturns="False" SortExpression="Site|DeptNumber" />
                    <CC1:MasterControlField DataField="Title" HeaderText="Title" ShowReturns="False"
                        SortExpression="Title" />
                    <CC1:MasterControlField DataField="DeptNumber" HeaderText="Dept" ShowReturns="False"
                        SortExpression="Dept" />
                    <CC1:MasterControlField DataField="Active" HeaderText="Active" ShowReturns="False"
                        SortExpression="Active" />
                    <CC1:MasterControlField DataField="ADConflict" HeaderText="AD User" ShowReturns="False"
                        SortExpression="ADConflict" />
                    <CC1:MasterControlField DataField="ADConflictInformation" HeaderText="Conflict" ShowReturns="False"
                        HtmlEncode="false" />
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
