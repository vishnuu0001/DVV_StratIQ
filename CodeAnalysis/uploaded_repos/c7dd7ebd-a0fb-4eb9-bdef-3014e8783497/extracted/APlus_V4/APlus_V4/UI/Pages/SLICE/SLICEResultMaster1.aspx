<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEResultMaster1.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEResultMaster1"
    Title="Slice Result Master" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelSliceResultMaster"
                FormName="Slice Result Master Maintenance" NewLinkCaption="Slice Result" ProgramMode="SLICEResultMasterMode"
                ProgramName="SLICEResultMaster1" RedirectProgramName="SLICEResultMaster2" ShowExport="False"
                AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="SLICEResultID" Visible="False" HeaderText="SLICE Result ID"
                        ShowReturns="False" SortExpression="SLICEResultID" />
                    <CC1:MasterControlField DataField="SLICEResultText" HeaderText="SLICE Result Text"
                        SortExpression="SLICEResultText" ShowReturns="False" />
                    <CC1:MasterControlField DataField="Pass" Visible="False" SortExpression="Pass" HeaderText="Pass" />
                    <CC1:MasterControlField DataField="PresentationSequence" SortExpression="PresentationSequence"
                        HeaderText="Presentation Sequence" />
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
