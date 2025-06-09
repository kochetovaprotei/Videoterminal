import allure
import pytest
import logging
from time import sleep
import datetime
from common.keywords.CheckStatistics import CheckStatistic
from common.keywords.Image_keywords import ImageChecker
from library.consts import Consts
from library.vcst_interface.keywords.Camera_keywords import CameraObj
from library.vcst_interface.configuration import (video_15_fps_mkv, video_30_fps_mkv,
                                                  video_5_15_60_30_fps_mkv)

orange = (237, 118, 14)
green = (11, 148, 2)
red = (115, 0, 0)
blue = (0, 0, 121)

VIDEO_PARAMS_LOW_FPS = {
    "fps": {"set": 30, "expected": 15, "error": 0.1, "middle_error": 0.1},
    "bitrate": {"set": 5000, "expected": 5000, "error": 0.25, "middle_error": 0.2},
    "resolution": {"set": "1920x1080", "expected": "1920x1080"},
    "aspect_ratio": "16:9"
}
VIDEO_PARAMS_HIGH_FPS = {
    "fps": {"set": 30, "expected": 30, "error": 0.1, "middle_error": 0.1},
    "bitrate": {"set": 5000, "expected": 5000, "error": 0.25, "middle_error": 0.2},
    "resolution": {"set": "1920x1080", "expected": "1920x1080"},
    "aspect_ratio": "16:9"
}
VIDEO_PARAMS_LOW_FPS_SLIDES = {
    "fps": {"set": 30, "expected": 3, "error": 0.1, "middle_error": 0.1},
    "bitrate": {"set": 5000, "expected": 5000, "error": 0.25, "middle_error": 0.2},
    "resolution": {"set": "1920x1080", "expected": "1920x1080"},
    "aspect_ratio": "16:9"
}
VIDEO_PARAMS_LOW_FPS_VCST = {
    "fps": {"set": 10, "expected": 10, "error": 0.1, "middle_error": 0.1},
    "bitrate": {"set": 1000, "expected": 1000, "error": 0.3, "middle_error": 0.25},
    "resolution": {"set": "1920x1080", "expected": "1920x1080"},
    "aspect_ratio": "16:9"
}
VIDEO_PARAMS_LOW_FPS_VCST_SLIDES = {
    "fps": {"set": 10, "expected": 3, "error": 0.1, "middle_error": 0.1},
    "bitrate": {"set": 1000, "expected": 1000, "error": 0.3, "middle_error": 0.25},
    "resolution": {"set": "1920x1080", "expected": "1920x1080"},
    "aspect_ratio": "16:9"
}


def wait_assert_statistic(assert_func, timeout):
    """
    Ждём пока появится нужный параметр для ассерта в статистике.
        :param assert_func: Функция ассерта.
        :param timeout: Время ожидания появления аттрибута в статистике.
    """
    start = datetime.datetime.today()
    stop = start + datetime.timedelta(seconds=timeout)
    while datetime.datetime.today() < stop:
        try:
            assert assert_func()
            break
        except AssertionError as exc:
            logging.debug(f"AssertionError - {exc}")
            sleep(0.5)
    else:
        raise AssertionError(f"TimeoutError in wait_assert_statistic")


@allure.feature("11-Параметры медиапотока (MediaStreamParam)")
@allure.story("Подстройка битрейта под fps")
@allure.description("Подстройка битрейта под fps")
@pytest.mark.neva
@pytest.mark.api
class TestBitrateResolvedByFps:

    @allure.severity("medium")
    @allure.title("Medium: Видеовызов. Высокий fps в настройках ВКСТ, низкий - у источника")
    @pytest.mark.medium
    @pytest.mark.usefixtures("vcst")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("codecs", ["h264", "h265"])
    def test_call_high_vcst_fps_low_source_fps(self, vcst, tester, codecs):
        with allure.step("Установка видеокодеков"):
            vcst.settings.set_video_codecs(codecs)
            tester.settings.set_video_codecs(codecs)
        with allure.step("Установка параметров медиа"):
            vcst.settings.set_media_params(VIDEO_PARAMS_LOW_FPS)
            tester.settings.set_media_params(VIDEO_PARAMS_LOW_FPS)
        with allure.step("Установка видеофайла с низким фпс в качестве источника основной камеры"):
            vcst.settings.set_main_camera_source_file(video_15_fps_mkv["path"])
        with allure.step("Добавление второй камеры: видеофайл с высоким фпс"):
            camera_high_fps = CameraObj.create_cam(vcst, source=video_30_fps_mkv["path"], name="camera_high_fps")

        with allure.step("Вызов ВКСТ -> Тестер"):
            vcst.call.call_by_number(number=Consts.tester_sip_number)
            tester.call.accept_incoming_call()
            vcst.call.is_call_active()

        with allure.step("Проверка битрейта и фпс отправки"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS, "send", "Video"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS, "recv", "Video"]])

        with allure.step("Выключить передачу видео на ВКСТ"):
            vcst.call.change_camera_state(state=False)
        with allure.step("Проверка битрейта и фпс после отключения камеры"):
            assert tester.statistic.recv_bitrate(zero=True) == 0, "Bitrate не равен нулю!"
            assert tester.statistic.recv_fps(zero=True) == 0, "fps не равен нулю!"

        with allure.step("Включить передачу видео на ВКСТ"):
            vcst.call.change_camera_state(state=True)
        with allure.step("Проверка битрейта и фпс отправки после включения камеры"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS, "send", "Video"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS, "recv", "Video"]])

        with allure.step("Изменить источник для основной камеры на источник с высоким фпс "):
            vcst.settings.set_main_camera(camera_high_fps)
        with allure.step("Проверка битрейта и фпс отправки после изменения камеры"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_HIGH_FPS, "send", "Video"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_HIGH_FPS, "recv", "Video"]])

        with allure.step("Завершение вызова"):
            vcst.call.release_call()
            tester.call.is_not_call_active()

    @allure.severity("medium")
    @allure.title("Medium: Вызов с презентацией. Высокий fps в настройках ВКСТ, низкий - у источника")
    @pytest.mark.medium
    @pytest.mark.usefixtures("vcst")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("codecs", ["h264", "h265"])
    def test_call_presentation_high_vcst_fps_low_source_fps(self, vcst, tester, codecs):
        with allure.step("Установка видеокодеков"):
            vcst.settings.set_video_codecs(codecs)
            tester.settings.set_video_codecs(codecs)
        with allure.step("Установка параметров медиа презентации"):
            vcst.settings.set_media_params_presentation(VIDEO_PARAMS_LOW_FPS)
            tester.settings.set_media_params_presentation(VIDEO_PARAMS_LOW_FPS)
        with allure.step("Установка видеофайла с низким фпс в качестве источника камеры презентации"):
            vcst.settings.set_presentation_camera_source_file(video_15_fps_mkv["path"])

        with allure.step("Вызов ВКСТ -> Тестер"):
            vcst.call.call_by_number(number=Consts.tester_sip_number)
            tester.call.accept_incoming_call()
            vcst.call.is_call_active()

        with allure.step("Включить передачу презентации на ВКСТ: Слайды"):
            vcst.call.change_presentation_state(state=True, action="Слайды", second_channel=True)
        with allure.step("Проверка битрейта и фпс отправки презентации"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_SLIDES, "send", "Presentation"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_SLIDES, "recv", "Presentation"]])

        with allure.step("Выключить передачу презентации на ВКСТ"):
            vcst.call.change_presentation_state(state=False)
        with allure.step("Проверка отсутствия битрейта и фпс после отключения презентации"):
            vcst.statistic.check_no_value(func=vcst.statistic.send_presentation_bitrate, reason="source_off")
            vcst.statistic.check_no_value(func=vcst.statistic.send_presentation_fps, reason="source_off")
            tester.statistic.check_no_value(func=tester.statistic.recv_presentation_bitrate, reason="source_off")
            tester.statistic.check_no_value(func=tester.statistic.recv_presentation_fps, reason="source_off")

        with allure.step("Включить передачу презентации на ВКСТ: Слайды"):
            vcst.call.change_presentation_state(state=True, action="Слайды", second_channel=True)
        with allure.step("Проверка битрейта и фпс отправки после включения презентации"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_SLIDES, "send", "Presentation"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_SLIDES, "recv", "Presentation"]])

        with allure.step("Выключить передачу презентации на ВКСТ"):
            vcst.call.change_presentation_state(state=False)
        with allure.step("Включить передачу презентации на ВКСТ: Видео"):
            vcst.call.change_presentation_state(state=True, action="Видео", second_channel=True)
        with allure.step("Проверка битрейта и фпс отправки после включения презентации: режим Видео"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS, "send", "Presentation"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS, "recv", "Presentation"]])

        with allure.step("Завершение вызова"):
            vcst.call.release_call()
            tester.call.is_not_call_active()

    @allure.severity("medium")
    @allure.title("Medium: Видеовызов. Низкий fps в настройках ВКСТ, высокий - у источника")
    @pytest.mark.medium
    @pytest.mark.usefixtures("vcst")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("codecs", ["h264", "h265"])
    def test_call_low_vcst_fps_high_source_fps(self, vcst, tester, codecs):
        with allure.step("Установка видеокодеков"):
            vcst.settings.set_video_codecs(codecs)
            tester.settings.set_video_codecs(codecs)
        with allure.step("Установка параметров медиа"):
            vcst.settings.set_media_params(VIDEO_PARAMS_LOW_FPS_VCST)
            tester.settings.set_media_params(VIDEO_PARAMS_HIGH_FPS)
        with allure.step("Установка видеофайла с высоким фпс в качестве источника основной камеры"):
            vcst.settings.set_main_camera_source_file(video_30_fps_mkv["path"])
        with allure.step("Добавление второй камеры: видеофайл с низким фпс"):
            camera_low_fps = CameraObj.create_cam(vcst, source=video_15_fps_mkv["path"], name="camera_low_fps")

        with allure.step("Вызов ВКСТ -> Тестер"):
            vcst.call.call_by_number(number=Consts.tester_sip_number)
            tester.call.accept_incoming_call()
            vcst.call.is_call_active()

        with allure.step("Проверка битрейта и фпс отправки"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "send", "Video"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "recv", "Video"]])

        with allure.step("Выключить передачу видео на ВКСТ"):
            vcst.call.change_camera_state(state=False)
        with allure.step("Проверка битрейта и фпс после отключения камеры"):
            assert tester.statistic.recv_bitrate(zero=True) == 0, "Bitrate не равен нулю!"
            assert tester.statistic.recv_fps(zero=True) == 0, "fps не равен нулю!"

        with allure.step("Включить передачу видео на ВКСТ"):
            vcst.call.change_camera_state(state=True)
        with allure.step("Проверка битрейта и фпс отправки после включения камеры"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "send", "Video"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "recv", "Video"]])

        with allure.step("Изменить источник для основной камеры на источник с низким фпс "):
            vcst.settings.set_main_camera(camera_low_fps)
        with allure.step("Проверка битрейта и фпс отправки после изменения камеры"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "send", "Video"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "recv", "Video"]])

        with allure.step("Завершение вызова"):
            vcst.call.release_call()
            tester.call.is_not_call_active()

    @allure.severity("medium")
    @allure.title("Medium: Вызов с презентацией. Низкий fps в настройках ВКСТ, высокий - у источника")
    @pytest.mark.medium
    @pytest.mark.usefixtures("vcst")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("codecs", ["h264", "h265"])
    def test_call_presentation_low_vcst_fps_high_source_fps(self, vcst, tester, codecs):
        with allure.step("Установка видеокодеков"):
            vcst.settings.set_video_codecs(codecs)
            tester.settings.set_video_codecs(codecs)
        with allure.step("Установка параметров медиа презентации"):
            vcst.settings.set_media_params_presentation(VIDEO_PARAMS_LOW_FPS_VCST)
            tester.settings.set_media_params_presentation(VIDEO_PARAMS_LOW_FPS)
        with allure.step("Установка видеофайла с высоким фпс в качестве источника камеры презентации"):
            vcst.settings.set_presentation_camera_source_file(video_30_fps_mkv["path"])

        with allure.step("Вызов ВКСТ -> Тестер"):
            vcst.call.call_by_number(number=Consts.tester_sip_number)
            tester.call.accept_incoming_call()
            vcst.call.is_call_active()

        with allure.step("Включить передачу презентации на ВКСТ: Видео"):
            vcst.call.change_presentation_state(state=True, action="Видео", second_channel=True)
        with allure.step("Проверка битрейта и фпс отправки презентации"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "send", "Presentation"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "recv", "Presentation"]])

        with allure.step("Выключить передачу презентации на ВКСТ"):
            vcst.call.change_presentation_state(state=False)
        with allure.step("Проверка отсутствия битрейта и фпс после отключения презентации"):
            vcst.statistic.check_no_value(func=vcst.statistic.send_presentation_bitrate, reason="source_off")
            vcst.statistic.check_no_value(func=vcst.statistic.send_presentation_fps, reason="source_off")
            tester.statistic.check_no_value(func=tester.statistic.recv_presentation_bitrate, reason="source_off")
            tester.statistic.check_no_value(func=tester.statistic.recv_presentation_fps, reason="source_off")

        with allure.step("Включить передачу презентации на ВКСТ: Видео"):
            vcst.call.change_presentation_state(state=True, action="Видео", second_channel=True)
        with allure.step("Проверка битрейта и фпс отправки после включения презентации"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "send", "Presentation"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST, "recv", "Presentation"]])

        with allure.step("Выключить передачу презентации на ВКСТ"):
            vcst.call.change_presentation_state(state=False)
        with allure.step("Включить передачу презентации на ВКСТ: Слайды"):
            vcst.call.change_presentation_state(state=True, action="Слайды", second_channel=True)
        with allure.step("Проверка битрейта и фпс отправки после включения презентации: режим Слайды"):
            CheckStatistic().check_statistic(checklist=[
                [vcst.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST_SLIDES, "send", "Presentation"],
                [tester.statistic.get_all_statistic, VIDEO_PARAMS_LOW_FPS_VCST_SLIDES, "recv", "Presentation"]])

        with allure.step("Завершение вызова"):
            vcst.call.release_call()
            tester.call.is_not_call_active()

    @allure.severity("medium")
    @allure.title("Medium: Видеовызов. Плавающий fps")
    @pytest.mark.medium
    @pytest.mark.usefixtures("vcst")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("codecs", ["h264", "h265"])
    def test_call_wave_source_fps(self, vcst, tester, codecs):
        with allure.step("Установка видеокодеков"):
            vcst.settings.set_video_codecs(codecs)
            tester.settings.set_video_codecs(codecs)
        with allure.step("Установка параметров медиа"):
            vcst.settings.set_media_params(VIDEO_PARAMS_HIGH_FPS)
            tester.settings.set_media_params(VIDEO_PARAMS_HIGH_FPS)
        with allure.step("Установка видеофайла с плавающим фпс в качестве источника основной камеры"):
            vcst.settings.set_main_camera_source_file(video_5_15_60_30_fps_mkv["path"])

        with allure.step("Вызов ВКСТ -> Тестер"):
            vcst.call.call_by_number(number=Consts.tester_sip_number)
            tester.call.accept_incoming_call()
            vcst.call.is_call_active()

        with allure.step("Проверка битрейта 5000 и фпс отправки 5 фпс"):
            wait_assert_statistic(lambda: 3 <= int(vcst.statistic.send_fps()) <= 6, timeout=1)
            wait_assert_statistic(lambda: 3600 < int(vcst.statistic.send_bitrate()) < 6250, timeout=7)
        with allure.step('Проверка картинки VCST с основной камеры - оранжевый квадрат'):
            snapshot = tester.statistic.get_gui_snapshot_in_call_old
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[orange, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 15 фпс"):
            wait_assert_statistic(lambda: 10 <= int(vcst.statistic.send_fps()) <= 16, timeout=13)
            wait_assert_statistic(lambda: 3600 < int(vcst.statistic.send_bitrate()) < 6250, timeout=6)
        with allure.step('Проверка картинки VCST с основной камеры - зеленый квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[green, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 30 фпс (источник 60 фпс)"):
            wait_assert_statistic(lambda: 25 <= int(vcst.statistic.send_fps()) <= 33, timeout=25)
            wait_assert_statistic(lambda: 3600 < int(vcst.statistic.send_bitrate()) < 6250, timeout=6)
        with allure.step('Проверка картинки VCST с основной камеры - красный квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[red, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 30 фпс"):
            wait_assert_statistic(lambda: 25 <= int(vcst.statistic.send_fps()) <= 33, timeout=16)
            wait_assert_statistic(lambda: 3600 < int(vcst.statistic.send_bitrate()) < 6250, timeout=1)
        with allure.step('Проверка картинки VCST с основной камеры - синий квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[blue, [960, 540]]], api=True)

        with allure.step("Завершение вызова"):
            vcst.call.release_call()
            tester.call.is_not_call_active()

    @allure.severity("medium")
    @allure.title("Medium: Вызов с презентацией. Плавающий fps")
    @pytest.mark.medium
    @pytest.mark.usefixtures("vcst")
    @pytest.mark.usefixtures("tester")
    @pytest.mark.parametrize("codecs", ["h264", "h265"])
    def test_call_presentation_wave_source_fps(self, vcst, tester, codecs):
        with allure.step("Установка видеокодеков"):
            vcst.settings.set_video_codecs(codecs)
            tester.settings.set_video_codecs(codecs)
        with allure.step("Установка параметров медиа презентации"):
            vcst.settings.set_media_params_presentation(VIDEO_PARAMS_HIGH_FPS)
            tester.settings.set_media_params_presentation(VIDEO_PARAMS_HIGH_FPS)
        with allure.step("Установка видеофайла с плавающим фпс в качестве источника камеры презентации"):
            vcst.settings.set_presentation_camera_source_file(video_5_15_60_30_fps_mkv["path"])

        with allure.step("Вызов ВКСТ -> Тестер"):
            vcst.call.call_by_number(number=Consts.tester_sip_number)
            tester.call.accept_incoming_call()
            vcst.call.is_call_active()
        with allure.step("Включить передачу презентации на ВКСТ: Видео"):
            vcst.call.change_presentation_state(state=True, action="Видео", second_channel=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 5 фпс"):
            wait_assert_statistic(lambda: 3 <= int(vcst.statistic.send_presentation_fps()) <= 6, timeout=1)
            wait_assert_statistic(lambda: 3750 < int(vcst.statistic.send_presentation_bitrate()) < 6250, timeout=6)
        with allure.step('Проверка картинки VCST с камеры презентации - оранжевый квадрат'):
            snapshot = tester.statistic.get_gui_snapshot_in_call_old
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[orange, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 15 фпс"):
            wait_assert_statistic(lambda: 8 <= int(vcst.statistic.send_presentation_fps()) <= 16, timeout=14)
            wait_assert_statistic(lambda: 3750 < int(vcst.statistic.send_presentation_bitrate()) < 6250, timeout=6)
        with allure.step('Проверка картинки VCST с камеры презентации - зеленый квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[green, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 30 фпс (источник 60 фпс)"):
            wait_assert_statistic(lambda: 20 <= int(vcst.statistic.send_presentation_fps()) <= 40, timeout=20)
            wait_assert_statistic(lambda: 3750 < int(vcst.statistic.send_presentation_bitrate()) < 6250, timeout=15)
        with allure.step('Проверка картинки VCST с камеры презентации - красный квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[red, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 30 фпс"):
            wait_assert_statistic(lambda: 20 <= int(vcst.statistic.send_presentation_fps()) <= 33, timeout=13)
            wait_assert_statistic(lambda: 3750 < int(vcst.statistic.send_presentation_bitrate()) < 6250, timeout=3)
        with allure.step('Проверка картинки VCST с камеры презентации - синий квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[blue, [960, 540]]], api=True)

        with allure.step("Выключить передачу презентации на ВКСТ"):
            vcst.call.change_presentation_state(state=False)
            sleep(4)
        with allure.step("Включить передачу презентации на ВКСТ: Слайды"):
            vcst.call.change_presentation_state(state=True, action="Слайды", second_channel=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 3 фпс (источник 5 фпс)"):
            wait_assert_statistic(lambda: int(vcst.statistic.send_presentation_fps()) == 3, timeout=11)
            wait_assert_statistic(lambda: 3750 < int(vcst.statistic.send_presentation_bitrate()) < 6250, timeout=7)
        with allure.step('Проверка картинки VCST с камеры презентации - оранжевый квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[orange, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 3 фпс (источник 15 фпс)"):
            wait_assert_statistic(lambda: 3 <= int(vcst.statistic.send_presentation_fps()) <= 4, timeout=11)
            wait_assert_statistic(lambda: 3750 < int(vcst.statistic.send_presentation_bitrate()) < 6250, timeout=8)
        with allure.step('Проверка картинки VCST с камеры презентации - зеленый квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[green, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 3 фпс (источник 60 фпс)"):
            wait_assert_statistic(lambda: 3 <= int(vcst.statistic.send_presentation_fps()) <= 4, timeout=13)
            wait_assert_statistic(lambda: 3750 < int(vcst.statistic.send_presentation_bitrate()) < 7000, timeout=8)
        with allure.step('Проверка картинки VCST с камеры презентации - красный квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[red, [960, 540]]], api=True)

        with allure.step("Проверка битрейта 5000 и фпс отправки 3 фпс (источник 30 фпс)"):
            wait_assert_statistic(lambda: 3 <= int(vcst.statistic.send_presentation_fps()) <= 4, timeout=8)
            wait_assert_statistic(lambda: 3750 < int(vcst.statistic.send_presentation_bitrate()) < 6250, timeout=15)
        with allure.step('Проверка картинки VCST с камеры презентации - синий квадрат'):
            ImageChecker.is_target_image(get_img_func=snapshot, target_info=[[blue, [960, 540]]], api=True)

        with allure.step("Завершение вызова"):
            vcst.call.release_call()
            tester.call.is_not_call_active()
