<%@ Page Language="VB" ValidateRequest="false" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SavingsTrackerImport1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.SavingsTrackerImport1"
    Title="Savings Tracker Data Import" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script language="javascript" type="text/javascript">
        function LoadData() {
            if (document.all.Spreadsheet1.TitleBar != null) {
                if (document.all.ctl00_ContentPlaceHolder1_HTMLData.value != '') {
                    document.all.Spreadsheet1.HTMLData = document.all.ctl00_ContentPlaceHolder1_HTMLData.value;
                    document.all.divspreadsheet.style.visibility = 'visible';
                }
            }
            else {
                document.getElementById("txtObjectError").style.visibility = "visible";
                document.getElementById("divspreadsheet").style.visibility = "hidden";
                document.getElementById("Spreadsheet1").style.height = "25";
                document.getElementById("btnImport").style.visibility = "hidden";
            }
        }

        function ImportFromExcel() {
            document.all.ctl00_ContentPlaceHolder1_HTMLData.value = document.all.Spreadsheet1.HTMLData;
            return true;
        }
    </script>
    <asp:Panel ID="pnlSpreadsheet" runat="server">
        <div id="txtObjectError" style="font-weight: bold; visibility: hidden; color: red">
            <p>
                Microsoft Office Web Components (OWC11) needs to be installed on your PC to use
                this program. This component is normally part of Microsoft Office 2003.</p>
        </div>
        <div id="divspreadsheet" style="visibility: hidden;">
            <div>
                Year :
                <asp:TextBox runat="server" ID="txtYear" CssClass="Textbox_Entry" MaxLength="4" Width="47px"></asp:TextBox></div>
            <br />
            <div style="font-weight: bold; font-size: small; text-align: left">
                Import from Excel</div>
            <br />
            <object id="Spreadsheet1" style="width: 100%; height: 314px" classid="clsid:0002E559-0000-0000-C000-000000000046"
                viewastext>
                <param name="HTMLURL" value="" />
                <param name="HTMLData" value="<html xmlns:x=&quot;urn:schemas-microsoft-com:office:excel&quot;&#13;&#10;xmlns=&quot;http://www.w3.org/TR/REC-html40&quot;>&#13;&#10;&#13;&#10;<head>&#13;&#10;<style type=&quot;text/css&quot;>&#13;&#10;<!--tr&#13;&#10;&#9;{mso-height-source:auto;}&#13;&#10;td&#13;&#10;&#9;{white-space:nowrap;}&#13;&#10;.wcC0E50D31&#13;&#10;&#9;{white-space:nowrap;&#13;&#10;&#9;font-family:Arial;&#13;&#10;&#9;mso-number-format:General;&#13;&#10;&#9;font-size:auto;&#13;&#10;&#9;font-weight:auto;&#13;&#10;&#9;font-style:auto;&#13;&#10;&#9;text-decoration:auto;&#13;&#10;&#9;mso-background-source:auto;&#13;&#10;&#9;mso-pattern:auto;&#13;&#10;&#9;mso-color-source:auto;&#13;&#10;&#9;text-align:general;&#13;&#10;&#9;vertical-align:bottom;&#13;&#10;&#9;border-top:none;&#13;&#10;&#9;border-left:none;&#13;&#10;&#9;border-right:none;&#13;&#10;&#9;border-bottom:none;&#13;&#10;&#9;mso-protection:locked;}&#13;&#10;-->&#13;&#10;</style>&#13;&#10;</head>&#13;&#10;&#13;&#10;<body>&#13;&#10;<!--[if gte mso 9]><xml>&#13;&#10; <x:ExcelWorkbook>&#13;&#10;  <x:ExcelWorksheets>&#13;&#10;   <x:ExcelWorksheet>&#13;&#10;    <x:OWCVersion>9.0.0.6621</x:OWCVersion>&#13;&#10;    <x:Label Style='border-top:solid .5pt silver;border-left:solid .5pt silver;&#13;&#10;     border-right:solid .5pt silver;border-bottom:solid .5pt silver'>&#13;&#10;     <x:Caption>Microsoft Office Spreadsheet</x:Caption>&#13;&#10;    </x:Label>&#13;&#10;    <x:Name>Sheet1</x:Name>&#13;&#10;    <x:WorksheetOptions>&#13;&#10;     <x:Selected/>&#13;&#10;     <x:Height>8308</x:Height>&#13;&#10;     <x:Width>21352</x:Width>&#13;&#10;     <x:TopRowVisible>0</x:TopRowVisible>&#13;&#10;     <x:LeftColumnVisible>0</x:LeftColumnVisible>&#13;&#10;     <x:ProtectContents>False</x:ProtectContents>&#13;&#10;     <x:DefaultRowHeight>255</x:DefaultRowHeight>&#13;&#10;     <x:StandardWidth>2340</x:StandardWidth>&#13;&#10;    </x:WorksheetOptions>&#13;&#10;   </x:ExcelWorksheet>&#13;&#10;  </x:ExcelWorksheets>&#13;&#10;  <x:MaxHeight>80%</x:MaxHeight>&#13;&#10;  <x:MaxWidth>80%</x:MaxWidth>&#13;&#10; </x:ExcelWorkbook>&#13;&#10;</xml><![endif]-->&#13;&#10;&#13;&#10;<table class=wcC0E50D31 x:str>&#13;&#10; <col class=wcC0E50D31 width=&quot;64&quot;>&#13;&#10; <tr height=&quot;17&quot;>&#13;&#10;  <td class=wcC0E50D31></td>&#13;&#10; </tr>&#13;&#10;</table>&#13;&#10;&#13;&#10;</body>&#13;&#10;&#13;&#10;</html>&#13;&#10;" />
                <param name="DataType" value="HTMLDATA" />
                <param name="AutoFit" value="1" />
                <param name="DisplayColHeaders" value="-1" />
                <param name="DisplayGridlines" value="-1" />
                <param name="DisplayHorizontalScrollBar" value="-1" />
                <param name="DisplayRowHeaders" value="-1" />
                <param name="DisplayTitleBar" value="0" />
                <param name="DisplayToolbar" value="-1" />
                <param name="DisplayVerticalScrollBar" value="-1" />
                <param name="EnableAutoCalculate" value="-1" />
                <param name="EnableEvents" value="-1" />
                <param name="MoveAfterReturn" value="-1" />
                <param name="MoveAfterReturnDirection" value="0" />
                <param name="RightToLeft" value="0" />
                <param name="ViewableRange" value="1:65536" />
            </object>
        </div>
        <table id="tbButtons2" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnImport" runat="server" Text="Validate Data" CssClass="Button_Default"
                        EnableViewState="False"></asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" Text="Cancel" CssClass="Button_Default"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlImport" runat="server" Visible="False">
        <div>
            Year :
            <asp:Label runat="server" ID="lblYear"></asp:Label></div>
        <br />
        <asp:GridView ID="grdImport" runat="server" Width="100%" SkinID="GridView" AutoGenerateColumns="False">
            <Columns>
            </Columns>
        </asp:GridView>
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" Text="Load Data" CssClass="Button_Default">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel2" runat="server" Text="Cancel" CssClass="Button_Default"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
    <asp:TextBox ID="HTMLData" Width="0" Height="0" runat="server" BorderStyle="none"
        Style="visibility: hidden"></asp:TextBox>
    <script type="text/javascript" language="javascript">
        LoadData()
    </script>
</asp:Content>
