<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEActivityGroupMaster1.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityGroupMaster1"
    Title="SLICE Activity Group Master" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelSLICEActivityGroupMaster"
                FormName="SLICE Activity Group Master" NewLinkCaption="Checksheet Template" ProgramMode="SLICEActivityGroupMasterMode"
                ProgramName="SLICEActivityGroupMaster1" RedirectProgramName="SLICEActivityGroupMaster2"
                ShowExport="False" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="SLICEActivityGroupID" SortExpression="SLICEActivityGroupID"
                        HeaderText="Template" Visible="False" />
                    <CC1:MasterControlField DataField="SLICEActivityGroup" SortExpression="SLICEActivityGroup"
                        HeaderText="Checksheet" />
                    <CC1:MasterControlField DataField="SLICEActivityGroupDescription" SortExpression="SLICEActivityGroupDescription"
                        Visible="True" HeaderText="Template Description" />
                    <CC1:MasterControlField DataField="Workcenter" SortExpression="Workcenter" HeaderText="Workcenter" />
                    <CC1:MasterControlField ShowReturns="False" DataField="WorkcenterID" SortExpression="WorkcenterID"
                        HeaderText="Workcenter ID" />
                    <CC1:MasterControlField ShowReturns="True" DataField="DistinctFreq" SortExpression="DistinctFreq"
                        HeaderText="Frequency" />
                    <CC1:MasterControlField ShowReturns="True" DataField="DistinctPos" SortExpression="DistinctPos"
                        HeaderText="Position" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TargetDeviation" Visible="False"
                        SortExpression="TargetDeviation" HeaderText="Target Deviation" />
                    <CC1:MasterControlField ShowReturns="False" DataField="ActivityCount" SortExpression="ActivityCount"
                        HeaderText="Activities" />
                    <CC1:MasterControlField ShowReturns="False" DataField="TargetTime" SortExpression="TargetTime"
                        HeaderText="Target" />
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
