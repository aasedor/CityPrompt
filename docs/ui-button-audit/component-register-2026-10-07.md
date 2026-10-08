# Button audit component register — 7 October 2026

Every component/file with an inventoried control appears below. Counts refer to source definitions, not simultaneously visible controls. The complete per-control handler, conditions, route scopes and recommendation are in [the CSV](button-inventory-2026-10-07.csv). See [the report](../COMPLETE_BUTTON_AUDIT_2026-10-07.md) for findings and verification limits.

| Source file | Section | Buttons | Other controls | Inventory IDs | Evidence |
| --- | --- | ---: | ---: | --- | --- |
| [components/buildings/AddBuildingModal.tsx](../../frontend/src/components/buildings/AddBuildingModal.tsx) | New custom assets and assembly | 3 | 3 | C0001–C0006 | Source |
| [components/buildings/AIGenerateModal.tsx](../../frontend/src/components/buildings/AIGenerateModal.tsx) | New custom assets and assembly | 12 | 5 | C0007–C0023 | Source |
| [components/buildings/BuildingReferenceSearch.tsx](../../frontend/src/components/buildings/BuildingReferenceSearch.tsx) | New custom assets and assembly | 1 | 4 | C0024–C0028 | Source |
| [components/buildings/StyleSelector.tsx](../../frontend/src/components/buildings/StyleSelector.tsx) | New custom assets and assembly | 6 | 0 | C0029–C0034 | Source |
| [components/FeedbackWidget.tsx](../../frontend/src/components/FeedbackWidget.tsx) | Help and feedback | 4 | 0 | C0035–C0038 | Source |
| [components/GenerationProgressBar.tsx](../../frontend/src/components/GenerationProgressBar.tsx) | Image job recovery | 3 | 1 | C0039–C0042 | Source |
| [components/layout/Layout.tsx](../../frontend/src/components/layout/Layout.tsx) | Projects and navigation | 4 | 14 | C0043–C0060 | Source + panel inspection |
| [components/layout/ThemeToggle.tsx](../../frontend/src/components/layout/ThemeToggle.tsx) | Projects and navigation | 1 | 0 | C0061–C0061 | Source |
| [components/sharing/ShareModal.tsx](../../frontend/src/components/sharing/ShareModal.tsx) | Sharing and read-only presentation | 9 | 2 | C0062–C0072 | Source + panel inspection |
| [components/ui/ImageLightbox.tsx](../../frontend/src/components/ui/ImageLightbox.tsx) | Saved-media viewing and editing | 3 | 2 | C0073–C0077 | Source |
| [components/ui/UndoRedoButtons.tsx](../../frontend/src/components/ui/UndoRedoButtons.tsx) | Undo and persisted history | 2 | 0 | C0078–C0079 | Source |
| [components/viewer/AIRenderPanel.tsx](../../frontend/src/components/viewer/AIRenderPanel.tsx) | Image generation and styles | 17 | 8 | C0080–C0104 | Source |
| [components/viewer/AnimateRenderButton.tsx](../../frontend/src/components/viewer/AnimateRenderButton.tsx) | Video and local trials | 4 | 3 | C0105–C0111 | Source + panel inspection |
| [components/viewer/BuildingModelViewer.tsx](../../frontend/src/components/viewer/BuildingModelViewer.tsx) | Saved-media viewing and editing | 1 | 3 | C0112–C0115 | Source |
| [components/viewer/CustomStyleEditor.tsx](../../frontend/src/components/viewer/CustomStyleEditor.tsx) | New custom assets and assembly | 3 | 0 | C0116–C0118 | Source |
| [components/viewer/globe/BuildingEntranceReviewPanel.tsx](../../frontend/src/components/viewer/globe/BuildingEntranceReviewPanel.tsx) | Ground and entrance diagnostics | 1 | 0 | C0119–C0119 | Source + panel inspection |
| [components/viewer/globe/BuildingGroundProblems.tsx](../../frontend/src/components/viewer/globe/BuildingGroundProblems.tsx) | Ground and entrance diagnostics | 1 | 0 | C0120–C0120 | Source |
| [components/viewer/globe/GlobeAIRenderPanel.tsx](../../frontend/src/components/viewer/globe/GlobeAIRenderPanel.tsx) | Image generation and styles | 20 | 12 | C0121–C0152 | Source + panel inspection |
| [components/viewer/globe/GlobeEditMode.tsx](../../frontend/src/components/viewer/globe/GlobeEditMode.tsx) | Drawing and camera navigation | 1 | 0 | C0153–C0153 | Source |
| [components/viewer/globe/GlobeSitePlannerMap.tsx](../../frontend/src/components/viewer/globe/GlobeSitePlannerMap.tsx) | Drawing and camera navigation | 29 | 3 | C0154–C0185 | Source + panel inspection |
| [components/viewer/globe/GroundReviewPanel.tsx](../../frontend/src/components/viewer/globe/GroundReviewPanel.tsx) | Ground and entrance diagnostics | 4 | 2 | C0186–C0191 | Source + panel inspection |
| [components/viewer/globe/ImageFidelityReview.tsx](../../frontend/src/components/viewer/globe/ImageFidelityReview.tsx) | Saved-media viewing and editing | 1 | 1 | C0192–C0193 | Source |
| [components/viewer/globe/ImagePresentationControls.tsx](../../frontend/src/components/viewer/globe/ImagePresentationControls.tsx) | Image generation and styles | 1 | 2 | C0194–C0196 | Source + panel inspection |
| [components/viewer/globe/RecoverImageAttempts.tsx](../../frontend/src/components/viewer/globe/RecoverImageAttempts.tsx) | Image job recovery | 5 | 1 | C0197–C0202 | Source |
| [components/viewer/globe/WorkingViewPerformance.tsx](../../frontend/src/components/viewer/globe/WorkingViewPerformance.tsx) | Performance and context | 1 | 1 | C0203–C0204 | Source + panel inspection |
| [components/viewer/HistoryPanel.tsx](../../frontend/src/components/viewer/HistoryPanel.tsx) | Undo and persisted history | 6 | 1 | C0205–C0211 | Source + panel inspection |
| [components/viewer/ImageModelSelect.tsx](../../frontend/src/components/viewer/ImageModelSelect.tsx) | Image generation and styles | 0 | 1 | C0212–C0212 | Source + panel inspection |
| [components/viewer/LayoutPreviewPanel.tsx](../../frontend/src/components/viewer/LayoutPreviewPanel.tsx) | AI site analysis and landscape | 10 | 3 | C0213–C0225 | Source |
| [components/viewer/LocalComfyTrialButton.tsx](../../frontend/src/components/viewer/LocalComfyTrialButton.tsx) | Video and local trials | 6 | 4 | C0226–C0235 | Source + panel inspection |
| [components/viewer/OnboardingTour.tsx](../../frontend/src/components/viewer/OnboardingTour.tsx) | Help and feedback | 3 | 0 | C0236–C0238 | Source + panel inspection |
| [components/viewer/RenderEditModal.tsx](../../frontend/src/components/viewer/RenderEditModal.tsx) | Saved-media viewing and editing | 7 | 2 | C0239–C0247 | Source + panel inspection |
| [components/viewer/RenderResultModal.tsx](../../frontend/src/components/viewer/RenderResultModal.tsx) | Saved-media viewing and editing | 5 | 4 | C0248–C0256 | Source |
| [components/viewer/RenderStyleGuide.tsx](../../frontend/src/components/viewer/RenderStyleGuide.tsx) | Image generation and styles | 4 | 1 | C0257–C0261 | Source |
| [components/viewer/RenderStyleGuideButton.tsx](../../frontend/src/components/viewer/RenderStyleGuideButton.tsx) | Image generation and styles | 1 | 0 | C0262–C0262 | Source |
| [components/viewer/SiteIntelligencePanel.tsx](../../frontend/src/components/viewer/SiteIntelligencePanel.tsx) | AI site analysis and landscape | 14 | 2 | C0263–C0278 | Source + panel inspection |
| [components/viewer/SitePlannerMap.tsx](../../frontend/src/components/viewer/SitePlannerMap.tsx) | Drawing and camera navigation | 4 | 0 | C0279–C0282 | Source |
| [components/viewer/SitePlannerToolbar.tsx](../../frontend/src/components/viewer/SitePlannerToolbar.tsx) | Drawing and camera navigation | 14 | 0 | C0283–C0296 | Source + panel inspection |
| [components/viewer/StreetViewPanel.tsx](../../frontend/src/components/viewer/StreetViewPanel.tsx) | Video and local trials | 22 | 5 | C0297–C0323 | Source |
| [components/viewer/VideoGeneratePanel.tsx](../../frontend/src/components/viewer/VideoGeneratePanel.tsx) | Video and local trials | 15 | 4 | C0324–C0342 | Source + panel inspection |
| [components/viewer/WorkflowStepper.tsx](../../frontend/src/components/viewer/WorkflowStepper.tsx) | Workflow and project composition | 1 | 0 | C0343–C0343 | Source |
| [components/viewer/ZoneLegend.tsx](../../frontend/src/components/viewer/ZoneLegend.tsx) | Drawing and camera navigation | 2 | 0 | C0344–C0345 | Source |
| [components/viewer/ZonePropertiesPanel.tsx](../../frontend/src/components/viewer/ZonePropertiesPanel.tsx) | Selected-object editing | 44 | 12 | C0346–C0401 | Source + panel inspection |
| [dev/NativeParkReview.tsx](../../frontend/src/dev/NativeParkReview.tsx) | Developer review fixtures | 0 | 2 | C0402–C0403 | Source |
| [dev/NeighborhoodParkPilotReview.tsx](../../frontend/src/dev/NeighborhoodParkPilotReview.tsx) | Developer review fixtures | 1 | 2 | C0404–C0406 | Source |
| [dev/ParkTrioReview.tsx](../../frontend/src/dev/ParkTrioReview.tsx) | Developer review fixtures | 1 | 3 | C0407–C0410 | Source |
| [features/admin/AdminBuildingsPage.tsx](../../frontend/src/features/admin/AdminBuildingsPage.tsx) | Staff administration | 8 | 7 | C0411–C0425 | Source |
| [features/admin/AdminDashboardPage.tsx](../../frontend/src/features/admin/AdminDashboardPage.tsx) | Staff administration | 0 | 2 | C0426–C0427 | Source |
| [features/admin/AdminFeedbackPage.tsx](../../frontend/src/features/admin/AdminFeedbackPage.tsx) | Staff administration | 5 | 0 | C0428–C0432 | Source |
| [features/admin/AdminProjectsPage.tsx](../../frontend/src/features/admin/AdminProjectsPage.tsx) | Staff administration | 0 | 3 | C0433–C0435 | Source |
| [features/admin/AdminRenderLogsPage.tsx](../../frontend/src/features/admin/AdminRenderLogsPage.tsx) | Staff administration | 11 | 14 | C0436–C0460 | Source |
| [features/admin/AdminUsersPage.tsx](../../frontend/src/features/admin/AdminUsersPage.tsx) | Staff administration | 6 | 3 | C0461–C0469 | Source |
| [features/admin/analytics/ApiBalancesWidget.tsx](../../frontend/src/features/admin/analytics/ApiBalancesWidget.tsx) | Staff administration | 1 | 0 | C0470–C0470 | Source |
| [features/admin/analytics/ApiUsageChart.tsx](../../frontend/src/features/admin/analytics/ApiUsageChart.tsx) | Staff administration | 2 | 0 | C0471–C0472 | Source |
| [features/admin/analytics/TimeRangeSelector.tsx](../../frontend/src/features/admin/analytics/TimeRangeSelector.tsx) | Staff administration | 1 | 0 | C0473–C0473 | Source |
| [features/admin/CofounderAnalyticsPage.tsx](../../frontend/src/features/admin/CofounderAnalyticsPage.tsx) | Staff administration | 0 | 2 | C0474–C0475 | Source |
| [features/admin/ConfirmRoleChangePage.tsx](../../frontend/src/features/admin/ConfirmRoleChangePage.tsx) | Staff administration | 0 | 1 | C0476–C0476 | Source |
| [features/auth/AuthPageShell.tsx](../../frontend/src/features/auth/AuthPageShell.tsx) | Authentication | 0 | 2 | C0477–C0478 | Source |
| [features/auth/ChangePasswordPage.tsx](../../frontend/src/features/auth/ChangePasswordPage.tsx) | Authentication | 4 | 0 | C0479–C0482 | Source |
| [features/auth/ForgotPasswordPage.tsx](../../frontend/src/features/auth/ForgotPasswordPage.tsx) | Authentication | 1 | 2 | C0483–C0485 | Source |
| [features/auth/LoginPage.tsx](../../frontend/src/features/auth/LoginPage.tsx) | Authentication | 2 | 2 | C0486–C0489 | Source |
| [features/auth/OAuthButtons.tsx](../../frontend/src/features/auth/OAuthButtons.tsx) | Authentication | 1 | 0 | C0490–C0490 | Source |
| [features/auth/RegisterPage.tsx](../../frontend/src/features/auth/RegisterPage.tsx) | Authentication | 2 | 1 | C0491–C0493 | Source |
| [features/auth/ResetPasswordPage.tsx](../../frontend/src/features/auth/ResetPasswordPage.tsx) | Authentication | 3 | 1 | C0494–C0497 | Source |
| [features/calgaryCatalogue/CatalogueBrowser.tsx](../../frontend/src/features/calgaryCatalogue/CatalogueBrowser.tsx) | Catalogue | 2 | 7 | C0498–C0506 | Source + panel inspection |
| [features/context/ContextControls.tsx](../../frontend/src/features/context/ContextControls.tsx) | Performance and context | 0 | 1 | C0507–C0507 | Source |
| [features/landing/LandingPage.tsx](../../frontend/src/features/landing/LandingPage.tsx) | Projects and navigation | 0 | 6 | C0508–C0513 | Source |
| [features/legoAssembly/LegoAssemblyPreview.tsx](../../frontend/src/features/legoAssembly/LegoAssemblyPreview.tsx) | New custom assets and assembly | 9 | 3 | C0514–C0525 | Source |
| [features/legoAssembly/LegoBuilderPanel.tsx](../../frontend/src/features/legoAssembly/LegoBuilderPanel.tsx) | New custom assets and assembly | 7 | 2 | C0526–C0534 | Source + panel inspection |
| [features/parks/ParkLayoutControls.tsx](../../frontend/src/features/parks/ParkLayoutControls.tsx) | Selected-object editing | 3 | 1 | C0535–C0538 | Source |
| [features/pickPlace/BrtStopControls.tsx](../../frontend/src/features/pickPlace/BrtStopControls.tsx) | Selected-object editing | 4 | 0 | C0539–C0542 | Source |
| [features/pickPlace/BuildingDesignControls.tsx](../../frontend/src/features/pickPlace/BuildingDesignControls.tsx) | Selected-object editing | 1 | 3 | C0543–C0546 | Source |
| [features/pickPlace/CanonicalCatalogueCard.tsx](../../frontend/src/features/pickPlace/CanonicalCatalogueCard.tsx) | Catalogue | 1 | 1 | C0547–C0548 | Source + panel inspection |
| [features/pickPlace/CatalogueFacetControls.tsx](../../frontend/src/features/pickPlace/CatalogueFacetControls.tsx) | Catalogue | 0 | 4 | C0549–C0552 | Source + panel inspection |
| [features/pickPlace/ConnectionEditor.tsx](../../frontend/src/features/pickPlace/ConnectionEditor.tsx) | Connections and terraces | 6 | 6 | C0553–C0564 | Source + panel inspection |
| [features/pickPlace/ParkComponentControls.tsx](../../frontend/src/features/pickPlace/ParkComponentControls.tsx) | Selected-object editing | 1 | 1 | C0565–C0566 | Source |
| [features/pickPlace/PlacementControls.tsx](../../frontend/src/features/pickPlace/PlacementControls.tsx) | Drawing and camera navigation | 0 | 1 | C0567–C0567 | Source |
| [features/pickPlace/PlacementPalette.tsx](../../frontend/src/features/pickPlace/PlacementPalette.tsx) | Catalogue | 9 | 2 | C0568–C0578 | Source + panel inspection |
| [features/pickPlace/ReshapePanel.tsx](../../frontend/src/features/pickPlace/ReshapePanel.tsx) | Selected-object editing | 8 | 1 | C0579–C0587 | Source + panel inspection |
| [features/pickPlace/StreetCrossSection.tsx](../../frontend/src/features/pickPlace/StreetCrossSection.tsx) | Selected-object editing | 0 | 1 | C0588–C0588 | Source |
| [features/pickPlace/StreetDesignControls.tsx](../../frontend/src/features/pickPlace/StreetDesignControls.tsx) | Selected-object editing | 1 | 3 | C0589–C0592 | Source |
| [features/pickPlace/StreetDuplicateControls.tsx](../../frontend/src/features/pickPlace/StreetDuplicateControls.tsx) | Selected-object editing | 3 | 0 | C0593–C0595 | Source |
| [features/pickPlace/StreetRoutePanel.tsx](../../frontend/src/features/pickPlace/StreetRoutePanel.tsx) | Selected-object editing | 5 | 1 | C0596–C0601 | Source |
| [features/pickPlace/TerraceEditor.tsx](../../frontend/src/features/pickPlace/TerraceEditor.tsx) | Connections and terraces | 4 | 4 | C0602–C0609 | Source + panel inspection |
| [features/pickPlace/TerraceSummary.tsx](../../frontend/src/features/pickPlace/TerraceSummary.tsx) | Connections and terraces | 1 | 0 | C0610–C0610 | Source |
| [features/pickPlace/UserGeneratedBuildings.tsx](../../frontend/src/features/pickPlace/UserGeneratedBuildings.tsx) | Catalogue | 2 | 1 | C0611–C0613 | Source |
| [features/policyPlans/CityPolicyDetailsCard.tsx](../../frontend/src/features/policyPlans/CityPolicyDetailsCard.tsx) | Policy and zoning guidance | 1 | 2 | C0614–C0616 | Source + panel inspection |
| [features/policyPlans/CityPolicyMapsPanel.tsx](../../frontend/src/features/policyPlans/CityPolicyMapsPanel.tsx) | Policy and zoning guidance | 3 | 3 | C0617–C0622 | Source + panel inspection |
| [features/policyPlans/LocalAreaPlanPanel.tsx](../../frontend/src/features/policyPlans/LocalAreaPlanPanel.tsx) | Policy and zoning guidance | 2 | 8 | C0623–C0632 | Source + panel inspection |
| [features/policyPlans/PolicyDetailsCard.tsx](../../frontend/src/features/policyPlans/PolicyDetailsCard.tsx) | Policy and zoning guidance | 1 | 1 | C0633–C0634 | Source |
| [features/projects/InvitationPage.tsx](../../frontend/src/features/projects/InvitationPage.tsx) | Sharing and read-only presentation | 3 | 2 | C0635–C0639 | Source |
| [features/projects/LayersPanel.tsx](../../frontend/src/features/projects/LayersPanel.tsx) | Reference context and assessment | 5 | 0 | C0640–C0644 | Source |
| [features/projects/ProjectEditModal.tsx](../../frontend/src/features/projects/ProjectEditModal.tsx) | Projects and navigation | 4 | 0 | C0645–C0648 | Source + panel inspection |
| [features/projects/ProjectListPage.tsx](../../frontend/src/features/projects/ProjectListPage.tsx) | Projects and navigation | 10 | 5 | C0649–C0663 | Source + panel inspection |
| [features/projects/ProjectViewPage.tsx](../../frontend/src/features/projects/ProjectViewPage.tsx) | Workflow and project composition | 23 | 15 | C0664–C0701 | Source + panel inspection |
| [features/projects/ReadOnlyProject.tsx](../../frontend/src/features/projects/ReadOnlyProject.tsx) | Sharing and read-only presentation | 1 | 2 | C0702–C0704 | Source |
| [features/projects/SavedRenderCard.tsx](../../frontend/src/features/projects/SavedRenderCard.tsx) | Saved-media viewing and editing | 1 | 0 | C0705–C0705 | Source |
| [features/projects/SharedPlanPreview.tsx](../../frontend/src/features/projects/SharedPlanPreview.tsx) | Sharing and read-only presentation | 0 | 3 | C0706–C0708 | Source |
| [features/projects/SharedProjectPage.tsx](../../frontend/src/features/projects/SharedProjectPage.tsx) | Sharing and read-only presentation | 2 | 2 | C0709–C0712 | Source |
| [features/projects/StudentWorkflow.tsx](../../frontend/src/features/projects/StudentWorkflow.tsx) | Workflow and project composition | 8 | 0 | C0713–C0720 | Source + panel inspection |
| [features/projects/StudioControls.tsx](../../frontend/src/features/projects/StudioControls.tsx) | Workflow and project composition | 9 | 0 | C0721–C0729 | Source + panel inspection |
| [features/referenceLayers/CalgaryContextButton.tsx](../../frontend/src/features/referenceLayers/CalgaryContextButton.tsx) | Reference context and assessment | 1 | 0 | C0730–C0730 | Source |
| [features/referenceLayers/CalgaryDistrictSelect.tsx](../../frontend/src/features/referenceLayers/CalgaryDistrictSelect.tsx) | Policy and zoning guidance | 0 | 1 | C0731–C0731 | Source |
| [features/referenceLayers/ReferenceImportButton.tsx](../../frontend/src/features/referenceLayers/ReferenceImportButton.tsx) | Reference context and assessment | 4 | 1 | C0732–C0736 | Source |
| [features/referenceLayers/ReferenceLayersPanel.tsx](../../frontend/src/features/referenceLayers/ReferenceLayersPanel.tsx) | Reference context and assessment | 7 | 2 | C0737–C0745 | Source + panel inspection |
| [features/referenceLayers/SiteAssessmentPanel.tsx](../../frontend/src/features/referenceLayers/SiteAssessmentPanel.tsx) | Reference context and assessment | 1 | 2 | C0746–C0748 | Source + panel inspection |
| [features/referenceLayers/SiteElevation.tsx](../../frontend/src/features/referenceLayers/SiteElevation.tsx) | Reference context and assessment | 1 | 1 | C0749–C0750 | Source + panel inspection |
| [features/referenceLayers/StudyEditorShell.tsx](../../frontend/src/features/referenceLayers/StudyEditorShell.tsx) | Proposed zoning drawing | 2 | 0 | C0751–C0752 | Source + panel inspection |
| [features/referenceLayers/ZoningLabelsControls.tsx](../../frontend/src/features/referenceLayers/ZoningLabelsControls.tsx) | Proposed zoning drawing | 2 | 7 | C0753–C0761 | Source |
| [features/referenceLayers/ZoningStudyEditor.tsx](../../frontend/src/features/referenceLayers/ZoningStudyEditor.tsx) | Proposed zoning drawing | 18 | 6 | C0762–C0785 | Source + panel inspection |
| [features/referenceLayers/ZoningStudyPanel.tsx](../../frontend/src/features/referenceLayers/ZoningStudyPanel.tsx) | Proposed zoning drawing | 1 | 1 | C0786–C0787 | Source + panel inspection |
| [features/siteLandscape/SiteLandscapePanel.tsx](../../frontend/src/features/siteLandscape/SiteLandscapePanel.tsx) | AI site analysis and landscape | 4 | 2 | C0788–C0793 | Source |
| [features/studentReports/StudentPlanningReport.tsx](../../frontend/src/features/studentReports/StudentPlanningReport.tsx) | Planning report | 5 | 5 | C0794–C0803 | Source + panel inspection |
| [features/zoningCatalogue/ZoningCatalogueCard.tsx](../../frontend/src/features/zoningCatalogue/ZoningCatalogueCard.tsx) | Policy and zoning guidance | 2 | 6 | C0804–C0811 | Source |
| [main.tsx](../../frontend/src/main.tsx) | Application crash recovery | 1 | 0 | C0812–C0812 | Source |
| [review/nativeStreetMixedJunctionReview.tsx](../../frontend/src/review/nativeStreetMixedJunctionReview.tsx) | Developer review fixtures | 2 | 0 | C0813–C0814 | Source |
