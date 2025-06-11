# Videoterminal Project Description

The **Videoterminal** project is a comprehensive automated testing suite for a video conferencing terminal system. It focuses on end-to-end verification of video/audio stream parameters, UI interactions, and participant management across a wide variety of use cases. The tests are implemented using `pytest` and are richly annotated with `allure` for detailed test reporting.

## test_bitrate.py
### Purpose:
This file contains a set of Allure-decorated pytest test cases that validate how video bitrate dynamically adjusts based on different framerate (fps) and source scenarios in a video terminal system.

### Main Features:

Parametrized Video Settings: Several dictionaries define different video configurations (low/high fps, various bitrates, resolutions).
wait_assert_statistic: Utility function to wait for a condition/assertion on video stats to become true, retrying with a timeout.
Test Class (TestBitrateResolvedByFps):
Contains multiple test methods, each verifying bitrate and fps adaptation in various call and presentation scenarios (e.g., high/low fps at VCST/source, with slides, with floating fps).
Uses multiple allure steps for structured reporting.
Tests include toggling video transmission, switching camera sources, and checking both statistical measures and visual output (using color checking in frames).
Includes tests for dynamic/floating fps sources and their effects on output bitrate and frame content.

## test_transfer_abonents.py
### Purpose:
This file tests the logic of transferring subscribers ("abonents") between video conferences, specifically handling cases like duplicate numbers, pre-active/active/inactive abonents, and media parameter propagation.

### Main Features:

Test Class (TestTransferAbonents):
Inherits from a base test suite (ITestSuite).
Defines various sets of conference and layout parameters for different test scenarios.
Contains tests (using @pytest.mark.parametrize) for:
Handling transfer of abonents with duplicate numbers and verifying correct handling of user prompts and final abonent status.
Bulk transfer and verification of lists of abonents, especially with duplicate numbers.
Transfers involving abonents in pre-active, active, and inactive states, including between such states.
Checking audio and video output as part of the verification steps.
Transfer of abonents sending a presentation stream, including checks for correct media parameter propagation.
Heavy Use of Allure Steps: Each logical test action is wrapped in an Allure step for rich reporting.
Parallel Execution: Some steps (e.g., audio checks) are performed in parallel for efficiency and realism.

## test_selected_contacts_examples.py
### Main features:

The tests include:
test__search_groups_with_handset: Tests searching for groups (with a handset context), including creating contacts/groups, searching with various arguments, and verifying search results and selection in both list and grid modes.
test__transfer_call_from_favourites: Tests transferring an active call via the “Favorites” widget, checking call states, and verifying call logs and statistics.
Utility Methods for Selection:

contact_should_be_selected and contact_should_be_selected_page: Methods to verify if a contact is selected by name or number under various widgets (contacts, groups, etc.).
get_and_check_first_selected: Checks if the first element in a list is selected and asserts correctness.
Test Structure and Steps:

Each test and utility uses allure.step for detailed step logging.
Markers like @allure.title, @pytest.mark.* are used for organizing and categorizing tests.
The tests simulate UI actions: adding contacts/groups, changing display modes, searching, verifying selections, transferring calls, and checking logs/statistics.

## Technologies Used
- **Python** with `pytest` for automation.
- **Allure** for rich, stepwise test reporting.
- **Custom utilities** for video/image analysis, parallel execution, and UI interaction.

## Typical Use Cases
- Automated regression testing for new firmware or software releases.
- Validating video terminal reliability in handling real-world conferencing scenarios.
- Ensuring high-quality user experience for video, audio, and UI flows.
