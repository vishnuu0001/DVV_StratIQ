#Region " Imports"
Imports System.Collections.Generic
Imports System.Globalization
#End Region

Namespace WebApp.APlus
    Public NotInheritable Class SessionManager

#Region "Enums"
        ' This enum is used to determine which events are written to the eventlog for tracking and debugging purposes.
        ' Simply add up the numbers to the right of the flag that you want to trap and this number gets put in the
        ' "EventTrackerLevel" web.config setting
        ' NOTICE that there is no setting for exceptions - this is because there is NO validation on the exceptions
        ' they are ALWAYS written to the eventlog
        '
        ' 2009.06.01
        ' COB - DJ
        <Flags()> _
        Public Enum EventTrackerLevels As Int32
            Login = 1
            Menu = 2
            DAMasterFile = 4
            DATeams = 8
            DASlice = 16
            DATraining = 32
            UIMasterFile = 64
            UITeams = 128
            UISlice = 256
            UITraining = 512
        End Enum

        Enum SessionVariables
            '==========================================================================================
            ' Here are all the session variables used in the application
            '==========================================================================================
            AllowMaintenance

            ADEmail
            ADFirstName
            ADLastName
            ADMiddleInitial
            ADUserID
            ADConflictRequestsSortdirection
            ADConflictRequestsSortfield
            AllowMaintenanceAdd
            AllowMaintenanceEdit
            AllowMaintenanceDelete
            AnomalyActionMode
            AnomalyCauseMode
            AnomalyMasterFilterAnomalyID
            AnomalyMasterFilterStatus
            AnomalyMasterFilterSearch
            AnomalyMode
            AreaGroupAreaMasterMode
            AreaGroupMasterMode
            AreaMaintenanceMode
            AttachmentJobSkillID
            AttachmentSkill
            AttachmentSkillCategory
            AttachmentsMode
            AttachmentType
            AttachmentTypeID
            Attribute1
            Attribute2
            Attribute3
            Attribute4
            Attribute5
            Attribute6
            Authenticated
            BusinessAreaMode
            BusinessUnitMode
            CalendarEventsMode
            CalendarEventsSelectedID
            CallingMode
            CallingProgram
            CallingProgram2
            ChartHeight
            ChartOPI
            ChartTeamID
            ChartTitle
            ChartType
            ChartWidth
            CloseOnLogout
            ConnectionError
            CultureMasterMode
            CulturePref
            CultureTranslationMode
            CurrentMenuProgram
            CurrentProgram
            CurrentProgramURL
            DataElementMode
            DateFormat
            DateTimeFormat
            DefaultWorkCenter
            DetailChart
            DisplayClosedTeams
            DisplayClosedTeamActions
            EditMode
            EntityFilterWorkcenterID
            EntityFilterEntity
            EntityFilterLocation
            EntityMasterMode
            EnvSelEditMonth
            EnvSelNavYear
            EventLogEmailAddressMasterMode
            EventLogTypeMode
            EventTrackerLevel
            ExpandedTeamKPIs
            ExportString
            FeedbackMode
            FXRateElementMode
            FXRateMode
            HeaderMessage
            HelpAttachmentMode
            IsAdministrator
            JobMode
            JobSkillAttachmentsMode
            JobSkillMode
            KPIDataEntryDaily
            KPIDataEntryMode
            KPIMasterMode
            KPIReportFilterBusinessAreaID
            KPIReportFilterReportID
            KPIReportFilterSiteID
            KPISelEditMode
            KPISelNavMonth
            KPISelNavYear
            KPITeamMasterMode
            LastPixelPosition
            LocationMode
            LookupRoomItem
            MasterControlExitProgram
            MasterControlExitProgram2
            MeetingDate
            MeetingTime
            MenuActioncoordinates
            MenuMode
            MenuOptionMode
            MenuProgramGroupMode
            MetricTargetMode
            Mode
            MyTeamKPIsShowClosed
            NetworkLogin
            OEEReportsMode
            OPIEntrySelectedValue
            OPIEntrySelectedValue1
            OPIMode
            OPIUOM
            Origin1Mode
            Origin2Mode
            Origin3Mode
            OverviewSortColumn
            PillarMasterMode
            PillarMembershipMode
            PopupAttachmentMode
            PositionMasterMode
            ProgramMasterMode
            QueryFrom
            QueryGroupBy
            QueryMasterMode
            QueryOrderBy
            QueryParameterMasterMode
            QuerySelect
            QueryWhere
            RatingScale
            RecordTransactionCurrentValues
            RedirectProgram
            RoleMasterMode
            RoomMasterMode
            RoomReservations
            RoomReservationsMode
            RoutesMode
            RoutesStepsMode
            RouteStepsKeyActionsMode
            RouteStepsKeyActionsToolsMode
            SavedProgram
            SavedSortOrders
            SavingsTrackerMode
            ScanMode
            SecondaryProgram
            SecurityGroupMasterMode
            SecurityGroupProgramMasterMode
            SelectedCultureCode
            SelectedCultureValue
            SelectedJobName
            SelectedKeyActionNo
            SelectedKeyActionToolID
            SelectedKPIReportGroupID
            SelectedMetricID
            SelectedNewMachine
            SelectedOPI
            SelectedOPIDate
            SelectedPalletPrinter
            SelectedQuery
            SelectedQueryName
            SelectedRollPrinter
            SelectedRoute
            SelectedRouteStepNo
            SelectedSite
            SelectedSiteGroup
            SelectedSiteGroupID
            SelectedSiteID
            SelectedSLICEActivityLinksID
            SelectedTargetDate
            SelectedTeamID
            SelectedTeam
            SelectedTeamName
            SelectedTeamAllowEdit
            SelectedValue
            SelectedValue1
            SelectedValue2
            SelectedValue3
            SelectedValue4
            SelectedValueActivityID
            SelectedValueAnomalyID
            SelectedValueAnomalyActionID
            SelectedValueAnomalyCauseID
            SelectedValueAreaGroupID
            SelectedValueAttachment
            SelectedValueAttachmentID
            SelectedValueBusinessAreaID
            SelectedValueBusinessUnitID
            SelectedValueCategory
            SelectedValueCategoryID
            SelectedValueCategoryTypeID
            SelectedValueCheckSheetID
            SelectedValueDataElement
            SelectedValueDate
            SelectedValueDateTime
            SelectedValueDescription
            SelectedValueEntityID
            SelectedValueEventDate
            SelectedValueFXRateID
            SelectedValueFXRatePeriod
            SelectedValueJob
            SelectedValueJobName
            SelectedValueJobSkillID
            SelectedValueKPIID
            SelectedValueLabelFormat
            SelectedValueLabelGroup
            SelectedValueLocation
            SelectedValueMenu
            SelectedValueOption
            SelectedValueOptionMenu
            SelectedValueOrigin1ID
            SelectedValueOrigin2ID
            SelectedValueOrigin3ID
            SelectedValuePositionID
            SelectedValueProgram
            SelectedValueProgramGroup
            SelectedValueProgramGroupMenu
            SelectedValueQueryID
            SelectedValueReservationID
            SelectedValueRoomID
            SelectedValueSite
            SelectedValueSiteID
            SelectedValueSliceActivityGroupID
            SelectedValueSLICEActivityID
            SelectedValueSLICEFrequency
            SelectedValueSLICEFrequencyID
            SelectedValueSLICEResultID
            SelectedValueSLICEType
            SelectedValueSLICETypeID
            SelectedValueSupplier
            SelectedValueTeamID
            SelectedValueTeam
            SelectedValueTeamSiteID
            SelectedValueTrackerCollectionID
            SelectedValueTrackerID
            SelectedValueTrackerPlanID
            SelectedValueTrackerPlanSavingsID
            SelectedValueTrackerTypeID
            SelectedValueUser
            SelectedValueUserJobUser
            SelectedValueWorkcenterID
            SelectedWorkCenter
            SelectedWorkcenterID
            ShowAllMenuOptions
            ShowAttachments
            ShowAttendance
            ShowCriteria
            ShowMenuOptionNumbers
            ShowPopups
            ShowProjected
            ShowValues
            SiteGroupSelectionRequired
            SiteMasterMode
            SiteSelectionRequired
            SkillCategoryMode
            SLICEActivityGroupMasterID
            SLICEActivityGroupMasterMode
            SLICEActivityID
            SLICEActivityLinkMasterMode
            SLICEActivityMaster1
            SLICEActivityMasterMode
            SLICEActivityResults
            SLICEChecksheetActivityID
            SLICEChecksheetMasterMode
            SLICEFrequencyMasterMode
            SLICEResultMasterMode
            SLICETypeMasterMode
            TeamActionPlanMode
            TeamBoardMenuDefaultsMode
            TeamBoardMenuOptionMasterMode
            TeamKPIMode
            TeamLogMode
            TeamMeetingAttendanceMode
            TeamMeetingEmailDateTime
            TeamMeetingEmailFrom
            TeamMeetingID
            TeamMeetingNewAgenda
            TeamMeetingNewDate
            TeamMeetingsMode
            TeamMembershipMode
            TeamOPIControlLimitsMode
            TeamOPIEventMode
            TeamOPIValueMode
            TeamOPIValueID
            TeamsMode
            TeamStack
            TeamStatusMode
            TeamUsersMode
            TemplateAttachmentMode
            TrackerCollectionMode
            TrackerMode
            TrackerPlanMode
            TrackerPlanSavingsMode
            TrackerSelEditMode
            TrackerSelEditMonth
            TrackerSelNavYear
            TrackerSelSiteID
            TrackerTypeMode
            TrackerVariableMode
            TrainingAttachmentMode
            UserADMode
            UserID
            UserITMode
            UserJobMode
            UserJobSortOrder
            UserMasterMode
            UserName
            UserSecurityGroupMasterMode
            UserSkillRatingsMode
            UserSiteMasterMode
            UserWorkCenterGroupMasterMode
            WhiteChart
            WorkCenterControlMasterMode
            WorkCenterGroupMasterMode
            WorkCenterGroupWorkCenterMasterMode
            WorkcenterMasterMode
            WorkCenterOvertaken
            WorkCenterOvertakenMessage
            WorkingSite
            WorkingSiteID
        End Enum
#End Region

#Region "Properties"
        Private Shared ReadOnly Property Session() As HttpSessionState
            Get
                Return HttpContext.Current.Session
            End Get
        End Property
        Public Shared ReadOnly Property Exists() As Boolean
            Get
                Return Not Session Is Nothing
            End Get
        End Property
        Public Shared Property EventTrackerLevel() As EventTrackerLevels
            Get
                If Session(SessionVariables.EventTrackerLevel.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EventTrackerLevel.ToString)
                Else
                    Return New EventTrackerLevels
                End If
            End Get
            Set(ByVal value As EventTrackerLevels)
                Session(SessionVariables.EventTrackerLevel.ToString) = value
            End Set
        End Property
        Public Shared Function CheckEventTrackerLevel(ByVal passLevel As EventTrackerLevels) As Boolean
            Return (passLevel = (passLevel And Session(SessionVariables.EventTrackerLevel.ToString)))
        End Function
        Public Shared Property ADEmail() As String
            Get
                If Session(SessionVariables.ADEmail.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ADEmail.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ADEmail.ToString) = value
            End Set
        End Property
        Public Shared Property ADFirstName() As String
            Get
                If Session(SessionVariables.ADFirstName.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ADFirstName.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ADFirstName.ToString) = value
            End Set
        End Property
        Public Shared Property ADLastName() As String
            Get
                If Session(SessionVariables.ADLastName.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ADLastName.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ADLastName.ToString) = value
            End Set
        End Property
        Public Shared Property ADMiddleInitial() As String
            Get
                If Session(SessionVariables.ADMiddleInitial.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ADMiddleInitial.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ADMiddleInitial.ToString) = value
            End Set
        End Property
        Public Shared Property ADUserID() As String
            Get
                If Session(SessionVariables.ADUserID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ADUserID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ADUserID.ToString) = value
            End Set
        End Property
        Public Shared Property ADConflictRequestsSortdirection() As String
            Get
                If Session(SessionVariables.ADConflictRequestsSortdirection.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ADConflictRequestsSortdirection.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ADConflictRequestsSortdirection.ToString) = value
            End Set
        End Property
        Public Shared Property ADConflictRequestsSortfield() As String
            Get
                If Session(SessionVariables.ADConflictRequestsSortfield.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ADConflictRequestsSortfield.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ADConflictRequestsSortfield.ToString) = value
            End Set
        End Property
        Public Shared Property AllowMaintenanceAdd() As Boolean
            Get
                If Session(SessionVariables.AllowMaintenanceAdd.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AllowMaintenanceAdd.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.AllowMaintenanceAdd.ToString) = value
            End Set
        End Property
        Public Shared Property AllowMaintenanceEdit() As Boolean
            Get
                If Session(SessionVariables.AllowMaintenanceEdit.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AllowMaintenanceEdit.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.AllowMaintenanceEdit.ToString) = value
            End Set
        End Property
        Public Shared Property AllowMaintenanceDelete() As Boolean
            Get
                If Session(SessionVariables.AllowMaintenanceDelete.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AllowMaintenanceDelete.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.AllowMaintenanceDelete.ToString) = value
            End Set
        End Property
        Public Shared Property AnomalyActionMode() As String
            Get
                If Session(SessionVariables.AnomalyActionMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AnomalyActionMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AnomalyActionMode.ToString) = value
            End Set
        End Property
        Public Shared Property AnomalyCauseMode() As String
            Get
                If Session(SessionVariables.AnomalyCauseMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AnomalyCauseMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AnomalyCauseMode.ToString) = value
            End Set
        End Property
        Public Shared Property AnomalyMasterFilterAnomalyID() As Integer
            Get
                If Session(SessionVariables.AnomalyMasterFilterAnomalyID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AnomalyMasterFilterAnomalyID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.AnomalyMasterFilterAnomalyID.ToString) = value
            End Set
        End Property
        Public Shared Property AnomalyMasterFilterStatus() As String
            Get
                If Session(SessionVariables.AnomalyMasterFilterStatus.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AnomalyMasterFilterStatus.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AnomalyMasterFilterStatus.ToString) = value
            End Set
        End Property
        Public Shared Property AnomalyMasterFilterSearch() As String
            Get
                If Session(SessionVariables.AnomalyMasterFilterSearch.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AnomalyMasterFilterSearch.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AnomalyMasterFilterSearch.ToString) = value
            End Set
        End Property
        Public Shared Property AnomalyMode() As String
            Get
                If Session(SessionVariables.AnomalyMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AnomalyMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AnomalyMode.ToString) = value
            End Set
        End Property
        Public Shared Property AreaGroupAreaMasterMode() As String
            Get
                If Session(SessionVariables.AreaGroupAreaMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AreaGroupAreaMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AreaGroupAreaMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property AreaGroupMasterMode() As String
            Get
                If Session(SessionVariables.AreaGroupMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AreaGroupMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AreaGroupMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property AreaMaintenanceMode() As String
            Get
                If Session(SessionVariables.AreaMaintenanceMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AreaMaintenanceMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AreaMaintenanceMode.ToString) = value
            End Set
        End Property
        Public Shared Property AttachmentJobSkillID() As Integer
            Get
                If Session(SessionVariables.AttachmentJobSkillID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AttachmentJobSkillID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.AttachmentJobSkillID.ToString) = value
            End Set
        End Property
        Public Shared Property AttachmentSkill() As String
            Get
                If Session(SessionVariables.AttachmentSkill.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AttachmentSkill.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AttachmentSkill.ToString) = value
            End Set
        End Property
        Public Shared Property AttachmentSkillCategory() As String
            Get
                If Session(SessionVariables.AttachmentSkillCategory.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AttachmentSkillCategory.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AttachmentSkillCategory.ToString) = value
            End Set
        End Property
        Public Shared Property AttachmentsMode() As String
            Get
                If Session(SessionVariables.AttachmentsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AttachmentsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AttachmentsMode.ToString) = value
            End Set
        End Property
        Public Shared Property AttachmentType() As String
            Get
                If Session(SessionVariables.AttachmentType.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AttachmentType.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AttachmentType.ToString) = value
            End Set
        End Property
        Public Shared Property AttachmentTypeID() As String
            Get
                If Session(SessionVariables.AttachmentTypeID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.AttachmentTypeID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.AttachmentTypeID.ToString) = value
            End Set
        End Property
        Public Shared Property Attribute1() As String
            Get
                If Session(SessionVariables.Attribute1.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Attribute1.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Attribute1.ToString) = value
            End Set
        End Property
        Public Shared Property Attribute2() As String
            Get
                If Session(SessionVariables.Attribute2.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Attribute2.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Attribute2.ToString) = value
            End Set
        End Property
        Public Shared Property Attribute3() As String
            Get
                If Session(SessionVariables.Attribute3.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Attribute3.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Attribute3.ToString) = value
            End Set
        End Property
        Public Shared Property Attribute4() As String
            Get
                If Session(SessionVariables.Attribute4.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Attribute4.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Attribute4.ToString) = value
            End Set
        End Property
        Public Shared Property Attribute5() As String
            Get
                If Session(SessionVariables.Attribute5.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Attribute5.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Attribute5.ToString) = value
            End Set
        End Property
        Public Shared Property Attribute6() As String
            Get
                If Session(SessionVariables.Attribute6.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Attribute6.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Attribute6.ToString) = value
            End Set
        End Property
        Public Shared Property Authenticated() As Boolean
            Get
                If Session(SessionVariables.Authenticated.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Authenticated.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.Authenticated.ToString) = value
            End Set
        End Property
        Public Shared Property BusinessAreaMode() As String
            Get
                If Session(SessionVariables.BusinessAreaMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.BusinessAreaMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.BusinessAreaMode.ToString) = value
            End Set
        End Property
        Public Shared Property BusinessUnitMode() As String
            Get
                If Session(SessionVariables.BusinessUnitMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.BusinessUnitMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.BusinessUnitMode.ToString) = value
            End Set
        End Property
        Public Shared Property CalendarEventsMode() As String
            Get
                If Session(SessionVariables.CalendarEventsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CalendarEventsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CalendarEventsMode.ToString) = value
            End Set
        End Property
        Public Shared Property CalendarEventsSelectedID() As Integer
            Get
                If Session(SessionVariables.CalendarEventsSelectedID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CalendarEventsSelectedID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.CalendarEventsSelectedID.ToString) = value
            End Set
        End Property
        Public Shared Property CallingMode() As String
            Get
                If Session(SessionVariables.CallingMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CallingMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CallingMode.ToString) = value
            End Set
        End Property
        Public Shared Property CallingProgram() As String
            Get
                If Session(SessionVariables.CallingProgram.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CallingProgram.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CallingProgram.ToString) = value
            End Set
        End Property
        Public Shared Property CallingProgram2() As String
            Get
                If Session(SessionVariables.CallingProgram2.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CallingProgram2.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CallingProgram2.ToString) = value
            End Set
        End Property
        Public Shared Property ChartHeight() As String
            Get
                If Session(SessionVariables.ChartHeight.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ChartHeight.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ChartHeight.ToString) = value
            End Set
        End Property
        Public Shared Property ChartOPI() As String
            Get
                If Session(SessionVariables.ChartOPI.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ChartOPI.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ChartOPI.ToString) = value
            End Set
        End Property
        Public Shared Property ChartTeamID() As Integer
            Get
                If Session(SessionVariables.ChartTeamID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ChartTeamID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.ChartTeamID.ToString) = value
            End Set
        End Property
        Public Shared Property ChartTitle() As String
            Get
                If Session(SessionVariables.ChartTitle.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ChartTitle.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ChartTitle.ToString) = value
            End Set
        End Property
        Public Shared Property ChartType() As String
            Get
                If Session(SessionVariables.ChartType.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ChartType.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ChartType.ToString) = value
            End Set
        End Property
        Public Shared Property ChartWidth() As String
            Get
                If Session(SessionVariables.ChartWidth.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ChartWidth.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ChartWidth.ToString) = value
            End Set
        End Property
        Public Shared Property CloseOnLogout() As Boolean
            Get
                If Session(SessionVariables.CloseOnLogout.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CloseOnLogout.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.CloseOnLogout.ToString) = value
            End Set
        End Property
        Public Shared Property ConnectionError() As String
            Get
                If Session(SessionVariables.ConnectionError.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ConnectionError.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ConnectionError.ToString) = value
            End Set
        End Property
        Public Shared Property CultureMasterMode() As String
            Get
                If Session(SessionVariables.CultureMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CultureMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CultureMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property CulturePref() As String
            Get
                If Session(SessionVariables.CulturePref.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CulturePref.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CulturePref.ToString) = value
            End Set
        End Property
        Public Shared Property CultureTranslationMode() As String
            Get
                If Session(SessionVariables.CultureTranslationMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CultureTranslationMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CultureTranslationMode.ToString) = value
            End Set
        End Property
        Public Shared Property CurrentMenuProgram() As String
            Get
                If Session(SessionVariables.CurrentMenuProgram.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CurrentMenuProgram.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CurrentMenuProgram.ToString) = value
            End Set
        End Property
        Public Shared Property CurrentProgram() As String
            Get
                If Session(SessionVariables.CurrentProgram.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CurrentProgram.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CurrentProgram.ToString) = value
            End Set
        End Property
        Public Shared Property CurrentProgramURL() As String
            Get
                If Session(SessionVariables.CurrentProgramURL.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.CurrentProgramURL.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.CurrentProgramURL.ToString) = value
            End Set
        End Property
        Public Shared Property DataElementMode() As String
            Get
                If Session(SessionVariables.DataElementMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.DataElementMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.DataElementMode.ToString) = value
            End Set
        End Property
        Public Shared Property DateFormat() As String
            Get
                If Session(SessionVariables.DateFormat.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.DateFormat.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.DateFormat.ToString) = value
            End Set
        End Property
        Public Shared Property DateTimeFormat() As String
            Get
                If Session(SessionVariables.DateTimeFormat.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.DateTimeFormat.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.DateTimeFormat.ToString) = value
            End Set
        End Property
        Public Shared Property DefaultWorkCenter() As String
            Get
                If Session(SessionVariables.DefaultWorkCenter.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.DefaultWorkCenter.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.DefaultWorkCenter.ToString) = value
            End Set
        End Property
        Public Shared Property DetailChart() As String
            Get
                If Session(SessionVariables.DetailChart.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.DetailChart.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.DetailChart.ToString) = value
            End Set
        End Property
        Public Shared Property DisplayClosedTeams() As Boolean
            Get
                If Session(SessionVariables.DisplayClosedTeams.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.DisplayClosedTeams.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.DisplayClosedTeams.ToString) = value
            End Set
        End Property
        Public Shared Property DisplayClosedTeamActions() As Boolean
            Get
                If Session(SessionVariables.DisplayClosedTeamActions.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.DisplayClosedTeamActions.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.DisplayClosedTeamActions.ToString) = value
            End Set
        End Property
        Public Shared Property EditMode() As String
            Get
                If Session(SessionVariables.EditMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EditMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.EditMode.ToString) = value
            End Set
        End Property
        Public Shared Property EventLogEmailAddressMasterMode() As String
            Get
                If Session(SessionVariables.EventLogEmailAddressMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EventLogEmailAddressMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.EventLogEmailAddressMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property EntityFilterWorkcenterID() As Integer
            Get
                If Session(SessionVariables.EntityFilterWorkcenterID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EntityFilterWorkcenterID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.EntityFilterWorkcenterID.ToString) = value
            End Set
        End Property
        Public Shared Property EntityFilterEntity() As String
            Get
                If Session(SessionVariables.EntityFilterEntity.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EntityFilterEntity.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.EntityFilterEntity.ToString) = value
            End Set
        End Property
        Public Shared Property EntityFilterLocation() As String
            Get
                If Session(SessionVariables.EntityFilterLocation.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EntityFilterLocation.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.EntityFilterLocation.ToString) = value
            End Set
        End Property
        Public Shared Property EntityMasterMode() As String
            Get
                If Session(SessionVariables.EntityMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EntityMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.EntityMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property EnvSelEditMonth() As String
            Get
                If Session(SessionVariables.EnvSelEditMonth.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EnvSelEditMonth.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.EnvSelEditMonth.ToString) = value
            End Set
        End Property
        Public Shared Property EnvSelNavYear() As String
            Get
                If Session(SessionVariables.EnvSelNavYear.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EnvSelNavYear.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.EnvSelNavYear.ToString) = value
            End Set
        End Property
        Public Shared Property EventLogTypeMode() As String
            Get
                If Session(SessionVariables.EventLogTypeMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.EnvSelNavYear.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.EventLogTypeMode.ToString) = value
            End Set
        End Property
        Public Shared Property ExpandedTeamKPIs() As ArrayList
            Get
                If Session(SessionVariables.ExpandedTeamKPIs.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ExpandedTeamKPIs.ToString)
                Else
                    Dim retval As New ArrayList
                    Return retval
                End If
            End Get
            Set(ByVal value As ArrayList)
                Session(SessionVariables.ExpandedTeamKPIs.ToString) = value
            End Set
        End Property
        Public Shared Property ExportString() As String
            Get
                If Session(SessionVariables.ExportString.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ExportString.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ExportString.ToString) = value
            End Set
        End Property
        Public Shared Property FeedbackMode() As String
            Get
                If Session(SessionVariables.FeedbackMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.FeedbackMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.FeedbackMode.ToString) = value
            End Set
        End Property
        Public Shared Property FXRateElementMode() As String
            Get
                If Session(SessionVariables.FXRateElementMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.FXRateElementMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.FXRateElementMode.ToString) = value
            End Set
        End Property
        Public Shared Property FXRateMode() As String
            Get
                If Session(SessionVariables.FXRateMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.FXRateMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.FXRateMode.ToString) = value
            End Set
        End Property
        Public Shared Property HeaderMessage() As String
            Get
                If Session(SessionVariables.HeaderMessage.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.HeaderMessage.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.HeaderMessage.ToString) = value
            End Set
        End Property
        Public Shared Property HelpAttachmentMode() As String
            Get
                If Session(SessionVariables.HelpAttachmentMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.HelpAttachmentMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.HelpAttachmentMode.ToString) = value
            End Set
        End Property
        Public Shared Property IsAdministrator() As Boolean
            Get
                If Session(SessionVariables.IsAdministrator.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.IsAdministrator.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.IsAdministrator.ToString) = value
            End Set
        End Property
        Public Shared Property JobMode() As String
            Get
                If Session(SessionVariables.JobMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.JobMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.JobMode.ToString) = value
            End Set
        End Property
        Public Shared Property JobSkillAttachmentsMode() As String
            Get
                If Session(SessionVariables.JobSkillAttachmentsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.JobSkillAttachmentsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.JobSkillAttachmentsMode.ToString) = value
            End Set
        End Property
        Public Shared Property JobSkillMode() As String
            Get
                If Session(SessionVariables.JobSkillMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.JobSkillMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.JobSkillMode.ToString) = value
            End Set
        End Property
        Public Shared Property LastPixelPosition() As Hashtable
            Get
                If Session(SessionVariables.LastPixelPosition.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.LastPixelPosition.ToString)
                Else
                    Return Nothing
                End If
            End Get
            Set(ByVal value As Hashtable)
                Session(SessionVariables.LastPixelPosition.ToString) = value
            End Set
        End Property
        Public Shared Property MasterControlExitProgram() As String
            Get
                If Session(SessionVariables.MasterControlExitProgram.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MasterControlExitProgram.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MasterControlExitProgram.ToString) = value
            End Set
        End Property
        Public Shared Property MasterControlExitProgram2() As String
            Get
                If Session(SessionVariables.MasterControlExitProgram2.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MasterControlExitProgram2.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MasterControlExitProgram2.ToString) = value
            End Set
        End Property
        Public Shared Property MenuActionCoordinates() As String
            Get
                If Session(SessionVariables.MenuActioncoordinates.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MenuActioncoordinates.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MenuActioncoordinates.ToString) = value
            End Set
        End Property
        Public Shared Property MenuMode() As String
            Get
                If Session(SessionVariables.MenuMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MenuMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MenuMode.ToString) = value
            End Set
        End Property
        Public Shared Property MenuOptionMode() As String
            Get
                If Session(SessionVariables.MenuOptionMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MenuOptionMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MenuOptionMode.ToString) = value
            End Set
        End Property
        Public Shared Property MenuProgramGroupMode() As String
            Get
                If Session(SessionVariables.MenuProgramGroupMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MenuProgramGroupMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MenuProgramGroupMode.ToString) = value
            End Set
        End Property
        Public Shared Property MetricTargetMode() As String
            Get
                If Session(SessionVariables.MetricTargetMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MetricTargetMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MetricTargetMode.ToString) = value
            End Set
        End Property
        Public Shared Property MeetingDate() As String
            Get
                If Session(SessionVariables.MeetingDate.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MeetingDate.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MeetingDate.ToString) = value
            End Set
        End Property
        Public Shared Property MeetingTime() As String
            Get
                If Session(SessionVariables.MeetingTime.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MeetingTime.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MeetingTime.ToString) = value
            End Set
        End Property
        Public Shared Property Mode() As String
            Get
                If Session(SessionVariables.Mode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Mode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Mode.ToString) = value
            End Set
        End Property
        Public Shared Property MyTeamKPIsShowClosed() As String
            Get
                If Session(SessionVariables.MyTeamKPIsShowClosed.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.MyTeamKPIsShowClosed.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.MyTeamKPIsShowClosed.ToString) = value
            End Set
        End Property
        Public Shared Property NetworkLogin() As Boolean
            Get
                If Session(SessionVariables.NetworkLogin.ToString) IsNot Nothing Then
                    Return Convert.ToBoolean(Session(SessionVariables.NetworkLogin.ToString))
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.NetworkLogin.ToString) = value
            End Set
        End Property
        Public Shared Property OEEReportsMode() As String
            Get
                If Session(SessionVariables.OEEReportsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.OEEReportsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.OEEReportsMode.ToString) = value
            End Set
        End Property
        Public Shared Property OPIEntrySelectedValue() As String
            Get
                If Session(SessionVariables.OPIEntrySelectedValue.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.OPIEntrySelectedValue.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.OPIEntrySelectedValue.ToString) = value
            End Set
        End Property
        Public Shared Property OPIEntrySelectedValue1() As String
            Get
                If Session(SessionVariables.OPIEntrySelectedValue1.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.OPIEntrySelectedValue1.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.OPIEntrySelectedValue1.ToString) = value
            End Set
        End Property
        Public Shared Property OPIMode() As String
            Get
                If Session(SessionVariables.OPIMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.OPIMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.OPIMode.ToString) = value
            End Set
        End Property
        Public Shared Property OPIUOM() As String
            Get
                If Session(SessionVariables.OPIUOM.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.OPIUOM.ToString).ToString
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.OPIUOM.ToString) = value
            End Set
        End Property
        Public Shared Property Origin1Mode() As String
            Get
                If Session(SessionVariables.Origin1Mode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Origin1Mode.ToString).ToString
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Origin1Mode.ToString) = value
            End Set
        End Property
        Public Shared Property Origin2Mode() As String
            Get
                If Session(SessionVariables.Origin2Mode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Origin2Mode.ToString).ToString
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Origin2Mode.ToString) = value
            End Set
        End Property
        Public Shared Property Origin3Mode() As String
            Get
                If Session(SessionVariables.Origin3Mode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.Origin3Mode.ToString).ToString
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.Origin3Mode.ToString) = value
            End Set
        End Property
        Public Shared Property OverviewSortColumn() As String
            Get
                If Session(SessionVariables.OverviewSortColumn.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.OverviewSortColumn.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.OverviewSortColumn.ToString) = value
            End Set
        End Property
        Public Shared Property PillarMasterMode() As String
            Get
                If Session(SessionVariables.PillarMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.PillarMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.PillarMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property PillarMembershipMode() As String
            Get
                If Session(SessionVariables.PillarMembershipMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.PillarMembershipMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.PillarMembershipMode.ToString) = value
            End Set
        End Property
        Public Shared Property PopupAttachmentMode() As String
            Get
                If Session(SessionVariables.PopupAttachmentMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.PopupAttachmentMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.PopupAttachmentMode.ToString) = value
            End Set
        End Property
        Public Shared Property PositionMasterMode() As String
            Get
                If Session(SessionVariables.PositionMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.PositionMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.PositionMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property ProgramMasterMode() As String
            Get
                If Session(SessionVariables.ProgramMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ProgramMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ProgramMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property QueryFrom() As String
            Get
                If Session(SessionVariables.QueryFrom.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.QueryFrom.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.QueryFrom.ToString) = value
            End Set
        End Property
        Public Shared Property QueryGroupBy() As String
            Get
                If Session(SessionVariables.QueryGroupBy.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.QueryGroupBy.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.QueryGroupBy.ToString) = value
            End Set
        End Property
        Public Shared Property QueryMasterMode() As String
            Get
                If Session(SessionVariables.QueryMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.QueryMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.QueryMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property QueryOrderBy() As String
            Get
                If Session(SessionVariables.QueryOrderBy.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.QueryOrderBy.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.QueryOrderBy.ToString) = value
            End Set
        End Property
        Public Shared Property QueryParameterMasterMode() As String
            Get
                If Session(SessionVariables.QueryParameterMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.QueryParameterMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.QueryParameterMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property QuerySelect() As String
            Get
                If Session(SessionVariables.QuerySelect.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.QuerySelect.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.QuerySelect.ToString) = value
            End Set
        End Property
        Public Shared Property QueryWhere() As String
            Get
                If Session(SessionVariables.QueryWhere.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.QueryWhere.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.QueryWhere.ToString) = value
            End Set
        End Property
        Public Shared Property RoomMasterMode() As String
            Get
                If Session(SessionVariables.RoomMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RoomMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RoomMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property RoomReservationsMode() As String
            Get
                If Session(SessionVariables.RoomReservationsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RoomReservationsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RoomReservationsMode.ToString) = value
            End Set
        End Property
        Public Shared Property RoutesMode() As String
            Get
                If Session(SessionVariables.RoutesMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RoutesMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RoutesMode.ToString) = value
            End Set
        End Property
        Public Shared Property RouteStepsKeyActionsMode() As String
            Get
                If Session(SessionVariables.RouteStepsKeyActionsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RouteStepsKeyActionsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RouteStepsKeyActionsMode.ToString) = value
            End Set
        End Property
        Public Shared Property RouteStepsKeyActionsToolsMode() As String
            Get
                If Session(SessionVariables.RouteStepsKeyActionsToolsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RouteStepsKeyActionsToolsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RouteStepsKeyActionsToolsMode.ToString) = value
            End Set
        End Property
        Public Shared Property RoutesStepsMode() As String
            Get
                If Session(SessionVariables.RoutesStepsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RoutesStepsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RoutesStepsMode.ToString) = value
            End Set
        End Property
        Public Shared Property SavedSortOrders() As Hashtable
            Get
                If Session(SessionVariables.SavedSortOrders.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SavedSortOrders.ToString)
                Else
                    Dim EmptyHashtable As New Hashtable
                    Return EmptyHashtable
                End If
            End Get
            Set(ByVal value As Hashtable)
                Session(SessionVariables.SavedSortOrders.ToString) = value
            End Set
        End Property
        Public Shared Property SecondaryProgram() As String
            Get
                If Session(SessionVariables.SecondaryProgram.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SecondaryProgram.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SecondaryProgram.ToString) = value
            End Set
        End Property
        Public Shared Property SecurityGroupMasterMode() As String
            Get
                If Session(SessionVariables.SecurityGroupMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SecurityGroupMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SecurityGroupMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SecurityGroupProgramMasterMode() As String
            Get
                If Session(SessionVariables.SecurityGroupProgramMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SecurityGroupProgramMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SecurityGroupProgramMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedCultureCode() As String
            Get
                If Session(SessionVariables.SelectedCultureCode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedCultureCode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedCultureCode.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedCultureValue() As String
            Get
                If Session(SessionVariables.SelectedCultureValue.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedCultureValue.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedCultureValue.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedJobName() As String
            Get
                If Session(SessionVariables.SelectedJobName.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedJobName.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedJobName.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedKeyActionNo() As String
            Get
                If Session(SessionVariables.SelectedKeyActionNo.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedKeyActionNo.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedKeyActionNo.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedKeyActionToolID() As String
            Get
                If Session(SessionVariables.SelectedKeyActionToolID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedKeyActionToolID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedKeyActionToolID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedKPIReportGroupID() As Integer
            Get
                If Session(SessionVariables.SelectedKPIReportGroupID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedKPIReportGroupID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedKPIReportGroupID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedMetricID() As String
            Get
                If Session(SessionVariables.SelectedMetricID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedMetricID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedMetricID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedOPI() As String
            Get
                If Session(SessionVariables.SelectedOPI.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedOPI.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedOPI.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedOPIDate() As String
            Get
                If Session(SessionVariables.SelectedOPIDate.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedOPIDate.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedOPIDate.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedPalletPrinter() As String
            Get
                If Session(SessionVariables.SelectedPalletPrinter.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedPalletPrinter.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedPalletPrinter.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedQuery() As String
            Get
                If Session(SessionVariables.SelectedQuery.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedQuery.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedQuery.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedQueryName() As String
            Get
                If Session(SessionVariables.SelectedQueryName.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedQueryName.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedQueryName.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedRollPrinter() As String
            Get
                If Session(SessionVariables.SelectedRollPrinter.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedRollPrinter.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedRollPrinter.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedRoute() As String
            Get
                If Session(SessionVariables.SelectedRoute.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedRoute.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedRoute.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedRouteStepNo() As String
            Get
                If Session(SessionVariables.SelectedRouteStepNo.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedRouteStepNo.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedRouteStepNo.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedSite() As String
            Get
                If Session(SessionVariables.SelectedSite.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedSite.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedSite.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedSiteGroup() As String
            Get
                If Session(SessionVariables.SelectedSiteGroup.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedSiteGroup.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedSiteGroup.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedSiteGroupID() As Integer
            Get
                If Session(SessionVariables.SelectedSiteGroupID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedSiteGroupID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedSiteGroupID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedSiteID() As Integer
            Get
                If Session(SessionVariables.SelectedSiteID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedSiteID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedSiteID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedSLICEActivityLinksID() As Integer
            Get
                If Session(SessionVariables.SelectedSLICEActivityLinksID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedSLICEActivityLinksID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedSLICEActivityLinksID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedTargetDate() As String
            Get
                If Session(SessionVariables.SelectedTargetDate.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedTargetDate.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedTargetDate.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValue() As String
            Get
                If Session(SessionVariables.SelectedValue.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValue.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValue.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValue1() As String
            Get
                If Session(SessionVariables.SelectedValue1.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValue1.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValue1.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValue2() As String
            Get
                If Session(SessionVariables.SelectedValue2.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValue2.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValue2.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValue3() As String
            Get
                If Session(SessionVariables.SelectedValue3.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValue3.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValue3.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValue4() As String
            Get
                If Session(SessionVariables.SelectedValue4.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValue4.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValue4.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueActivityID() As String
            Get
                If Session(SessionVariables.SelectedValueActivityID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueActivityID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueActivityID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueAnomalyID() As Integer
            Get
                If Session(SessionVariables.SelectedValueAnomalyID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueAnomalyID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueAnomalyID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueAreaGroupID() As Integer
            Get
                If Session(SessionVariables.SelectedValueAreaGroupID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueAreaGroupID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueAreaGroupID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueAnomalyActionID() As Integer
            Get
                If Session(SessionVariables.SelectedValueAnomalyActionID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueAnomalyActionID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueAnomalyActionID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueAnomalyCauseID() As Integer
            Get
                If Session(SessionVariables.SelectedValueAnomalyCauseID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueAnomalyCauseID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueAnomalyCauseID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueAttachment() As String
            Get
                If Session(SessionVariables.SelectedValueAttachment.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueAttachment.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueAttachment.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueAttachmentID() As String
            Get
                If Session(SessionVariables.SelectedValueAttachmentID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueAttachmentID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueAttachmentID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueBusinessAreaID() As Integer
            Get
                If Session(SessionVariables.SelectedValueBusinessAreaID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueBusinessAreaID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueBusinessAreaID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueBusinessUnitID() As Integer
            Get
                If Session(SessionVariables.SelectedValueBusinessUnitID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueBusinessUnitID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueBusinessUnitID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueCategory() As String
            Get
                If Session(SessionVariables.SelectedValueCategory.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueCategory.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueCategory.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueCategoryID() As String
            Get
                If Session(SessionVariables.SelectedValueCategoryID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueCategoryID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueCategoryID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueCategoryTypeID() As String
            Get
                If Session(SessionVariables.SelectedValueCategoryTypeID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueCategoryTypeID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueCategoryTypeID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueCheckSheetID() As String
            Get
                If Session(SessionVariables.SelectedValueCheckSheetID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueCheckSheetID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueCheckSheetID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueDescription() As String
            Get
                If Session(SessionVariables.SelectedValueDescription.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueDescription.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueDescription.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueEntityID() As String
            Get
                If Session(SessionVariables.SelectedValueEntityID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueEntityID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueEntityID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueEventDate() As String
            Get
                If Session(SessionVariables.SelectedValueEventDate.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueEventDate.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueEventDate.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueFXRateID() As Integer
            Get
                If Session(SessionVariables.SelectedValueFXRateID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueFXRateID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueFXRateID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueFXRatePeriod() As String
            Get
                If Session(SessionVariables.SelectedValueFXRatePeriod.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueFXRatePeriod.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueFXRatePeriod.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueJob() As Integer
            Get
                If Session(SessionVariables.SelectedValueJob.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueJob.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueJob.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueJobName() As String
            Get
                If Session(SessionVariables.SelectedValueJobName.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueJobName.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueJobName.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueJobSkillID() As String
            Get
                If Session(SessionVariables.SelectedValueJobSkillID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueJobSkillID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueJobSkillID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueKPIID() As Integer
            Get
                If Session(SessionVariables.SelectedValueKPIID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueKPIID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueKPIID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueMenu() As String
            Get
                If Session(SessionVariables.SelectedValueMenu.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueMenu.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueMenu.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueOption() As String
            Get
                If Session(SessionVariables.SelectedValueOption.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueOption.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueOption.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueOptionMenu() As String
            Get
                If Session(SessionVariables.SelectedValueOptionMenu.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueOptionMenu.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueOptionMenu.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueOrigin1ID() As Integer
            Get
                If Session(SessionVariables.SelectedValueOrigin1ID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueOrigin1ID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueOrigin1ID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueOrigin2ID() As Integer
            Get
                If Session(SessionVariables.SelectedValueOrigin2ID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueOrigin2ID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueOrigin2ID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueOrigin3ID() As Integer
            Get
                If Session(SessionVariables.SelectedValueOrigin3ID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueOrigin3ID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueOrigin3ID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValuePositionID() As String
            Get
                If Session(SessionVariables.SelectedValuePositionID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValuePositionID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValuePositionID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueProgram() As String
            Get
                If Session(SessionVariables.SelectedValueProgram.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueProgram.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueProgram.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueProgramGroup() As String
            Get
                If Session(SessionVariables.SelectedValueProgramGroup.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueProgramGroup.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueProgramGroup.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueProgramGroupMenu() As String
            Get
                If Session(SessionVariables.SelectedValueProgramGroupMenu.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueProgramGroupMenu.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueProgramGroupMenu.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueQueryID() As String
            Get
                If Session(SessionVariables.SelectedValueQueryID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueQueryID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueQueryID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueReservationID() As String
            Get
                If Session(SessionVariables.SelectedValueReservationID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueReservationID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueReservationID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueRoomID() As String
            Get
                If Session(SessionVariables.SelectedValueRoomID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueRoomID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueRoomID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSite() As String
            Get
                If Session(SessionVariables.SelectedValueSite.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSite.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSite.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSiteID() As String
            Get
                If Session(SessionVariables.SelectedValueSiteID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSiteID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSiteID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSliceActivityGroupID() As String
            Get
                If Session(SessionVariables.SelectedValueSliceActivityGroupID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSliceActivityGroupID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSliceActivityGroupID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueUser() As String
            Get
                If Session(SessionVariables.SelectedValueUser.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueUser.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueUser.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueUserJobUser() As String
            Get
                If Session(SessionVariables.SelectedValueUserJobUser.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueUserJobUser.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueUserJobUser.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueWorkcenterID() As String
            Get
                If Session(SessionVariables.SelectedValueWorkcenterID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueWorkcenterID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueWorkcenterID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedWorkCenter() As String
            Get
                If Session(SessionVariables.SelectedWorkCenter.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedWorkCenter.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedWorkCenter.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedWorkCenterID() As Integer
            Get
                If Session(SessionVariables.SelectedWorkcenterID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedWorkcenterID.ToString)
                Else
                    Return -1
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedWorkcenterID.ToString) = value
            End Set
        End Property
        Public Shared Property ShowMenuOptionNumbers() As Boolean
            Get
                If Session(SessionVariables.ShowMenuOptionNumbers.ToString) IsNot Nothing Then
                    Return Convert.ToBoolean(Session(SessionVariables.ShowMenuOptionNumbers.ToString))
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.ShowMenuOptionNumbers.ToString) = value
            End Set
        End Property
        Public Shared Property ShowAllMenuOptions() As Boolean
            Get
                If Session(SessionVariables.ShowAllMenuOptions.ToString) IsNot Nothing Then
                    Return CBool(Session(SessionVariables.ShowAllMenuOptions.ToString))
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.ShowAllMenuOptions.ToString) = value
            End Set
        End Property
        Public Shared Property ShowProjected() As Boolean
            Get
                If Session(SessionVariables.ShowProjected.ToString) IsNot Nothing Then
                    Return CBool(Session(SessionVariables.ShowProjected.ToString))
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.ShowProjected.ToString) = value
            End Set
        End Property
        Public Shared Property SiteGroupSelectionRequired() As String
            Get
                If Session(SessionVariables.SiteGroupSelectionRequired.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SiteGroupSelectionRequired.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SiteGroupSelectionRequired.ToString) = value
            End Set
        End Property
        Public Shared Property SiteMasterMode() As String
            Get
                If Session(SessionVariables.SiteMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SiteMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SiteMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SiteSelectionRequired() As String
            Get
                If Session(SessionVariables.SiteSelectionRequired.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SiteSelectionRequired.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SiteSelectionRequired.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEActivityGroupMasterID() As String
            Get
                If Session(SessionVariables.SLICEActivityGroupMasterID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEActivityGroupMasterID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEActivityGroupMasterID.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEActivityID() As String
            Get
                If Session(SessionVariables.SLICEActivityID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEActivityID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEActivityID.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEActivityLinkMasterMode() As String
            Get
                If Session(SessionVariables.SLICEActivityLinkMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEActivityLinkMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEActivityLinkMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEActivityMaster1() As String
            Get
                If Session(SessionVariables.SLICEActivityMaster1.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEActivityMaster1.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEActivityMaster1.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEActivityMasterMode() As String
            Get
                If Session(SessionVariables.SLICEActivityMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEActivityMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEActivityMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEActivityResults() As String
            Get
                If Session(SessionVariables.SLICEActivityResults.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEActivityResults.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEActivityResults.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEChecksheetActivityID() As Integer
            Get
                If Session(SessionVariables.SLICEChecksheetActivityID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEChecksheetActivityID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SLICEChecksheetActivityID.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEChecksheetMasterMode() As String
            Get
                If Session(SessionVariables.SLICEChecksheetMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEChecksheetMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEChecksheetMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEFrequencyMasterMode() As String
            Get
                If Session(SessionVariables.SLICEFrequencyMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEFrequencyMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEFrequencyMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEResultMasterMode() As String
            Get
                If Session(SessionVariables.SLICEResultMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEResultMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEResultMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SLICETypeMasterMode() As String
            Get
                If Session(SessionVariables.SLICETypeMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICETypeMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICETypeMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamActionPlanMode() As String
            Get
                If Session(SessionVariables.TeamActionPlanMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamActionPlanMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamActionPlanMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamBoardMenuDefaultsMode() As String
            Get
                If Session(SessionVariables.TeamBoardMenuDefaultsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamBoardMenuDefaultsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamBoardMenuDefaultsMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamBoardMenuOptionMasterMode() As String
            Get
                If Session(SessionVariables.TeamBoardMenuOptionMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamBoardMenuOptionMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamBoardMenuOptionMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamKPIMode() As String
            Get
                If Session(SessionVariables.TeamKPIMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamKPIMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamKPIMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamLogMode() As String
            Get
                If Session(SessionVariables.TeamLogMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamLogMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamLogMode.ToString) = value
            End Set
        End Property
        Public Shared Property SkillCategoryMode() As String
            Get
                If Session(SessionVariables.SkillCategoryMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SkillCategoryMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SkillCategoryMode.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSLICEActivityID() As Integer
            Get
                If Session(SessionVariables.SelectedValueSLICEActivityID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSLICEActivityID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueSLICEActivityID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSLICEFrequencyID() As String
            Get
                If Session(SessionVariables.SelectedValueSLICEFrequencyID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSLICEFrequencyID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSLICEFrequencyID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSLICEFrequency() As String
            Get
                If Session(SessionVariables.SelectedValueSLICEFrequency.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSLICEFrequency.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSLICEFrequency.ToString) = value
            End Set
        End Property
        Public Shared Property SLICEActivityGroupMasterMode() As String
            Get
                If Session(SessionVariables.SLICEActivityGroupMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SLICEActivityGroupMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SLICEActivityGroupMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSLICEResultID() As String
            Get
                If Session(SessionVariables.SelectedValueSLICEResultID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSLICEResultID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSLICEResultID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSLICEType() As String
            Get
                If Session(SessionVariables.SelectedValueSLICEType.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSLICEType.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSLICEType.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSLICETypeID() As String
            Get
                If Session(SessionVariables.SelectedValueSLICETypeID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSLICETypeID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSLICETypeID.ToString) = value
            End Set
        End Property
        Public Shared Property TeamMeetingAttendanceMode() As String
            Get
                If Session(SessionVariables.TeamMeetingAttendanceMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamMeetingAttendanceMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamMeetingAttendanceMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamMeetingEmailDateTime() As String
            Get
                If Session(SessionVariables.TeamMeetingEmailDateTime.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamMeetingEmailDateTime.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamMeetingEmailDateTime.ToString) = value
            End Set
        End Property
        Public Shared Property TeamMeetingEmailFrom() As String
            Get
                If Session(SessionVariables.TeamMeetingEmailFrom.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamMeetingEmailFrom.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamMeetingEmailFrom.ToString) = value
            End Set
        End Property
        Public Shared Property TeamMeetingID() As Integer
            Get
                If Session(SessionVariables.TeamMeetingID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamMeetingID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.TeamMeetingID.ToString) = value
            End Set
        End Property
        Public Shared Property TeamMeetingNewAgenda() As String
            Get
                If Session(SessionVariables.TeamMeetingNewAgenda.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamMeetingNewAgenda.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamMeetingNewAgenda.ToString) = value
            End Set
        End Property
        Public Shared Property TeamMeetingNewDate() As String
            Get
                If Session(SessionVariables.TeamMeetingNewDate.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamMeetingNewDate.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamMeetingNewDate.ToString) = value
            End Set
        End Property
        Public Shared Property TeamMeetingsMode() As String
            Get
                If Session(SessionVariables.TeamMeetingsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamMeetingsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamMeetingsMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamMembershipMode() As String
            Get
                If Session(SessionVariables.TeamMembershipMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamMembershipMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamMembershipMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamsMode() As String
            Get
                If Session(SessionVariables.TeamsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamsMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamOPIControlLimitsMode() As String
            Get
                If Session(SessionVariables.TeamOPIControlLimitsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamOPIControlLimitsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamOPIControlLimitsMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamOPIEventMode() As String
            Get
                If Session(SessionVariables.TeamOPIEventMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamOPIEventMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamOPIEventMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamOPIValueMode() As String
            Get
                If Session(SessionVariables.TeamOPIValueMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamOPIValueMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamOPIValueMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamOPIValueID() As Integer
            Get
                If Session(SessionVariables.TeamOPIValueID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamOPIValueID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.TeamOPIValueID.ToString) = value
            End Set
        End Property
        Public Shared Property TeamStack() As Stack
            Get
                If Session(SessionVariables.TeamStack.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamStack.ToString)
                Else
                    Return New Stack
                End If
            End Get
            Set(ByVal value As Stack)
                Session(SessionVariables.TeamStack.ToString) = value
            End Set
        End Property
        Public Shared Property TeamStatusMode() As String
            Get
                If Session(SessionVariables.TeamStatusMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamStatusMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamStatusMode.ToString) = value
            End Set
        End Property
        Public Shared Property TeamUsersMode() As String
            Get
                If Session(SessionVariables.TeamUsersMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TeamUsersMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TeamUsersMode.ToString) = value
            End Set
        End Property
        Public Shared Property TemplateAttachmentMode() As String
            Get
                If Session(SessionVariables.TemplateAttachmentMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TemplateAttachmentMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TemplateAttachmentMode.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerCollectionMode() As String
            Get
                If Session(SessionVariables.TrackerCollectionMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerCollectionMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TrackerCollectionMode.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerMode() As String
            Get
                If Session(SessionVariables.TrackerMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TrackerMode.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerPlanMode() As String
            Get
                If Session(SessionVariables.TrackerPlanMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerPlanMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TrackerPlanMode.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerPlanSavingsMode() As String
            Get
                If Session(SessionVariables.TrackerPlanSavingsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerPlanSavingsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TrackerPlanSavingsMode.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerSelEditMode() As String
            Get
                If Session(SessionVariables.TrackerSelEditMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerSelEditMode.ToString)
                Else
                    Return ""
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TrackerSelEditMode.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerSelEditMonth() As Integer
            Get
                If Session(SessionVariables.TrackerSelEditMonth.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerSelEditMonth.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.TrackerSelEditMonth.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerSelNavYear() As Integer
            Get
                If Session(SessionVariables.TrackerSelNavYear.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerSelNavYear.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.TrackerSelNavYear.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerSelSiteID() As Integer
            Get
                If Session(SessionVariables.TrackerSelSiteID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerSelSiteID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.TrackerSelSiteID.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerTypeMode() As String
            Get
                If Session(SessionVariables.TrackerTypeMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerTypeMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TrackerTypeMode.ToString) = value
            End Set
        End Property
        Public Shared Property TrackerVariableMode() As String
            Get
                If Session(SessionVariables.TrackerVariableMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrackerVariableMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TrackerVariableMode.ToString) = value
            End Set
        End Property
        Public Shared Property TrainingAttachmentMode() As String
            Get
                If Session(SessionVariables.TrainingAttachmentMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.TrainingAttachmentMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.TrainingAttachmentMode.ToString) = value
            End Set
        End Property
        Public Shared Property UserADMode() As String
            Get
                If Session(SessionVariables.UserADMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserADMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserADMode.ToString) = value
            End Set
        End Property
        Public Shared Property UserJobMode() As String
            Get
                If Session(SessionVariables.UserJobMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserJobMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserJobMode.ToString) = value
            End Set
        End Property
        Public Shared Property UserJobSortOrder() As String
            Get
                If Session(SessionVariables.UserJobSortOrder.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserJobSortOrder.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserJobSortOrder.ToString) = value
            End Set
        End Property
        Public Shared Property UserID() As String
            Get
                If Session(SessionVariables.UserID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserID.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserID.ToString) = value
            End Set
        End Property
        Public Shared Property UserMasterMode() As String
            Get
                If Session(SessionVariables.UserMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property UserName() As String
            Get
                If Session(SessionVariables.UserName.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserName.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserName.ToString) = value
            End Set
        End Property
        Public Shared Property UserITMode() As String
            Get
                If Session(SessionVariables.UserITMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserITMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserITMode.ToString) = value
            End Set
        End Property
        Public Shared Property UserSecurityGroupMasterMode() As String
            Get
                If Session(SessionVariables.UserSecurityGroupMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserSecurityGroupMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserSecurityGroupMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property UserSkillRatingsMode() As String
            Get
                If Session(SessionVariables.UserSkillRatingsMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserSkillRatingsMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserSkillRatingsMode.ToString) = value
            End Set
        End Property
        Public Shared Property UserSiteMasterMode() As String
            Get
                If Session(SessionVariables.UserSiteMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserSiteMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserSiteMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property UserWorkCenterGroupMasterMode() As String
            Get
                If Session(SessionVariables.UserWorkCenterGroupMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.UserWorkCenterGroupMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.UserWorkCenterGroupMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property WhiteChart() As String
            Get
                If Session(SessionVariables.WhiteChart.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WhiteChart.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.WhiteChart.ToString) = value
            End Set
        End Property
        Public Shared Property WorkCenterControlMasterMode() As String
            Get
                If Session(SessionVariables.WorkCenterControlMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WorkCenterControlMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.WorkCenterControlMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property WorkCenterGroupMasterMode() As String
            Get
                If Session(SessionVariables.WorkCenterGroupMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WorkCenterGroupMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.WorkCenterGroupMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property WorkCenterGroupWorkCenterMasterMode() As String
            Get
                If Session(SessionVariables.WorkCenterGroupWorkCenterMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WorkCenterGroupWorkCenterMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.WorkCenterGroupWorkCenterMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property WorkcenterMasterMode() As String
            Get
                If Session(SessionVariables.WorkcenterMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WorkcenterMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.WorkcenterMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property WorkCenterOvertaken() As String
            Get
                If Session(SessionVariables.WorkCenterOvertaken.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WorkCenterOvertaken.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.WorkCenterOvertaken.ToString) = value
            End Set
        End Property
        Public Shared Property WorkCenterOvertakenMessage() As String
            Get
                If Session(SessionVariables.WorkCenterOvertakenMessage.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WorkCenterOvertakenMessage.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.WorkCenterOvertakenMessage.ToString) = value
            End Set
        End Property
        Public Shared Property WorkingSite() As String
            Get
                If Session(SessionVariables.WorkingSite.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WorkingSite.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.WorkingSite.ToString) = value
            End Set
        End Property
        Public Shared Property WorkingSiteID() As Integer
            Get
                If Session(SessionVariables.WorkingSiteID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.WorkingSiteID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.WorkingSiteID.ToString) = value
            End Set
        End Property
        Public Shared Property KPIDataEntryDaily() As Boolean
            Get
                If Session(SessionVariables.KPIDataEntryDaily.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPIDataEntryDaily.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.KPIDataEntryDaily.ToString) = value
            End Set
        End Property
        Public Shared Property KPIDataEntryMode() As Boolean
            Get
                If Session(SessionVariables.KPIDataEntryMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPIDataEntryMode.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.KPIDataEntryMode.ToString) = value
            End Set
        End Property
        Public Shared Property KPIMasterMode() As String
            Get
                If Session(SessionVariables.KPIMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPIMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.KPIMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property KPIReportFilterBusinessAreaID() As Integer
            Get
                If Session(SessionVariables.KPIReportFilterBusinessAreaID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPIReportFilterBusinessAreaID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.KPIReportFilterBusinessAreaID.ToString) = value
            End Set
        End Property
        Public Shared Property KPIReportFilterReportID() As Integer
            Get
                If Session(SessionVariables.KPIReportFilterReportID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPIReportFilterReportID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.KPIReportFilterReportID.ToString) = value
            End Set
        End Property
        Public Shared Property KPIReportFilterSiteID() As Integer
            Get
                If Session(SessionVariables.KPIReportFilterSiteID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPIReportFilterSiteID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.KPIReportFilterSiteID.ToString) = value
            End Set
        End Property
        Public Shared Property KPISelNavMonth() As Integer
            Get
                If Session(SessionVariables.KPISelNavMonth.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPISelNavMonth.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.KPISelNavMonth.ToString) = value
            End Set
        End Property
        Public Shared Property KPISelNavYear() As Integer
            Get
                If Session(SessionVariables.KPISelNavYear.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPISelNavYear.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.KPISelNavYear.ToString) = value
            End Set
        End Property
        Public Shared Property KPISelEditMode() As String
            Get
                If Session(SessionVariables.KPISelEditMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPISelEditMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.KPISelEditMode.ToString) = value
            End Set
        End Property
        Public Shared Property KPITeamMasterMode() As String
            Get
                If Session(SessionVariables.KPITeamMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.KPITeamMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.KPITeamMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property LocationMode() As String
            Get
                If Session(SessionVariables.LocationMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.LocationMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.LocationMode.ToString) = value
            End Set
        End Property
        Public Shared Property LookupRoomItem() As String
            Get
                If Session(SessionVariables.LookupRoomItem.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.LookupRoomItem.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.LookupRoomItem.ToString) = value
            End Set
        End Property
        Public Shared Property RatingScale() As String
            Get
                If Session(SessionVariables.RatingScale.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RatingScale.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RatingScale.ToString) = value
            End Set
        End Property
        Public Shared Property RecordTransactionCurrentValues() As Dictionary(Of String, String)
            Get
                If Session(SessionVariables.RecordTransactionCurrentValues.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RecordTransactionCurrentValues.ToString)
                Else
                    Return New Dictionary(Of String, String)
                End If
            End Get
            Set(ByVal value As Dictionary(Of String, String))
                Session(SessionVariables.RecordTransactionCurrentValues.ToString) = value
            End Set
        End Property
        Public Shared Property RedirectProgram() As String
            Get
                If Session(SessionVariables.RedirectProgram.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RedirectProgram.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RedirectProgram.ToString) = value
            End Set
        End Property
        Public Shared Property RoleMasterMode() As String
            Get
                If Session(SessionVariables.RoleMasterMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RoleMasterMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RoleMasterMode.ToString) = value
            End Set
        End Property
        Public Shared Property RoomReservations() As String
            Get
                If Session(SessionVariables.RoomReservations.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.RoomReservations.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.RoomReservations.ToString) = value
            End Set
        End Property
        Public Shared Property SavedProgram() As String
            Get
                If Session(SessionVariables.SavedProgram.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SavedProgram.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SavedProgram.ToString) = value
            End Set
        End Property
        Public Shared Property SavingsTrackerMode() As String
            Get
                If Session(SessionVariables.SavingsTrackerMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SavingsTrackerMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SavingsTrackerMode.ToString) = value
            End Set
        End Property
        Public Shared Property ScanMode() As String
            Get
                If Session(SessionVariables.ScanMode.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ScanMode.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ScanMode.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedNewMachine() As String
            Get
                If Session(SessionVariables.SelectedNewMachine.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedNewMachine.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedNewMachine.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedTeamID() As Integer
            Get
                If Session(SessionVariables.SelectedTeamID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedTeamID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedTeamID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedTeam() As String
            Get
                If Session(SessionVariables.SelectedTeam.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedTeam.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedTeam.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedTeamName() As String
            Get
                If Session(SessionVariables.SelectedTeamName.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedTeamName.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedTeamName.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedTeamAllowEdit() As Boolean
            Get
                If Session(SessionVariables.SelectedTeamAllowEdit.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedTeamAllowEdit.ToString)
                Else
                    Return False
                End If
            End Get
            Set(ByVal value As Boolean)
                Session(SessionVariables.SelectedTeamAllowEdit.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueDataElement() As String
            Get
                If Session(SessionVariables.SelectedValueDataElement.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueDataElement.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueDataElement.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueDate() As String
            Get
                If Session(SessionVariables.SelectedValueDate.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueDate.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueDate.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueDateTime() As String
            Get
                If Session(SessionVariables.SelectedValueDateTime.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueDateTime.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueDateTime.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueLabelFormat() As String
            Get
                If Session(SessionVariables.SelectedValueLabelFormat.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueLabelFormat.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueLabelFormat.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueLabelGroup() As String
            Get
                If Session(SessionVariables.SelectedValueLabelGroup.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueLabelGroup.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueLabelGroup.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueLocation() As String
            Get
                If Session(SessionVariables.SelectedValueLocation.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueLocation.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueLocation.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueSupplier() As String
            Get
                If Session(SessionVariables.SelectedValueSupplier.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueSupplier.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueSupplier.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueTeamID() As Integer
            Get
                If Session(SessionVariables.SelectedValueTeamID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueTeamID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueTeamID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueTeam() As String
            Get
                If Session(SessionVariables.SelectedValueTeam.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueTeam.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.SelectedValueTeam.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueTeamSiteID() As Integer
            Get
                If Session(SessionVariables.SelectedValueTeamSiteID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueTeamSiteID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueTeamSiteID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueTrackerCollectionID() As Integer
            Get
                If Session(SessionVariables.SelectedValueTrackerCollectionID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueTrackerCollectionID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueTrackerCollectionID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueTrackerID() As Integer
            Get
                If Session(SessionVariables.SelectedValueTrackerID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueTrackerID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueTrackerID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueTrackerPlanID() As Integer
            Get
                If Session(SessionVariables.SelectedValueTrackerPlanID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueTrackerPlanID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueTrackerPlanID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueTrackerPlanSavingsID() As Integer
            Get
                If Session(SessionVariables.SelectedValueTrackerPlanSavingsID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueTrackerPlanSavingsID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueTrackerPlanSavingsID.ToString) = value
            End Set
        End Property
        Public Shared Property SelectedValueTrackerTypeID() As Integer
            Get
                If Session(SessionVariables.SelectedValueTrackerTypeID.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.SelectedValueTrackerTypeID.ToString)
                Else
                    Return 0
                End If
            End Get
            Set(ByVal value As Integer)
                Session(SessionVariables.SelectedValueTrackerTypeID.ToString) = value
            End Set
        End Property
        Public Shared Property ShowAttendance() As String
            Get
                If Session(SessionVariables.ShowAttendance.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ShowAttendance.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ShowAttendance.ToString) = value
            End Set
        End Property
        Public Shared Property ShowAttachments() As String
            Get
                If Session(SessionVariables.ShowAttachments.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ShowAttachments.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ShowAttachments.ToString) = value
            End Set
        End Property
        Public Shared Property ShowCriteria() As String
            Get
                If Session(SessionVariables.ShowCriteria.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ShowCriteria.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ShowCriteria.ToString) = value
            End Set
        End Property
        Public Shared Property ShowPopups() As String
            Get
                If Session(SessionVariables.ShowPopups.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ShowPopups.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ShowPopups.ToString) = value
            End Set
        End Property
        Public Shared Property ShowValues() As String
            Get
                If Session(SessionVariables.ShowValues.ToString) IsNot Nothing Then
                    Return Session(SessionVariables.ShowValues.ToString)
                Else
                    Return String.Empty
                End If
            End Get
            Set(ByVal value As String)
                Session(SessionVariables.ShowValues.ToString) = value
            End Set
        End Property
#End Region

#Region "Subs and Functions"
        Public Shared Sub RemoveSessionVariable(ByVal SessionName As SessionVariables)
            If Session(SessionName.ToString) IsNot Nothing Then
                Session.Remove(SessionName.ToString)
            End If
        End Sub
        Public Shared Function RequestingPageName() As String
            '==========================================================================================
            ' This will get the name of the requesting page
            '==========================================================================================
            Dim strPath As String = System.Web.HttpContext.Current.Request.Url.AbsolutePath
            Dim fiInfo As System.IO.FileInfo = New System.IO.FileInfo(strPath)
            Dim strRet As String = fiInfo.Name

            Return strRet
        End Function
        Public Shared Function GetAllSessionVariables() As Hashtable
            '==========================================================================================
            ' This will get all the session variables and their values
            ' Returns a hashtable 
            '==========================================================================================
            Dim ht As New Hashtable

            Dim x As Integer
            For x = 0 To Session.Contents.Count - 1
                ht.Add(Session.Contents.Keys(x), Session.Contents.Item(x))
            Next

            Return ht
        End Function
#End Region

    End Class
End Namespace
