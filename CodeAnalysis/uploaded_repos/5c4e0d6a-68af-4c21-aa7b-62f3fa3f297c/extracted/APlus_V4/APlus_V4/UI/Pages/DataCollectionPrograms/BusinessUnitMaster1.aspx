<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="BusinessUnitMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.BusinessUnitMaster1"
    Title="Business Unit Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowView="False" ShowAdd="True"
                ShowDelete="True" ShowEdit="True" NewLinkCaption="Business Unit" RedirectProgramName="BusinessUnitMaster2"
                FormName="Business Unit Maintenance" ProgramName="BusinessUnitMaster1" CommandText="spSelBusinessUnitMaster"
                ProgramMode="BusinessUnitMode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="BusinessUnitID" HeaderText="BusinessUnitID" />
                    <CC1:MasterControlField DataField="BusinessUnit" SortExpression="BusinessUnit" HeaderText="Business Unit" />
                    <CC1:MasterControlField DataField="BusinessUnitAbbrev" SortExpression="BusinessUnitAbbrev"
                        HeaderText="Abbreviation" />
                    <CC1:MasterControlField DataField="BusinessArea" SortExpression="BusinessArea" HeaderText="Business Area" />
                    <CC1:MasterControlField DataField="Active" SortExpression="Active" HeaderText="Active" />
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
