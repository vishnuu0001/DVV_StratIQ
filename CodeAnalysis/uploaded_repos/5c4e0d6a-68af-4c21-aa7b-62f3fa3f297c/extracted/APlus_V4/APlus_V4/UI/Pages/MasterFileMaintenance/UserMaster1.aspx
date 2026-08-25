<%@ Page Language="vb" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="~/UI/Pages/MasterFileMaintenance/UserMaster1.aspx.vb"
    Inherits="WebApp.APlus.UI.Pages.UserMaster1" Title="User Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="server"
    Visible="true">
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
            <CC1:MasterControl runat="server" ID="MasterControl1" ConnectionString="" RaiseAddEvent="False"
                RaiseExitEvent="False" ShowAdd="True" ShowDelete="True" ShowEdit="True" ShowExit="True"
                ShowExport="True" ShowView="True" StoredProcedureParams="(Collection)" Translate="False"
                Width="100%" DeleteLabel="Delete" EditLabel="Edit" ViewLabel="View" CommandText="spSelUserMaster"
                FormName="User Master Maintenance" NewLinkCaption="User" ProgramMode="UserMasterMode"
                ProgramName="UserMaster1" RedirectProgramName="UserMaster2" AlternatingRows="True"
                ShowRowCount="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="LastName" HeaderText="Last Name" ShowReturns="False"
                        SortExpression="LastName" />
                    <CC1:MasterControlField DataField="FirstName" HeaderText="First Name" ShowReturns="False"
                        SortExpression="FirstName" />
                    <CC1:MasterControlField DataField="MiddleInitial" HeaderText="Middle" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="UserID" HeaderText="UserID" ShowReturns="False"
                        SortExpression="UserID" />
                    <CC1:MasterControlField DataField="Title" HeaderText="Title" ShowReturns="False" />
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" ShowReturns="False" SortExpression="Site|DeptNumber" />
                    <CC1:MasterControlField DataField="DeptNumber" HeaderText="Dept" ShowReturns="False"
                        SortExpression="DeptNumber" />
                    <CC1:MasterControlField DataField="CultureCode" HeaderText="Culture" ShowReturns="False"
                        SortExpression="CultureCode" />
                    <CC1:MasterControlField DataField="IsAdministrator" HeaderText="Admin" SortExpression="IsAdministrator">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Active" HeaderText="Active" ShowReturns="False"
                        SortExpression="Active" />
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
