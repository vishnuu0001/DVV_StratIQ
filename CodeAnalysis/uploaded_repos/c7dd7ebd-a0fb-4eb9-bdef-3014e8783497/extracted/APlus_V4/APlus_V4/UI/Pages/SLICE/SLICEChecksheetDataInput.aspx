<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEChecksheetDataInput.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEChecksheetDataInput"
    Title="SLICE Checksheet Data Input Page" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>

    <script type="text/javascript" language="javascript">
        $(document).ready(function() {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>

    <script type="text/javascript" language="javascript">

        function checkAllYesRadioButtons() {
            $("input[id$='_rdoResults_0']").attr('checked', true);
        }

        function checkAllNoRadioButtons() {
            $("input[id$='_rdoResults_1']").attr('checked', true);
        }

        function ClearControlsInRow(intX) {
            $("input[id$='" + intX + "_rdoResults_0']").attr('checked', false);
            $("input[id$='" + intX + "_rdoResults_1']").attr('checked', false);
            $("textarea[id$='" + intX + "_txtComments']").val('');
            $("input[id$='" + intX + "_txtWorkorderNum']").val('');
            $("input[id$='" + intX + "_txtElapsedTime']").val('');
        }

        function checkForComments() {
            var grid;
            var i = 2;

            grid = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput');

            if (grid != null) {
                var len = i.toString().length
                if (len == 1) { i = '0' + i.toString(); }

                var objRdo = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput_ctl' + i + '_rdoResults_1');
                while (objRdo != null) {
                    if (!objRdo.disabled) {
                        if (objRdo.checked) {

                            if (document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput:_ctl' + i + '_txtExpandComments').innerText.length == 0) {
                                alert("Comments required when desired condition not met!");
                                return false;
                            }
                        }
                    }

                    i++;
                    var len = i.toString().length
                    if (len == 1) { i = '0' + i.toString(); }

                    objRdo = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput_ctl' + i + '_rdoResults_1');
                }
            }

            return true;
        }

        function CheckForElapsedTimeInput() {
            var objTxtETime;
            var objTxtETime2;

            var bTxtBox1Empty = false;
            var bTxtBox2Empty = false;
            var bResult = true;

            var grid;
            var i = 2;

            grid = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput');

            if (grid != null) {
                var len = i.toString().length
                if (len == 1) { i = '0' + i.toString(); }

                objTxtETime = document.getElementById('ctl00_ContentPlaceHolder1_txtEnterElapsedTime');
                var objRdoYes = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput_ctl' + i + '_rdoResults_0');
                var objRdoNo = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput_ctl' + i + '_rdoResults_1');

                if (objTxtETime != null) {
                    if (document.Form1.txtEnterElapsedTime.value.length < 1) {
                        bTxtBox1Empty = true;
                    }
                }

                objTxtETime2 = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput:_ctl' + i + '_txtElapsedTime');

                while (objTxtETime2 != null) {
                    if (!objTxtETime2.disabled) {
                        if (objRdoYes.checked || objRdoNo.checked) {
                            if (objTxtETime2.value.length < 1) {
                                bTxtBox2Empty = true;
                                break;
                            }
                        }
                    }

                    i++;
                    var len = i.toString().length
                    if (len == 1) { i = '0' + i.toString(); }

                    objTxtETime2 = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput:_ctl' + i + '_txtElapsedTime');
                    objRdoYes = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput_ctl' + i + '_rdoResults_0');
                    objRdoNo = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput_ctl' + i + '_rdoResults_1');

                }

                if (bTxtBox1Empty && bTxtBox2Empty) {
                    bResult = false;
                    alert("Please enter Elapsed Time before submitting form!");
                }

                return bResult;

            }
        }

        // allow only main textbox for elapsed time
        // OR the dynamic textboxes...but not both!
        function CheckElapsedTimeInputFields() {
            var bResult = true;
            var grid;
            var i = 2;

            grid = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput');

            if (grid != null) {
                objTxtETime = document.getElementById('ctl00_ContentPlaceHolder1_txtEnterElapsedTime');

                if (objTxtETime.value.length > 0) {
                    var len = i.toString().length
                    if (len == 1) { i = '0' + i.toString(); }

                    objTxtETime = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput:_ctl' + i + '_txtElapsedTime');

                    while (objTxtETime != null) {
                        if (!objTxtETime.disabled) {

                            if (objTxtETime.value.length > 0) {
                                bResult = false;
                                alert("Enter Elapsed Time as total elapsed time OR by row!");
                                break;
                            }
                        }

                        i++;
                        var len = i.toString().length
                        if (len == 1) { i = '0' + i.toString(); }

                        objTxtETime = document.getElementById('ctl00_ContentPlaceHolder1_grdChecksheetDataInput:_ctl' + i + '_txtElapsedTime');
                    }
                }
            }

            return bResult;
        }

        function CheckRequiredFieldsOnForm() {
            if (CheckForElapsedTimeInput() && CheckElapsedTimeInputFields() && checkForComments()) {
                return confirm("Are you sure you are ready to save data?");
            }
            else {
                return false;
            }
        }
    </script>

    <div align="center">
        <asp:Label ID="lblShowSAPEntity" runat="server" Font-Bold="True" Font-Names="Verdana"
            Font-Size="20px">Checksheet ID: </asp:Label></div>
    <table id="Table1" cellspacing="1" cellpadding="1" width="100%" border="0">
        <tr>
            <td>
                <asp:Label ID="lblChkId" runat="server" Font-Bold="True" Font-Names="Verdana">Checksheet ID: </asp:Label><asp:Label
                    ID="lblShowChecksheetId" runat="server" Font-Bold="True" Font-Names="Verdana"></asp:Label>
            </td>
            <td>
                <asp:Label ID="lblStatus" runat="server" Font-Bold="True" Font-Names="Verdana">Status: </asp:Label><asp:Label
                    ID="lblShowStatus" runat="server" Font-Bold="True" Font-Names="Verdana"></asp:Label>
            </td>
            <td>
                <asp:Label ID="lblReleaseDate" runat="server" Font-Bold="True" Font-Names="Verdana">Release Date: </asp:Label><asp:Label
                    ID="lblShowReleaseDate" runat="server" Font-Bold="True" Font-Names="Verdana"></asp:Label>
            </td>
            <td>
                <asp:Label ID="lblDueDate" runat="server" Font-Bold="True" Font-Names="Verdana">Due Date: </asp:Label><asp:Label
                    ID="lblShowDueDate" runat="server" Font-Bold="True" Font-Names="Verdana"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="height: 18px">
                <asp:Label ID="lblTargetTime" runat="server" Font-Bold="True" Font-Names="Verdana">Target Time: </asp:Label><asp:Label
                    ID="lblShowTargetTime" runat="server" Font-Bold="True" Font-Names="Verdana"></asp:Label>
            </td>
            <td style="height: 18px">
                <asp:Label ID="lblElapsedTime" runat="server" Font-Bold="True" Font-Names="Verdana">Elapsed Time: </asp:Label><asp:Label
                    ID="lblDisplayElapsedTime" runat="server" Font-Bold="True" Font-Names="Verdana"></asp:Label>
            </td>
            <td style="height: 18px">
                &nbsp;
            </td>
            <td style="height: 18px">
                &nbsp;
            </td>
        </tr>
        <tr>
            <td>
            </td>
            <td>
            </td>
            <td>
            </td>
            <td>
            </td>
        </tr>
    </table>
    <br />
    <asp:Label ID="lblDbUpdateInfoTop" runat="server">Db Import Info Here</asp:Label><br>
    <br />
    <asp:Panel ID="pnlSetRadioBtnsTop" runat="server" Visible="True" Width="100%">
        &nbsp;
        <table id="Table2" cellspacing="1" cellpadding="1" width="100%" border="0">
            <tr>
                <td class="style1">
                    <input runat="server" class="Button_Default" id="btnAllConditionMet" style="width: 104px;
                        height: 18px" onclick="checkAllYesRadioButtons();" type="button" value="All Conditions Met" />
                </td>
                <td>
                    <input runat="server" class="Button_Default" id="btnAllConditionNotMet" style="width: 110px;
                        height: 18px" onclick="checkAllNoRadioButtons();" type="button" value="All Conditions Not Met" />
                </td>
                <td align="right" style="width: 706px">
                    <asp:Label ID="lblEnterElapsedTime" runat="server" Font-Names="Verdana" Font-Bold="True"
                        Text="Enter Elapsed Time:"></asp:Label>
                    <asp:TextBox ID="txtEnterElapsedTime" runat="server" Width="60px" CssClass="Textbox_Entry"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <p>
    </p>
    <asp:DataGrid ID="grdChecksheetDataInput" runat="server" Width="100%" OnItemCommand="dgItemCommand"
        BorderStyle="None" AutoGenerateColumns="False" GridLines="Vertical" CellPadding="3"
        BorderColor="#999999" SkinID="DataGrid">
        <FooterStyle ForeColor="Black" BackColor="#CCCCCC"></FooterStyle>
        <AlternatingItemStyle BackColor="Gainsboro"></AlternatingItemStyle>
        <ItemStyle Height="20px" ForeColor="Black" BackColor="#EEEEEE"></ItemStyle>
        <HeaderStyle Font-Bold="True" ForeColor="White" BackColor="#41519A"></HeaderStyle>
        <Columns>
            <asp:BoundColumn DataField="PresentationSequence" HeaderText="Seq"></asp:BoundColumn>
            <asp:BoundColumn DataField="SAPEntity" HeaderText="Entity #"></asp:BoundColumn>
            <asp:BoundColumn DataField="CoLoc" HeaderText="Component/Location"></asp:BoundColumn>
            <asp:BoundColumn DataField="Position" HeaderText="Pos"></asp:BoundColumn>
            <asp:BoundColumn DataField="Type" HeaderText="Type"></asp:BoundColumn>
            <asp:BoundColumn DataField="DesiredCondition" HeaderText="Desired Condition"></asp:BoundColumn>
            <asp:TemplateColumn HeaderText="Meets Desired Condition">
                <ItemTemplate>
                    <asp:RadioButtonList ID="rdoResults" runat="server" RepeatDirection="Horizontal">
                        <asp:ListItem Value="1">Yes&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</asp:ListItem>
                        <asp:ListItem Value="2">No</asp:ListItem>
                    </asp:RadioButtonList>
                </ItemTemplate>
            </asp:TemplateColumn>
            <asp:TemplateColumn HeaderText="Elapsed Time">
                <ItemTemplate>
                    <asp:TextBox runat="server" ID="txtElapsedTime" CssClass="Textbox_Entry" Width="50"></asp:TextBox>
                </ItemTemplate>
            </asp:TemplateColumn>
            <asp:TemplateColumn HeaderText="Comments">
                <ItemTemplate>
                    <asp:TextBox ID="txtExpandComments" TextMode="MultiLine" runat="server" Text='' CssClass='Textbox_Entry'></asp:TextBox>
                    <br>
                    <asp:Label ID="lblWorkOrderNum" runat="server">Workorder #</asp:Label>
                    <asp:TextBox ID="txtWorkorderNum" runat="server" Width="85" CssClass="Textbox_Entry"></asp:TextBox>
                </ItemTemplate>
            </asp:TemplateColumn>
            <asp:TemplateColumn>
                <ItemTemplate>
                    <asp:LinkButton ID="lbtnEditClear" CommandName="Edit" runat="server" Text="Edit"
                        CssClass="Link_Default">
                    </asp:LinkButton>
                    <asp:HyperLink ID="lnkClear" runat="server" NavigateUrl="" Text="Clear" CssClass="Link_Default"></asp:HyperLink>
                </ItemTemplate>
            </asp:TemplateColumn>
            <asp:BoundColumn Visible="False" DataField="SLICEActivityID" HeaderText="SLICEActivityID">
            </asp:BoundColumn>
            <asp:BoundColumn Visible="False" DataField="SLICEChecksheetActivityID" HeaderText="SLICEChecksheetActivityID">
            </asp:BoundColumn>
            <asp:BoundColumn Visible="False" DataField="TargetTime" HeaderText="Target Time">
            </asp:BoundColumn>
        </Columns>
    </asp:DataGrid><asp:Panel ID="pnlSetRadioBtnsBottom" runat="server" Visible="True">
        <table>
            <tr>
                <td class="style2">
                    <input runat="server" class="Button_Default" id="btnAllConditionMet2" style="width: 104px;
                        height: 18px" onclick="checkAllYesRadioButtons();" type="button" value="All Conditions Met" />
                </td>
                <td>
                    <input runat="server" class="Button_Default" id="btnAllConditionNotMet2" style="width: 110px;
                        height: 18px" onclick="checkAllNoRadioButtons();" type="button" value="All Conditions Not Met" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <br />
    <table>
        <tr>
            <td class="style2">
                <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
            </td>
            <td class="style2">
                <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel">
                </asp:Button>
            </td>
        </tr>
    </table>
    <br />
    <asp:Label ID="lblDbUpdateInfo" runat="server" Text="Db Import Info Here"></asp:Label>
    <p>
    </p>
</asp:Content>
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 148px;
        }
        .style2
        {
            width: 150px;
        }
    </style>
</asp:Content>
