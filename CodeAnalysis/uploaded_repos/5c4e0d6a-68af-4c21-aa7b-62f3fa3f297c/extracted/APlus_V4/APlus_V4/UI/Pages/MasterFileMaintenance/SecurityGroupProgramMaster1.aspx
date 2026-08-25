<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SecurityGroupProgramMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.SecurityGroupProgramMaster1"
    Title="Security Group Program Master" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelSecurityGroupProgramMaster"
                FormName="Security Group Program Master Maintenance" NewLinkCaption="Security Group Program"
                ProgramMode="SecurityGroupProgramMasterMode" ProgramName="SecurityGroupProgramMaster1"
                RedirectProgramName="SecurityGroupProgramMaster2" AlternatingRows="True" ShowExport="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="SecurityGroupID" HeaderText="SecurityGroupID"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="SecurityGroup" HeaderText="Security Group" ShowReturns="False"
                        SortExpression="SecurityGroup|Program">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Program" HeaderText="Program" ShowReturns="False"
                        SortExpression="Program|SecurityGroup">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowAdd" HeaderText="Allow Add" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowEdit" HeaderText="Allow Edit" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowDelete" HeaderText="Allow Delete" ShowReturns="False">
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
