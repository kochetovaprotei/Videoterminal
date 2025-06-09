import pytest
import allure
from time import sleep
from test_suites.common.ITestSuite import ITestSuite
from test_suites.common.slides_params import *
from test_suites.common.videofiles_params import *
from library.vcst_interface.keywords.Resolution_keywords import Resolution
from library.vcst_interface.keywords.CheckVideo import CheckVideo
from library.vcst_interface.configuration import empty_slot_vcss, speaker_vcss, white, blue, yellow, red, \
    tester_2_presentation
from library.vcst_interface.vcst_consts import tester_sinks, tester2_sinks, tone, tester_npy, tester2_npy
from common.parallel import RunParallel
from common.audio.Sound_keywords import check_sound
from common.decorators import testit_id, testit_class
from ..common.layout_params import layout_with_auto_slots
from common.keywords.CheckVideo.CheckVideoVcss import CheckVideoVcss


virtual_audio = [{"tester": True, "tester_2": True}]


# TODO: Добавить проверку картинки после переноса (кажется есть кейсы, в которых нет)
@testit_class
@allure.feature("003. Абоненты (Abonents)")
@allure.story("Перенос между конференциями")
@pytest.mark.usefixtures("vcss_default")
@pytest.mark.gui
class TestTransferAbonents(ITestSuite):
    protocol = ["SIP", "H.323"]
    custom_params = {"fps": "60",
                     "presentation_aspect_ratio": "4:3",
                     "layout_fill_type": "Автоматическое",
                     "layout_type_auto": "Только докладчик",
                     "dtmf_sending_mode": "INFO",
                     "operators_rights": "true",
                     "adjust_effective_resolution": "false"}
    default_params = {"fps": "25",
                      "presentation_aspect_ratio": "Любое",
                      "layout_fill_type": "Автоматическое",
                      "layout_type_auto": "Обычная сетка",
                      "dtmf_sending_mode": "Авто",
                      "operators_rights": "false",
                      "adjust_effective_resolution": "false"}
    new_custom_params = {"fps": "40",
                         "presentation_aspect_ratio": "16:9",
                         "layout_fill_type": "Автоматическое",
                         "layout_type_auto": "Докладчик крупным планом",
                         "dtmf_sending_mode": "RTP",
                         "operators_rights": "false",
                         "adjust_effective_resolution": "true"}

    layout_and_image = [
        {
            "layout": "Обычная сетка",
            "slots": [white, "tester_2"],
            "type_layout": "grid"
        },
        {
            "layout": "Только докладчик",
            "slots": ["tester_2"],
            "type_layout": "only_speaker"
        },
        {
            "layout": "Докладчик крупным планом",
            "slots": ["tester_2", white],
            "type_layout": "speaker"
        },
        {
            "layout": "Только презентация",
            "slots": [tester_2_presentation["color"]],
            "type_layout": "only_presentation"
        }
    ]
       
 @testit_id(128477)
    @allure.title("Medium: Перенос активного абонента в конференцию, "
                  "в которой есть абонент с таким же номером и он активен")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_same_number_abonent_transfer_active_abonent_to_active(self, admin_create_two_conferences, tester,
                                                                   outgoing_call_protocol):
        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]
        text = f'Перенести абонентов с дублирующимися номерами?\n"Переносимый ({tester_number})"'
        with allure.step("Создание конференций и абонентов"):
            admin = admin_create_two_conferences
            admin.abonent.create_abonent(abonent_number=tester_number, abonent_name='Переносимый')
            admin.abonent.create_abonent(abonent_number=tester_number, abonent_name='Статичный',
                                         conference=self.layout_name)

        with allure.step("Активировать конференции"):
            params_conference = {
                "signal_protocol": outgoing_call_protocol
            }
            admin.conference.change_parameters(params=params_conference)
            admin.conference.change_parameters(params=params_conference, conference=self.layout_name)
            admin.conference.activate_conference()
            tester.call.accept_incoming_call()
            admin.abonent.check_state(abonent_number=tester_number,
                                      abonent_name='Переносимый',
                                      abonent_state=self.state["active"])
            admin.conference.activate_conference(conference=self.layout_name)
            tester.call.accept_incoming_call(conference=True)
            admin.abonent.check_state(abonent_number=tester_number,
                                      abonent_name='Статичный',
                                      conference=self.layout_name,
                                      abonent_state=self.state["active"])

        with allure.step("Перенос первого абонента из конференции 1 в конференцию 2, отказываемся переносить абонента"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            abonent_name='Переносимый',
                                                            conference2=self.layout_name,
                                                            duplicate=False,
                                                            text=text)

        with allure.step("Проверка, что абонент не перенесен"):
            admin.abonent.check_abonent_exist(abonent_number=tester_number, abonent_name='Переносимый')
            admin.abonent.check_abonent_not_exist(conference=self.layout_name, abonent_number=tester_number,
                                                  abonent_name='Переносимый')

        with allure.step("Перенос первого абонента из конференции 1 в конференцию 2"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            abonent_name='Переносимый',
                                                            conference2=self.layout_name,
                                                            duplicate=True,
                                                            text=text)

        with allure.step("Проверка, что абонента нет в первой конференции"):
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number, abonent_name='Переносимый')
        with allure.step("Проверка, что абонент есть во второй конференции"):
            admin.abonent.check_abonent_exist(abonent_number=tester_number, abonent_name='Переносимый',
                                              conference=self.layout_name)

        with allure.step("Проверка, что оба абонента активны во второй конференции"):
            admin.abonent.check_state(abonent_number=tester_number,
                                      abonent_name='Переносимый',
                                      conference=self.layout_name,
                                      abonent_state=self.state["active"])
            admin.abonent.check_state(abonent_number=tester_number,
                                      abonent_name='Статичный',
                                      conference=self.layout_name,
                                      abonent_state=self.state["active"])

        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()
                    
  @testit_id(128481)
    @allure.title("Перенос  нескольких абонентов с проверкой перечня дублирующихся номеров")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_few_inactive_dublicate_abonents_transfer(self, admin_create_two_conferences, outgoing_call_protocol):

        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_2_numbers = {'SIP': self.tester_2_sip_number, 'H.323': self.tester_2_h323_number}
        tester_3_numbers = {'SIP': self.tester_3_sip_number, 'H.323': self.tester_3_h323_number}
        tester_4_numbers = {'SIP': self.tester_4_sip_number, 'H.323': self.tester_4_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]
        tester_2_number = tester_2_numbers[outgoing_call_protocol]
        tester_3_number = tester_3_numbers[outgoing_call_protocol]
        tester_4_number = tester_4_numbers[outgoing_call_protocol]
        params_conference = {
            "signal_protocol": outgoing_call_protocol
        }
        text = (f'Перенести абонентов с дублирующимися номерами?\n"Переносимый 1 ({tester_number})", '
                f'"Переносимый 3 ({tester_3_number})"')
        with allure.step("Создание конференций"):
            admin = admin_create_two_conferences
            admin.conference.change_parameters(params=params_conference)
            admin.conference.change_parameters(params=params_conference, conference=self.layout_name)
            admin.abonent.create_abonent(abonent_number=tester_number, abonent_name='Переносимый 1')
            admin.abonent.create_abonent(abonent_number=tester_2_number, abonent_name='Переносимый 2')
            admin.abonent.create_abonent(abonent_number=tester_3_number, abonent_name='Переносимый 3')
            admin.abonent.create_abonent(abonent_number=tester_4_number, abonent_name='Переносимый 4')
            admin.abonent.create_abonent(abonent_number=tester_number, abonent_name='Статичный 1',
                                         conference=self.layout_name)
            admin.abonent.create_abonent(abonent_number=tester_3_number, abonent_name='Статичный 3',
                                         conference=self.layout_name)
        with allure.step("Сбор участников"):
            admin.conference.activate_conference()
            admin.abonent.deactivate_abonent(abonent_number=tester_number, abonent_name='Переносимый 1',
                                             check_state=False)
            admin.abonent.deactivate_abonent(abonent_number=tester_2_number, abonent_name='Переносимый 2',
                                             check_state=False)
            admin.abonent.deactivate_abonent(abonent_number=tester_3_number, abonent_name='Переносимый 3',
                                             check_state=False)
            admin.abonent.deactivate_abonent(abonent_number=tester_4_number, abonent_name='Переносимый 4',
                                             check_state=False)
            admin.conference.activate_conference(conference=self.layout_name)
            admin.abonent.deactivate_abonent(abonent_number=tester_number, conference=self.layout_name,
                                             abonent_name='Статичный 1', check_state=False)
            admin.abonent.deactivate_abonent(abonent_number=tester_3_number, conference=self.layout_name,
                                             abonent_name='Статичный 3', check_state=False)
        with allure.step("Перенос абонентов 1,2,3"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            abonent_name='Переносимый 1',
                                                            duplicate=False,
                                                            conference2=self.layout_name,
                                                            text=text,
                                                            count=3)
            admin.abonent.check_abonent_exist(abonent_number=tester_2_number, abonent_name='Переносимый 2',
                                              conference=self.layout_name)
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number, abonent_name='Переносимый 1',
                                                  conference=self.layout_name)
            admin.abonent.check_abonent_not_exist(abonent_number=tester_3_number, abonent_name='Переносимый 3',
                                                  conference=self.layout_name)
        with allure.step("Перенос абонентов 1,3,4"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            abonent_name='Переносимый 1',
                                                            duplicate=True,
                                                            conference2=self.layout_name,
                                                            text=text,
                                                            count=3)
            admin.abonent.check_abonent_exist(abonent_number=tester_number, abonent_name='Переносимый 1',
                                              conference=self.layout_name)
            admin.abonent.check_abonent_exist(abonent_number=tester_3_number, abonent_name='Переносимый 3',
                                              conference=self.layout_name)
            admin.abonent.check_abonent_exist(abonent_number=tester_4_number, abonent_name='Переносимый 4',
                                              conference=self.layout_name)
        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()           
           
@testit_id(128484)
    @allure.title("Medium: Перенос  предактивного абонента из предактивной конференции в предактивную")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_pre_active_abonent_transfer_pre_active_to_pre_active(self, admin_create_two_conferences, tester,
                                                                  outgoing_call_protocol):

        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]

        with allure.step("Создание конференций и абонента"):
            admin = admin_create_two_conferences
            admin.abonent.create_abonent(abonent_number=tester_number)

        with allure.step("Изменить параметры и перевести конференции в режим ожидания"):
            params_conference = {
                "signal_protocol": outgoing_call_protocol,
                "pre_activation_duration": "10"
            }
            admin.conference.change_parameters(params=params_conference)
            admin.conference.change_parameters(params=params_conference, conference=self.layout_name)
            admin.conference.activate_conference(pre_activate=True)
            admin.conference.activate_conference(pre_activate=True, conference=self.layout_name)

        with allure.step("Активировать абонента"):
            admin.abonent.activate_abonent(abonent_number=tester_number, check_state=False)
            tester.call.accept_incoming_call()
        with allure.step("Проверка, что абонент в предактивном состоянии"):
            admin.abonent.check_state(abonent_number=tester_number, abonent_state=self.state["pre_active"])

        with allure.step("Перенос абонента из предактивной конференции в предактивную"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            conference2=self.layout_name)
        with allure.step("Проверка, что абонента нет в первой конференции"):
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number)
        with allure.step("Проверка, что абонент есть во второй конференции и что он предактивен"):
            admin.abonent.check_abonent_exist(conference=self.layout_name, abonent_number=tester_number)
            admin.abonent.check_state(abonent_number=tester_number, conference=self.layout_name,
                                      abonent_state=self.state["pre_active"])

        with allure.step("Проверка звука и заставки получаемого ВКСТ в режиме ожидания"):
            check_sound(application=tester, stream_name=tester_sinks["headset"]["name"], np_path=tone["wait_start"])
            CheckVideo.check_video_conference(phone=tester, slots=[red])

        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()

    @testit_id(128485)
    @allure.title("Medium: Перенос предактивного абонента из предактивной конференции в активную")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.usefixtures("tester_2")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_pre_active_abonent_transfer_pre_active_to_active(self, admin_create_two_conferences, tester, tester_2,
                                                              outgoing_call_protocol):

        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_2_numbers = {'SIP': self.tester_2_sip_number, 'H.323': self.tester_2_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]
        tester_2_number = tester_2_numbers[outgoing_call_protocol]

        with allure.step("Создание конференций и абонентов"):
            admin = admin_create_two_conferences
            admin.abonent.create_abonent(abonent_number=tester_number)
            admin.abonent.create_abonent(abonent_number=tester_2_number, conference=self.layout_name)

        with allure.step("Изменить параметры и перевести первую конференцию в режим ожидания"):
            params_conference = {
                "signal_protocol": outgoing_call_protocol,
                "pre_activation_duration": "10"
            }
            admin.conference.change_parameters(params=params_conference)
            admin.conference.activate_conference(pre_activate=True)

        with allure.step("Активировать абонента"):
            admin.abonent.activate_abonent(abonent_number=tester_number, check_state=False)
            tester.call.accept_incoming_call()
        with allure.step("Проверка, что абонент в предактивном состоянии"):
            admin.abonent.check_state(abonent_number=tester_number, abonent_state=self.state["pre_active"])

        with allure.step("Активировать вторую конференцию c абонентом 2"):
            params_conference_2 = {
                "signal_protocol": outgoing_call_protocol
            }
            admin.conference.change_parameters(params=params_conference_2, conference=self.layout_name)
            admin.conference.activate_conference(conference=self.layout_name)
        with allure.step("Принять вызов на тестере 2"):
            tester_2.call.accept_incoming_call()

        with allure.step("Перенос абонента из предактивной конференции в активную"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            conference2=self.layout_name)
        with allure.step("Проверка, что абонента нет в первой конференции"):
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number)
        with allure.step("Проверка, что абонент есть во второй конференции и что он активен"):
            admin.abonent.check_abonent_exist(conference=self.layout_name, abonent_number=tester_number)
            admin.abonent.check_state(abonent_number=tester_number, conference=self.layout_name,
                                      abonent_state=self.state["active"])

        with allure.step('Проверка получаемой картинки на абонентах'):
            CheckVideo.check_video_conference(phone=tester, slots=["tester_2"])
            CheckVideo.check_video_conference(phone=tester_2, slots=["tester"])

        with allure.step("Проверка звука на абонентах"):
            with RunParallel() as parallel:
                parallel.execute(target=check_sound,
                                 kwargs={"application": tester,
                                         "stream_name": tester_sinks["headset"]["name"],
                                         "np_path": tester2_npy["headset"]})
                parallel.execute(target=check_sound,
                                 kwargs={"application": tester_2,
                                         "stream_name": tester2_sinks["headset"]["name"],
                                         "np_path": tester_npy["headset"]})

        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()

    @testit_id(128486)
    @allure.title("Medium: Перенос  неактивного абонента из предактивной конференции в предактивную")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_inactive_abonent_transfer_pre_active_to_pre_active(self, admin_create_two_conferences,
                                                                outgoing_call_protocol):
        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]

        with allure.step("Создание конференций и абонента"):
            admin = admin_create_two_conferences
            admin.abonent.create_abonent(abonent_number=tester_number)

        with allure.step("Изменить параметры и перевести конференции в режим ожидания"):
            params_conference = {
                "signal_protocol": outgoing_call_protocol,
                "pre_activation_duration": "10"
            }
            admin.conference.change_parameters(params=params_conference)
            admin.conference.change_parameters(params=params_conference, conference=self.layout_name)
            admin.conference.activate_conference(pre_activate=True)
            admin.conference.activate_conference(pre_activate=True, conference=self.layout_name)

        with allure.step("Проверка, что абонент в неактивном состоянии"):
            admin.abonent.check_state(abonent_number=tester_number, abonent_state=self.state["inactive"])

        with allure.step("Перенос абонента из предактивной конференции в предактивную"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            conference2=self.layout_name)
        with allure.step("Проверка, что абонента нет в первой конференции"):
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number)
        with allure.step("Проверка, что абонент есть во второй конференции и что он неактивен"):
            admin.abonent.check_abonent_exist(conference=self.layout_name, abonent_number=tester_number)
            admin.abonent.check_state(abonent_number=tester_number, conference=self.layout_name,
                                      abonent_state=self.state["inactive"])

        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()

    @testit_id(128487)
    @allure.title("Medium: Перенос неактивного абонента из предактивной конференции в активную")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_inactive_abonent_transfer_pre_active_to_active(self, admin_create_two_conferences, outgoing_call_protocol):

        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]

        with allure.step("Создание конференций и абонента"):
            admin = admin_create_two_conferences
            admin.abonent.create_abonent(abonent_number=tester_number)

        with allure.step("Изменить параметры и перевести первую конференцию в режим ожидания"):
            params_conference = {
                "signal_protocol": outgoing_call_protocol,
                "pre_activation_duration": "10"
            }
            admin.conference.change_parameters(params=params_conference)
            admin.conference.activate_conference(pre_activate=True)

        with allure.step("Активировать вторую конференцию"):
            params_conference_2 = {
                "signal_protocol": outgoing_call_protocol
            }
            admin.conference.change_parameters(params=params_conference_2, conference=self.layout_name)
            admin.conference.activate_conference(conference=self.layout_name)

        with allure.step("Проверка, что абонент в неактивном состоянии"):
            admin.abonent.check_state(abonent_number=tester_number, abonent_state=self.state["inactive"])

        with allure.step("Перенос абонента из предактивной конференции в активную"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            conference2=self.layout_name)
        with allure.step("Проверка, что абонента нет в первой конференции"):
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number)
        with allure.step("Проверка, что абонент есть во второй конференции и что он неактивен"):
            admin.abonent.check_abonent_exist(conference=self.layout_name, abonent_number=tester_number)
            admin.abonent.check_state(abonent_number=tester_number, conference=self.layout_name,
                                      abonent_state=self.state["inactive"])

        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()

    @testit_id(128488)
    @allure.title("Medium: Перенос неактивного абонента из активной конференции в предактивную")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_inactive_abonent_transfer_active_to_pre_active(self, admin_create_two_conferences,
                                                            outgoing_call_protocol):

        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]

        with allure.step("Создание конференций и абонента"):
            admin = admin_create_two_conferences
            admin.abonent.create_abonent(abonent_number=tester_number)

        with allure.step("Активировать первую конференцию и деактивировать абонента"):
            params_conference = {
                "signal_protocol": outgoing_call_protocol
            }
            admin.conference.change_parameters(params=params_conference)
            admin.conference.activate_conference()
            admin.abonent.deactivate_abonent(abonent_number=tester_number)
        with allure.step("Проверка, что абонент в неактивном состоянии"):
            admin.abonent.check_state(abonent_number=tester_number, abonent_state=self.state["inactive"])

        with allure.step("Изменить параметры и перевести вторую конференцию в режим ожидания"):
            params_conference_2 = {
                "signal_protocol": outgoing_call_protocol,
                "pre_activation_duration": "10"
            }
            admin.conference.change_parameters(params=params_conference_2, conference=self.layout_name)
            admin.conference.activate_conference(pre_activate=True, conference=self.layout_name)

        with allure.step("Перенос абонента из активной конференции в предактивную"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            conference2=self.layout_name)
        with allure.step("Проверка, что абонента нет в первой конференции"):
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number)
        with allure.step("Проверка, что абонент есть во второй конференции и что он неактивен"):
            admin.abonent.check_abonent_exist(conference=self.layout_name, abonent_number=tester_number)
            admin.abonent.check_state(abonent_number=tester_number, conference=self.layout_name,
                                      abonent_state=self.state["inactive"])

        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()

    @testit_id(128489)
    @allure.title("Medium: Перенос активного абонента из активной конференции в предактивную")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_active_abonent_transfer_active_to_pre_active(self, admin_create_two_conferences, tester,
                                                          outgoing_call_protocol):

        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]

        with allure.step("Создание конференций и абонента"):
            admin = admin_create_two_conferences
            admin.abonent.create_abonent(abonent_number=tester_number)

        with allure.step("Активировать первую конференцию"):
            params_conference = {
                "signal_protocol": outgoing_call_protocol
            }
            admin.conference.change_parameters(params=params_conference)
            admin.conference.activate_conference()
            tester.call.accept_incoming_call()
        with allure.step("Проверка, что абонент в активном состоянии"):
            admin.abonent.check_state(abonent_number=tester_number, abonent_state=self.state["active"])

        with allure.step("Изменить параметры и перевести вторую конференцию в режим ожидания"):
            params_conference_2 = {
                "signal_protocol": outgoing_call_protocol,
                "pre_activation_duration": "10"
            }
            admin.conference.change_parameters(params=params_conference_2, conference=self.layout_name)
            admin.conference.activate_conference(pre_activate=True, conference=self.layout_name)

        with allure.step("Перенос абонента из активной конференции в предактивную"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            conference2=self.layout_name)
        with allure.step("Проверка, что абонента нет в первой конференции"):
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number)
        with allure.step("Проверка, что абонент есть во второй конференции и что он предактивен"):
            admin.abonent.check_abonent_exist(conference=self.layout_name, abonent_number=tester_number)
            admin.abonent.check_state(abonent_number=tester_number, conference=self.layout_name,
                                      abonent_state=self.state["pre_active"])

        with allure.step("Проверка звука и заставки получаемого ВКСТ в режиме ожидания"):
            check_sound(application=tester, stream_name=tester_sinks["headset"]["name"], np_path=tone["wait_start"])
            CheckVideo.check_video_conference(phone=tester, slots=[red])

        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()

    @testit_id(128490)
    @allure.title("Medium: Перенос предактивного абонента, передающего презентацию")
    @pytest.mark.medium
    @pytest.mark.usefixtures("admin_create_two_conferences")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.usefixtures("tester_2")
    @pytest.mark.parametrize("outgoing_call_protocol", protocol)
    def test_pre_active_abonent_with_presentation_transfer_pre_active_to_pre_active(self, admin_create_two_conferences,
                                                                                    outgoing_call_protocol, tester,
                                                                                    tester_2):
        tester_numbers = {'SIP': self.tester_sip_number, 'H.323': self.tester_h323_number}
        tester_2_numbers = {'SIP': self.tester_2_sip_number, 'H.323': self.tester_2_h323_number}
        tester_number = tester_numbers[outgoing_call_protocol]
        tester_2_number = tester_2_numbers[outgoing_call_protocol]

        send_params = [{"presentation_send_bitrate": 4000, "error": 0.2, "middle_error": 0.2},
                       {"presentation_send_resolution": "FHD"}]
        send_params_2 = [{"presentation_send_bitrate": "-"}, {"presentation_send_resolution": "-"}]
        recv_params = [{"presentation_recv_bitrate": "-"}, {"presentation_recv_resolution": "-"}]

        with allure.step("Создание конференций и абонентов"):
            admin = admin_create_two_conferences
            admin.abonent.create_abonent(abonent_number=tester_number)
            admin.abonent.create_abonent(abonent_number=tester_2_number)

        with allure.step("Изменить параметры и перевести обе конференции в режим ожидания"):
            params_conference = {
                "signal_protocol": outgoing_call_protocol,
                "pre_activation_duration": "10"
            }
            admin.conference.change_parameters(params=params_conference)
            admin.conference.activate_conference(pre_activate=True)
            admin.conference.change_parameters(params=params_conference, conference=self.layout_name)
            admin.conference.activate_conference(pre_activate=True, conference=self.layout_name)
            if outgoing_call_protocol == "H.323":
                tester.settings.set_h239_support_state("true")
                tester_2.settings.set_h239_support_state("true")
            elif outgoing_call_protocol == "SIP":
                tester.settings.set_bfcp_transport("UDP")
                tester_2.settings.set_bfcp_transport("UDP")

        with allure.step("Активировать абонентов"):
            admin.abonent.activate_abonent(abonent_number=tester_number, check_state=False)
            admin.abonent.activate_abonent(abonent_number=tester_2_number, check_state=False)
            tester.call.accept_incoming_call()
            tester_2.call.accept_incoming_call()
        with allure.step("Проверка, что абоненты в предактивном состоянии"):
            admin.abonent.check_state(abonent_number=tester_number, abonent_state=self.state["pre_active"])
            admin.abonent.check_state(abonent_number=tester_2_number, abonent_state=self.state["pre_active"])

        with allure.step("Включить презентацию на тестере"):
            tester.call.change_presentation_state(state=True)

        with allure.step("Проверка отправки битрейта и разрешения тестером"):
            admin.statistic.check_statistic(abonent_number=tester_number, expected_params=send_params)
        with allure.step("Проверка отсутствия получения битрейта и разрешения тестером 2"):
            admin.statistic.check_statistic(abonent_number=tester_2_number, expected_params=recv_params)
        with allure.step("Проверка отсутствия получаемой картинки на тестере 2"):
            CheckVideo.check_recv_presentation(phone=tester_2, abonent=tester, check=False)

        with allure.step("Перенос абонентов из предактивной конференции в предактивную"):
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_number,
                                                            conference2=self.layout_name)
            admin.abonent.drag_n_drop_abonent_to_conference(abonent_number=tester_2_number,
                                                            conference2=self.layout_name)
        with allure.step("Проверка, что абонента нет в первой конференции"):
            admin.abonent.check_abonent_not_exist(abonent_number=tester_number)
        with allure.step("Проверка, что абонент есть во второй конференции и что он предактивен"):
            admin.abonent.check_abonent_exist(conference=self.layout_name, abonent_number=tester_number)
            admin.abonent.check_state(abonent_number=tester_2_number, conference=self.layout_name,
                                      abonent_state=self.state["pre_active"])
        # в админке параметры презентации отсутствуют
        with allure.step("Проверка отсутствия отправки битрейта и разрешения тестером"):
            if outgoing_call_protocol == "SIP":
                admin.statistic.check_statistic(abonent_number=tester_number, conference=self.layout_name,
                                                expected_params=send_params_2)
            elif outgoing_call_protocol == "H.323":
                admin.statistic.check_statistic(abonent_number=tester_number, conference=self.layout_name,
                                                expected_params=send_params)

        with allure.step("Проверка отсутствия получения битрейта и разрешения тестером 2"):
            admin.statistic.check_statistic(abonent_number=tester_2_number, conference=self.layout_name,
                                            expected_params=recv_params)
        with allure.step("Проверка отсутствия получаемой картинки на тестере 2"):
            CheckVideo.check_recv_presentation(phone=tester_2, abonent=tester, check=False)

        with allure.step("Завершение конференции и удаление конференции"):
            admin.conference.deactivate_conference(conference=self.layout_name)
            admin.conference.deactivate_conference()         
                    
