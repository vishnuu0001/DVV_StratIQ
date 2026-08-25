<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyCauses2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyCauses2"
    Title="Anomaly Causes" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC2" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <CC2:MasterControl ID="mcAnomaly" runat="server" ShowAdd="false" ShowDelete="false"
        Translate="true" ShowView="false" ShowEdit="false" NewLinkCaption="Anomaly" RedirectProgramName="AnomalyMaster2"
        FormName="Anomaly Maintenance" ProgramName="AnomalyMaster1" CommandText="spSelAnomalyMasterByID"
        ProgramMode="AnomalyMode" AlternatingRows="True" PrimaryControl="false">
        <GridColumns>
            <CC2:MasterControlField DataField="AnomalyID" HeaderText="ID" />
            <CC2:MasterControlField DataField="Site" HeaderText="Site" />
            <CC2:MasterControlField DataField="AnomalyType" HeaderText="Type" />
            <CC2:MasterControlField DataField="Anomaly" HeaderText="Anomaly" />
            <CC2:MasterControlField DataField="Subject" HeaderText="Description" />
            <CC2:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
            <CC2:MasterControlField DataField="Observations" HeaderText="Observations" />
            <CC2:MasterControlField DataField="ClosedDateTime" HeaderText="Closed" />
            <CC2:MasterControlField DataField="CreatedUser" HeaderText="Created By" />
            <CC2:MasterControlField DataField="CreatedDateTime" HeaderText="Created" />
        </GridColumns>
    </CC2:MasterControl>
    <hr width="100%" />
    <table class="Table_Default" id="Table1">
        <tr>
            <td>
                <asp:Label ID="lblAnomalyCauseID" runat="server" Text="Anomaly Cause ID:" CssClass="Label_Left_8PT"
                    Visible="False"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAnomalyCauseID" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="31px" ReadOnly="True" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblAnomalyCause" runat="server" Text="Anomaly Cause:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandAnomalyCause" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="350px" Height="28px" TextMode="MultiLine"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAnomalyCause" runat="server" ErrorMessage="Enter Anomaly Cause"
                    ControlToValidate="txtExpandAnomalyCause" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 175px">
                <asp:Label ID="lblAnalysis" runat="server" Text="Analysis Comprehensiveness:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandAnalysis" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="350px" Height="28px" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
