import music
import customtkinter as ctk
import numpy as np
from soundfile import read as sfRead
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinterdnd2 import TkinterDnD, DND_FILES
from sys import exit as sysExit, argv
from os import getcwd, remove
from os.path import exists, split, splitext
from threading import Thread
from time import perf_counter
from pydub.audio_segment import AudioSegment
from pydub.playback import play as dubplay
from icon import daIconFile
from tempfile import mkstemp


class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class App:
    def __init__(self) -> None:
        _, self.ICON_PATH = mkstemp()
        with open(self.ICON_PATH, "wb") as self.iconFile:
            self.iconFile.write(daIconFile)
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("green")
        
        if ctk.get_appearance_mode() == "Dark":
            self.COLOR1 = "#101010"
            self.BG_COLOR = "#303030"
            self.FG_GREEN = "#3fb582"
            self.GREY = "#808080"
            # self.APP_BG = "#242424"
        else:
            self.COLOR1 = "#c0c0c0"
            self.BG_COLOR = "#303030"
            self.FG_GREEN = "#3fb582"
            self.GREY = "#505050"
            # self.APP_BG = "#ebebeb"
        
        self.window = Tk()
        self.window.title("Music Player by erfan :D")
        self.window.resizable(False, False)
        self.window.geometry("320x240")
        self.window.iconbitmap(default=self.ICON_PATH)
        
        self.m = music.Music()
        self.m.init()
        self.window.protocol("WM_DELETE_WINDOW", self.on_quit)
        
        self.timer_text: float = 0.0
        self.timer_step_ms: int = 10
        
        self.start = perf_counter()
        
        self.timer = ctk.CTkLabel(self.window,
                                  text=self.timer_text)
        self.timer.grid(row=0, column=0)
        
        self.loaded_file: str = ""
        
        self.progress_bar = ctk.CTkProgressBar(self.window,
                                               width=300)
        self.progress_bar.place(x=10, y=210)
        self.progress_bar.set(0)
        
        self.bcr = 8 # button_corner_radius
        self.export_buttons_pady = 2
        self.temp_wav_file = ""
        
        self.label_at_02 = ctk.CTkLabel(self.window, text="")
        self.label_at_02.grid(row=0, column=2, columnspan=20)
        
        self.direc = getcwd()
        
        if len(argv) > 1 and exists(argv[1]):
            self.song_duration = 0
            x = Thread(target=self.play_and_close, args=(argv[1],))
            x.start()
            self.window.after(self.timer_step_ms, self.update_time, self.timer)
        
        self.main()
        self.iconFile.close()
        self.window.mainloop()
    
    
    def config_stream(self, samp_width: int, channels: int, sample_rate: int):
        if type(samp_width) == str:
            samp_width = self.get_sampwidth_from_str(samp_width)
        
        return self.m.AUDIO_OBJECT.open(format=samp_width,
                                        channels=channels,
                                        rate=sample_rate,
                                        output=True)
    
    
    def play_loaded(self):
        if self.loaded_file:
            y = Thread(target=self.play, args=(self.loaded_file,))
            y.start()
        
        else:
            self.play_file()
    
    
    def play(self, file_path: str):
        self.timer_text = 0
        
        self.progress_bar.destroy()
        self.progress_bar = ctk.CTkProgressBar(self.window,
                                               width=300)
        self.progress_bar.place(x=10, y=210)
        
        fformat = splitext(file_path)[1]
        fformat = fformat.removeprefix(".")
        
        print(f"now playing {file_path}")
        
        #-- for ".erfan" files --#
        if fformat == "erfan":
            with open(file_path, "rb") as f:
                data = f.read()
                sample_rate = int.from_bytes(data[0:4], "little")
                dtype = int.from_bytes(data[4:6], "little")
                dtype = self.get_sampwidth_from_number(dtype)
                data = np.frombuffer(data[8:], dtype=dtype)
                self.song_duration = len(data)/sample_rate
                
                duration = ctk.CTkLabel(self.window,
                                        text=round(self.song_duration, 2))
                duration.grid(row=0, column=1)
                
                self.window.after(self.timer_step_ms, self.update_time, self.timer)
                self.start = perf_counter()
                
                self.m.play_erfan(file_path)
        
        #-- for adts files --#
        elif fformat in ["aac", "wma", "m4a"]:
            sound = AudioSegment.from_file(file_path, fformat)
            
            self.song_duration = sound.duration_seconds
            duration = ctk.CTkLabel(self.window,
                                    text=round(self.song_duration, 2))
            duration.grid(row=0, column=1)
            
            self.window.after(self.timer_step_ms, self.update_time, self.timer)
            self.start = perf_counter()
            
            dubplay(sound)
        
        #-- other files such as mp3, ogg, wav, aiff, flac --#
        else:
            data, sample_rate = sfRead(file_path)
            self.song_duration = len(data)/sample_rate
            
            duration = ctk.CTkLabel(self.window,
                                    text=round(self.song_duration, 2))
            duration.grid(row=0, column=1)
            
            self.window.after(self.timer_step_ms, self.update_time, self.timer)
            self.start = perf_counter()
            
            if data.dtype == "float64":
                data = data.astype(np.float32)
            
            dtype = self.get_sampwidth_from_str(data.dtype)
            
            self.m.stream.stop_stream()
            self.m.stream.close()
            self.m.stream.stop_stream()
            self.m.stream = self.config_stream(samp_width=self.m.AUDIO_OBJECT.get_format_from_width(dtype),
                                               channels=data.ndim,
                                               sample_rate=sample_rate)
            
            self.m.play_buffer(data)
            
    
    def play_and_close(self, file_name: str):
        self.play(file_name)
        self.on_quit()
    
    
    def play_file(self):
        self.load_file()
       
        if self.loaded_file:
            y = Thread(target=self.play, args=(self.loaded_file,))
            y.start()
    
    
    def on_quit(self):
        self.m.done()
        self.window.quit()
        sysExit()
    
    
    def load_file(self):
        file = askopenfilename(title="select a sound file",
                               defaultextension=("sound files", ".wav .erfan"),
                               filetypes=[("sound files", ".erfan"),
                                          ("sound files", ".wav"),
                                          ("sound files", ".mp3"),
                                          ("sound files", ".aiff"),
                                          ("sound files", ".aifc"),
                                          ("sound files", ".aif"),
                                          ("sound files", ".flac"),
                                          ("sound files", ".ogg"),
                                          ("sound files", ".m4a"),
                                          ("sound files", ".acc"),
                                          ("sound files", ".wma"),
                                          ("erfan", ".erfan"),
                                          ("wav", ".wav"),
                                          ("mp3", ".mp3"),
                                          ("aiff", ".aiff"),
                                          ("aifc", ".aifc"),
                                          ("aif", ".aif"),
                                          ("flac", ".flac"),
                                          ("ogg", ".ogg"),
                                          ("m4a", ".m4a"),
                                          ("acc", ".acc"),
                                          ("wma", ".wma"),
                                          ("any", ".*")])
        
        if file:
            self.loaded_file = file
            self.label_at_02.destroy()
            self.label_at_02 = ctk.CTkLabel(self.window,
                         text="file has been loaded",
                         text_color=self.FG_GREEN)
            self.label_at_02.grid(row=0, column=2, columnspan=20)
    
    
    def get_sampwidth_from_number(self, dtype: int) -> str:
        match dtype:
            case 1:
                dtype = "uint8"
            case 2:
                dtype = "int16"
            case 3:
                dtype = "int24"
            case 4:
                dtype = "float32"
        
        return dtype
    
    
    def get_sampwidth_from_str(self, dtype: str) -> int:
        match dtype:
            case "uint8":
                dtype = 1
            case "int16":
                dtype = 2
            case "int24":
                dtype = 3
            case "float32":
                dtype = 4
        
        return dtype
    
    
    def update_time(self, timer: ctk.CTkLabel):
        if self.song_duration and self.timer_text < self.song_duration:
            self.timer_text = perf_counter() - self.start
            text = ("%.2f" % self.timer_text)
            timer.configure(text=text)
            self.window.after(self.timer_step_ms, self.update_time, timer)
            
            self.progress_bar.set(0)
    
    
    def export_to_wav(self, file_path: str|None=None):
        if not file_path:
            if not self.loaded_file:
                self.load_file()
                if not self.loaded_file:
                    return
            
            file_path = self.loaded_file
        
        with open(file_path, "rb") as f:
            data = f.read()
            sample_rate = int.from_bytes(data[0:4], "little")
            dtype = int.from_bytes(data[4:6], "little")
            dtype = self.get_sampwidth_from_number(dtype)
            data = np.frombuffer(data[8:], dtype=dtype)
        
        file_path = file_path.removesuffix(".erfan")
        self.m.export_to_wav(file_path, data, sample_rate, dtype)
        
    
    def save_as(self, file_path: str|None=None, fformat: str="wav", bitrate: int=320):
        remove_temp_file = False
        if not file_path:
            if not self.loaded_file:
                self.load_file()
                if not self.loaded_file:
                    return
            
            file_path = self.loaded_file
        
        direc, file_name = split(file_path)
        file_name, file_format = splitext(file_name)
        file_format = file_format[1:]
        
        print(fformat)
        file_save_path = asksaveasfilename(title="save to:",
                                           initialfile=file_name,
                                           defaultextension=f".{fformat}",
                                           filetypes=[("sound files", ".erfan"),
                                                      ("sound files", ".mp3"),
                                                      ("sound files", ".wav"),
                                                      ("sound files", ".aiff"),
                                                      ("sound files", ".aifc"),
                                                      ("sound files", ".aif"),
                                                      ("sound files", ".flac"),
                                                      ("sound files", ".ogg"),
                                                      ("sound files", ".m4a"),
                                                      ("sound files", ".aac"),
                                                      ("sound files", ".wma"),
                                                      ("erfan", ".erfan"),
                                                      ("mp3", ".mp3"),
                                                      ("wav", ".wav"),
                                                      ("aiff", ".aiff"),
                                                      ("aifc", ".aifc"),
                                                      ("aif", ".aif"),
                                                      ("wma", ".wma"),
                                                      ("flac", ".flac"),
                                                      ("ogg", ".ogg"),
                                                      ("m4a", ".m4a"),
                                                      ("aac", ".aac"),
                                                      ("wma", ".wma"),
                                                      ("All Files", ".*")])
        
        if not file_save_path:
            return
        
        fformat = splitext(file_save_path)[1]
        fformat = fformat.removeprefix(".")
        
        codec = fformat
        
        if fformat in ["aac", "m4a", "wma"]:
            codec = "adts"
        
        if fformat in ["aiff", "aifc", "aif"]:
            codec = "aiff"
        
        if direc:
            direc = direc+"/"
        
        if file_format == "erfan":
            wav_file_full_name = direc+file_name+".wav"
            if not exists(wav_file_full_name):
                remove_temp_file = True
            
            self.export_to_wav(file_path)
            file_format = "wav"
            file_path = direc+file_name+"."+file_format
            
        print(fformat)
        if codec in ["adts", "mp3", "aac"]:
            
            AudioSegment.from_file(file_path, file_format).export(file_save_path,
                                                                  format=fformat,
                                                                  bitrate=str(bitrate)+"k")
        else:
            AudioSegment.from_file(file_path, file_format).export(file_save_path,
                                                                  format=fformat)
        
        self.label_at_02.destroy()
        self.label_at_02 = ctk.CTkLabel(self.window,
                     text="successfully exported",
                     text_color=self.FG_GREEN)
        self.label_at_02.grid(row=0, column=2, columnspan=20)
        
        if remove_temp_file:
            remove(wav_file_full_name)
    
    
    def load_dragged(self, event):
        files = event.data.split("} {")
        for file_path in files:
            file_path = file_path.strip("{}")
            file_format = splitext(split(file_path)[1])[1][1:]
            if file_format in ["mp3", "wav", "ogg", "m4a", "aiff", "aifc", "aif", "flac", "wma", "aac", "erfan"]:
                break
        else:
            return
        
        self.loaded_file = file_path
        self.label_at_02.destroy()
        self.label_at_02 = ctk.CTkLabel(self.window,
                     text="file has been loaded",
                     text_color=self.FG_GREEN)
        self.label_at_02.grid(row=0, column=2, columnspan=20)
    
    
    def export(self):
        win_exists=False
        try:
            win_exists = self.export_window.winfo_exists()
        except AttributeError:
            self.export_window = ctk.CTkToplevel(self.window)
        
        if win_exists:
            return
        
        self.export_window.title("Export to:")
        self.export_window.resizable(False, False)
        self.export_window.geometry("220x360")
        
        
        ctk.CTkLabel(self.export_window,
                     text="Export to:").grid(row=0, column=0)
        
        ctk.CTkButton(self.export_window,
                      text="wav",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as()).grid(row=1,
                                                           column=0,
                                                           pady=self.export_buttons_pady,
                                                           padx=30)
        
        ctk.CTkButton(self.export_window,
                      text="mp3",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="mp3")).grid(row=2,
                                                                       column=0,
                                                                       pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="aiff",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="aiff")).grid(row=3,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="aifc",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="aifc")).grid(row=4,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="aif",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="aif")).grid(row=5,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="flac",
                      command=lambda: self.save_as(fformat="flac")).grid(row=6,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="ogg",
                      command=lambda: self.save_as(fformat="ogg")).grid(row=7,
                                                                       column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="m4a",
                      command=lambda: self.save_as(fformat="m4a")).grid(row=8,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="aac",
                      command=lambda: self.save_as(fformat="aac")).grid(row=9,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="wma",
                      command=lambda: self.save_as(fformat="wma")).grid(row=10,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
    
    
    def main(self):
        open_btn = ctk.CTkButton(self.window,
                             text="open file",
                             command=self.load_file,
                             width=80,
                             corner_radius=self.bcr)
        open_btn.grid(row=1, column=0, padx=4)
        
        export_btn = ctk.CTkButton(self.window,
                            text="export",
                            command=self.export,
                            width=80,
                            corner_radius=self.bcr)
        export_btn.grid(row=1, column=1, padx=4)
        
        play_btn = ctk.CTkButton(self.window,
                             text="play",
                             command=self.play_loaded,
                             width=80,
                             corner_radius=self.bcr)
        play_btn.grid(row=1, column=2, padx=4)
        
        drag_lab = ctk.CTkLabel(self.window,
                                text="drag",
                                width=280,
                                height=120,
                                fg_color=self.COLOR1,
                                text_color=self.GREY)
        drag_lab.place(relx=0.5, rely=0.55, anchor=ctk.CENTER)
        drag_lab.drop_target_register(DND_FILES)
        drag_lab.dnd_bind("<<Drop>>", self.load_dragged)



if __name__ == '__main__':
    app = App()