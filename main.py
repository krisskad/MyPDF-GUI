from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.config import Config
from plyer import filechooser
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.button import MDFlatButton
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivy.clock import mainthread
from kivy.clock import Clock
from kivy.uix.popup import Popup
import os

############################## Default Window ###############################
Config.set('graphics', 'resizable', 0)
Config.set('kivy', 'window_icon', os.path.join(os.getcwd(),"logo", "window-icon.png"))
Config.write()
#############################################################################

import glob
import cv2
import numpy as np
# import tesserocr
import re
import pytesseract
from pytesseract import Output
# import img2pdf
from PIL import Image
# from threading import Thread
from pdf2image import convert_from_path
import shutil
# from io import BytesIO
import threading
import time
from functools import partial


############################################# Config ##############################################

poppler_dir = os.path.join(os.getcwd(), 'src', 'plugins', 'poppler-0.68.0', 'bin')
pytesseract.pytesseract.tesseract_cmd = os.path.join(os.getcwd(), 'src', "plugins", "Tesseract-OCR", "tesseract.exe")

###################################################################################################

# Kivy String
kv = '''
ScreenManager:
    StarterScreen:
    MenuScreen:

<StarterScreen>:
    name: 'starter'
    id: first
    Image:
        source: 'logo/opening.gif'
        size: self.texture_size
        anim_delay: 0.1
        mipmap: True
        allow_stretch: True
    MDRectangleFlatButton:
        text: 'Start'
        pos_hint: {"center_x":0.5, "center_y":0.2}     
        on_release: root.manager.current = 'menu'

<MenuScreen>:
    name: 'menu'
    id: second
    MDToolbar:
        id: header
        title: "Dashboard"
        pos_hint: {'top':1.0}
        elevation: 10

    MDBottomAppBar:

        MDToolbar:
            id: footer
            title: "Choose Folder"
            font_size: '50sp'
            icon: "folder-plus"
            type: "bottom"
            left_action_items: [["folder", lambda x: app.file_manager_open()]]
            elevation: 10
            mode: "center"
            on_action_button: app.file_manager_open()


    MDRoundFlatButton:
        text: 'Run'
        md_bg_color: 1,0,1,1
        pos_hint: {"center_x":0.5, "center_y":0.5}
        on_release: app.run_main()
        
'''


class StarterScreen(Screen):
    pass


class MenuScreen(Screen):
    def show_popup(self, req):
        self.req_data = req
        self.progress_bar = MDProgressBar()
        self.popup = Popup(
            title='Progress',
            content=self.progress_bar,
            auto_dismiss=False,  # dialog does NOT close if click outside it
            size_hint=(None, None),
            pos_hint = {'center_y':0.3},
            size=(400, 200)
        )
        self.popup.bind(on_open=lambda x: self.run_thread())
        self.progress_bar.max = 100
        self.progress_bar.value = 10

        self.popup.open()
        # print(self.progress_bar.value)

    @mainthread
    def update_progress_bar(self, val, _):
        self.progress_bar.value = val
        # print(self.progress_bar.value)

        if val >= 100:
            self.popup.dismiss()
            self.dialog = MDDialog(
                title="Status",
                text="Process Successfully Complete, Check OUTPUT folder",
                buttons=[
                    MDFlatButton(
                        text='OK',
                        on_release=lambda _: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text='Cancel',
                        on_release=lambda _: self.dialog.dismiss()
                    )
                ],
            )
            self.dialog.open()
            toast("Process Successfully Completed", duration=2.5)

    def run_thread(self):
        t1 = threading.Thread(target=self.process_some_data)
        t1.start()
        # t1.join()

    def process_some_data(self):
        ########################## PDF to Image ###############################

        # output_dir = os.path.join(os.getcwd(), 'src', 'temp_images')

        if self.req_data.get("status"):
            pdf_list = self.req_data.get("pdf_file_list")
            count = 0
            for pdf_file in pdf_list:
                count = count + 1
                time.sleep(0)  # simulate program is running something
                Clock.schedule_once(partial(self.update_progress_bar, count), 0)

                if os.path.isfile(pdf_file):
                    # print(pdf_file, count)
                    images = convert_from_path(pdf_file, 400, size=2000, poppler_path=poppler_dir)
                    for image in images:
                        # fname = os.path.join(output_dir, str(count) + ".png")
                        # image.save(fname, "PNG")

        ##############################################################################
                        next_counter = count

                        original = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                        if original.shape[1] > original.shape[0]:
                            end_point = (original.shape[1], original.shape[0])  # 2000, 1422
                            start_point = (original.shape[1] - 300, original.shape[0] - 170)  # 1700, 1222

                            x = start_point[0]
                            y = start_point[1]
                            w = end_point[0] - start_point[0]
                            h = end_point[1] - start_point[1]
                        else:
                            hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)

                            lower_range = np.array([110, 50, 50])
                            upper_range = np.array([130, 255, 255])

                            mask = cv2.inRange(hsv, lower_range, upper_range)
                            points = cv2.findNonZero(mask)
                            avg = np.mean(points, axis=0)
                            x, y = int(avg[0, 0]) - 50, int(avg[0, 1]) - 400

                            start_point = (x, y)
                            end_point = (original.shape[1] - 200, original.shape[0] - 50)

                            w = end_point[0] - x
                            h = end_point[1] - y

                        ROI = original[y:y + h, x:x + w]
                        rgb = cv2.cvtColor(ROI, cv2.COLOR_BGR2RGB)
                        results = pytesseract.image_to_data(rgb, output_type=Output.DICT)

                        final_text = set()
                        for i in range(0, len(results["text"])):
                            # extract the bounding box coordinates of the text region from
                            # the current result
                            x = results["left"][i]
                            y = results["top"][i]
                            w = results["width"][i]
                            h = results["height"][i]
                            # extract the OCR text itself along with the confidence of the
                            # text localization
                            text = results["text"][i]
                            conf = int(results["conf"][i])

                            # filter out weak confidence text localizations
                            if conf > 50 and w > 100 and h > 10:
                                final_text.add(text)

                                pattern = r'[A-Z0-9\.\-+_,]+(?:\.[A-Z0-9\.\-+_,]+){1,6}'
                                gotit = []
                                if len(text)>0:
                                    number = re.findall(pattern, text)
                                    # gotit.append("".join(number))
                                    if len(number)>0:
                                        # print(number, original_image)

                                        file_name = number[0].replace(".", "_")
                                        final_output_file = os.path.join(os.getcwd(), "OUTPUT", file_name + ".pdf")
                                        # cv2.imwrite(final_output_file, original)
                                        # shutil.move(pdf_file, final_output_file)
                                        shutil.copy2(pdf_file, final_output_file)

                                        next_counter+=1
                                        time.sleep(0)  # simulate program is running something
                                        Clock.schedule_once(partial(self.update_progress_bar, next_counter), 0)

            time.sleep(1)  # simulate program is running something
            Clock.schedule_once(partial(self.update_progress_bar, 100), 0)



sm = ScreenManager()
sm.add_widget(StarterScreen(name='starter'))
sm.add_widget(MenuScreen(name='menu'))


class MyPDFApp(MDApp):
    def build(self):
        self.builder = Builder.load_string(kv)
        self.req_data = {"raw_path": 0, "pdf_file_list": 0, "pdf_file_count": 0, "status": False}
        return self.builder

    def file_manager_open(self):
        raw_path = filechooser.choose_dir()
        # print(raw_path)
        if len(raw_path) > 0:
            file_list = glob.glob(os.path.join(raw_path[0], "*.pdf"))

            if len(file_list) > 0:
                file_count = len(file_list)
                hint_text = "TOTAL PDF FILES FOUND"
                path_label = raw_path[0]
            else:
                file_count = len(file_list)
                hint_text = "FOLDER DOES NOT CONTAIN ANY PDF FILE"
                path_label = raw_path[0]
                toast('Please Select Folder Which contain your PDF Files')

            self.req_data = {"raw_path": path_label, "pdf_file_list": file_list, "pdf_file_count": file_count,
                             "status": True}

            file_cnt_label = MDLabel(text=str(file_count), halign="center",
                                     pos_hint={'center_x': 0.5, 'center_y': 0.7},
                                     theme_text_color='Custom',
                                     text_color=(153 / 255.0, 214 / 255.0, 1, 1),
                                     font_style='H1')

            hint_label = MDLabel(text=str(hint_text), halign="center",
                                 pos_hint={'center_x': 0.5, 'center_y': 0.6},
                                 font_size=10,
                                 theme_text_color='Hint')

            self.builder.get_screen('menu').add_widget(file_cnt_label)
            self.builder.get_screen('menu').add_widget(hint_label)
            self.builder.get_screen('menu').ids.footer.title = str(path_label)

        else:
            self.req_data = {"raw_path": 0, "pdf_file_list": 0, "pdf_file_count": 0, "status": False}


    def run_main(self):
        if self.req_data.get("status"):
            MenuScreen().show_popup(self.req_data)
        else:
            toast('Please Select PDF Folder to proceed')


def reset():
    import kivy.core.window as window
    from kivy.base import EventLoop
    if not EventLoop.event_listeners:
        from kivy.cache import Cache
        window.Window = window.core_select_lib('window', window.window_impl, True)
        Cache.print_usage()
        for cat in Cache._categories:
            Cache._objects[cat] = {}


if __name__ == '__main__':
    reset()
    app = MyPDFApp()
    app.run()
