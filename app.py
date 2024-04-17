from soundtools import Music, SoundBuffer
import numpy as np
import matplotlib.pyplot as plt
import customtkinter as ctk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinterdnd2 import DND_FILES
from tkinterdnd2.TkinterDnD import _require, DnDWrapper
from soundfile import read as sfRead
from sys import exit as sysExit, argv, platform
from os import remove
from os.path import exists, split, splitext
from threading import Thread
from time import perf_counter
from pydub.audio_segment import AudioSegment
from pydub.playback import play as dubplay
from icon import daIconFile
from tempfile import mkstemp
from pyaudio import Stream
from subprocess import check_output, run


class Tk(ctk.CTk, DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = _require(self)


class App:
    def __init__(self) -> None:
        if platform == "win32":
            if not b"\n.erfan=" in check_output("assoc", shell=True):
                run(f"assoc .erfan={__file__}")

        
        self.ICON_PATH = mkstemp()[1]
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
        self.window.geometry("480x360")
        self.window.iconbitmap(default=self.ICON_PATH)
        
        self.m = Music()
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
                                               width=440,
                                               height=15)
        self.progress_bar.place(x=20, y=330)
        self.progress_bar.set(0)
        
        self.bcr = 8 # button_corner_radius
        self.export_buttons_pady = 2
        self.temp_wav_file = ""
        self.image_label = ctk.CTkLabel(self.window, text="test text")
        self.offset = 8
        
        self.label_at_02 = ctk.CTkLabel(self.window, text="")
        
        
        if len(argv) > 1 and exists(argv[1]):
            self.song_duration = 0
            x = Thread(target=self.play_and_close, args=(argv[1],))
            x.start()
            self.window.after(self.timer_step_ms, self.update_time, self.timer)
        
        self.main()
        self.iconFile.close()
        self.window.mainloop()
    
    
    def visualize_sound(self, wave: SoundBuffer, sample_rate: int) -> None:
        times = np.linspace(0, wave.size/sample_rate, wave.size)
        duration = wave.size / sample_rate
        
        
        plt.figure(figsize=(15, 5))
        plt.plot(times, wave)
        plt.title('wave:')
        plt.ylabel('Signal Value')
        plt.xlabel('Time (s)')
        plt.xlim(0, duration)
        plt.get_current_fig_manager().window.wm_iconbitmap(self.ICON_PATH)
        plt.show()
    
    
    def config_stream(self, samp_width: int, channels: int, sample_rate: int) -> Stream:
        if type(samp_width) == str:
            samp_width = self.get_sampwidth_from_str(samp_width)
        
        return self.m.AUDIO_OBJECT.open(format=samp_width,
                                        channels=channels,
                                        rate=sample_rate,
                                        output=True)
    
    
    def play_loaded(self) -> None:
        if self.loaded_file:
            y = Thread(target=self.play, args=(self.loaded_file,))
            y.start()
        
        else:
            self.play_file()
    
    
    def play(self, file_path: str) -> None:
        self.timer_text = 0
        
        fformat = splitext(file_path)[1]
        fformat = fformat.removeprefix(".")
        
        #-- for ".erfan" files --#
        if fformat == "erfan":
            with open(file_path, "rb") as f:
                data = f.read()
                sample_rate = int.from_bytes(data[0:4], "little")
                dtype = int.from_bytes(data[4:6], "little")
                strdtype = self.get_sampwidth_from_number(dtype)
                n_channels = int.from_bytes(data[6:8], "little")
                data = np.frombuffer(data[8:], dtype=strdtype)
                self.song_duration = data.size/sample_rate
                minuts = int(self.song_duration/60)
                seconds = self.song_duration - minuts*60
                timer_text = f"{minuts}:{round(seconds, 2)}"
                
                duration = ctk.CTkLabel(self.window,
                                        text=timer_text)
                duration.grid(row=0, column=1)
                
                self.m.stream.stop_stream()
                self.m.stream.close()
                self.m.stream = self.config_stream(samp_width=self.m.AUDIO_OBJECT.get_format_from_width(dtype),
                                                channels=n_channels,
                                                sample_rate=sample_rate)
                
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
            self.song_duration = data.size/sample_rate/data.ndim
            
            duration = ctk.CTkLabel(self.window,
                                    text=round(self.song_duration, 2))
            duration.grid(row=0, column=1)
            
            if data.dtype == "float64":
                data = data.astype(np.float32)
            
            dtype = self.get_sampwidth_from_str(data.dtype)
            
            self.m.stream.stop_stream()
            self.m.stream.close()
            self.m.stream = self.config_stream(samp_width=self.m.AUDIO_OBJECT.get_format_from_width(dtype),
                                               channels=data.ndim,
                                               sample_rate=sample_rate)
            
            self.window.after(self.timer_step_ms, self.update_time, self.timer)
            self.start = perf_counter()
            
            
            self.m.play_buffer(data)
            
    
    def play_and_close(self, file_name: str) -> None:
        self.loaded_file = file_name
        self.play(file_name)
        self.on_quit()
    
    
    def play_file(self) -> None:
        self.load_file()
       
        if self.loaded_file:
            y = Thread(target=self.play, args=(self.loaded_file,))
            y.start()
    
    
    def visualize_sound_file(self) -> None:
        if not self.loaded_file:
            self.load_file()
        if not self.loaded_file:
            return
        
        file_path = self.loaded_file
        
        fformat = splitext(file_path)[1]
        fformat = fformat.removeprefix(".")
        
        if fformat == "erfan":
            with open(self.loaded_file, "rb") as f:
                data = f.read()
                sample_rate = int.from_bytes(data[0:4], "little")
                dtype = int.from_bytes(data[4:6], "little")
                n_channels = int.from_bytes(data[6:8], "little")
                
                dtype = self.get_sampwidth_from_number(dtype)
                
                if n_channels > 1:
                    data = np.frombuffer(data[8:], dtype=dtype)[0]
                else:
                    data = np.frombuffer(data[8:], dtype=dtype)
        
        elif fformat in ["aac", "wma", "m4a"]:
            sound = AudioSegment.from_file(file_path, fformat)
            sample_rate = sound.frame_rate
            data = np.array(sound.get_array_of_samples(), dtype=np.float32)
        
        else:
            data, sample_rate = sfRead(file_path)
            if data.ndim > 1:
                data = data.reshape(2, data.size//data.ndim)[0]
        
        
        self.visualize_sound(data, sample_rate)
    
    
    def on_quit(self):
        self.iconFile.close()
        try:
            remove(self.ICON_PATH)
        except Exception:
            pass
        self.m.done()
        self.window.quit()
        sysExit()
    
    
    def load_file(self) -> None:
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
                                          ("sound files", ".aac"),
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
                                          ("aac", ".aac"),
                                          ("wma", ".wma"),
                                          ("any", ".*")])
        
        if file:
            self.loaded_file = file
            self.label_at_02.destroy()
            self.label_at_02 = ctk.CTkLabel(self.window,
                                            text="file has been loaded",
                                            text_color=self.FG_GREEN)
            self.label_at_02.place(relx=0.5, y=10, anchor="center")
    
    
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
    
    
    def update_time(self, timer: ctk.CTkLabel) -> None:
        if self.song_duration and self.timer_text < self.song_duration:
            self.timer_text = perf_counter() - self.start
            
            minuts = int(self.timer_text/60)
            seconds = self.timer_text - minuts*60
            text = "%d:%.2f" % (minuts, seconds)
            timer.configure(text=text)
            self.window.after(self.timer_step_ms, self.update_time, timer)
            
            self.progress_bar.set(self.timer_text/self.song_duration)
    
    
    def export_to_wav(self, file_path: str|None=None) -> None:
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
        
    
    def save_as(self, file_path: str|None=None, fformat: str="wav", bitrate: int=320) -> None:
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
        
        file_save_path = asksaveasfilename(title="save to:",
                                           initialdir=direc,
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
            direc += "/"
        
        if file_format == "erfan":
            wav_file_full_name = direc+file_name+".wav"
            if not exists(wav_file_full_name):
                remove_temp_file = True
            
            self.export_to_wav(file_path)
            file_format = "wav"
            file_path = direc+file_name+"."+file_format
        
        if fformat == "erfan":
            wav_file_full_name = direc+file_name+".wav"
            if not exists(wav_file_full_name):
                remove_temp_file = True
            
            AudioSegment.from_file(file_path, file_format).export(wav_file_full_name,
                                                                  format="wav")
            self.m.wav_to_erfan(wav_file_full_name)
        
        elif codec in ["adts", "mp3", "aac"]:
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
        self.label_at_02.place(relx=0.5, y=10, anchor="center")
        
        if remove_temp_file:
            remove(wav_file_full_name)
    
    
    def load_dragged(self, event) -> None:
        self.image_label.destroy()
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
        self.label_at_02.place(relx=0.5, y=10, anchor="center")
    
    
    def on_quit_TopLevel(self):
        self.export_window.destroy()
        del self.export_window
    
    
    def export(self) -> None:
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
        
        self.export_window.protocol("WM_DELETE_WINDOW", self.on_quit_TopLevel)
        
        
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
    
    
    def render_drag_name(self, event):
        file_name = split(event.data.strip("}{"))[1]
        self.image_label.destroy()
        self.image_label = ctk.CTkLabel(self.window,
                                        text=file_name)
        x, y = self.window.winfo_pointerxy()
        self.image_label.place(x=x - self.window.winfo_rootx() + self.offset,
                               y=y - self.window.winfo_rooty() + self.offset)
        
    
    def show_drag_name(self, event):
        file_name = split(event.data.strip("}{"))[1]
        self.label_at_02.destroy()
        self.label_at_02 = ctk.CTkLabel(self.window,
                                        text=file_name,
                                        text_color=self.FG_GREEN)
        self.label_at_02.place(relx=0.5, y=10, anchor="center")
    
    
    def remove_drag_name(self, event):
        self.image_label.destroy()
        self.label_at_02.destroy()
    
    
    def main(self) -> None:
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
        export_btn.grid(row=2, column=0, padx=4, pady=8)
        
        play_btn = ctk.CTkButton(self.window,
                                 text="play",
                                 command=self.play_loaded,
                                 width=80,
                                 corner_radius=self.bcr)
        play_btn.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)
        
        visualize_btn = ctk.CTkButton(self.window,
                                     text="visualize",
                                     command=self.visualize_sound_file,
                                     width=80,
                                     corner_radius=self.bcr)
        visualize_btn.place(relx=0.9, rely=0.1, anchor=ctk.CENTER)
        
        drag_lab = ctk.CTkLabel(self.window,
                                text="drag",
                                width=400,
                                height=190,
                                fg_color=self.COLOR1,
                                text_color=self.GREY)
        drag_lab.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
        drag_lab.drop_target_register(DND_FILES)
        drag_lab.dnd_bind("<<DropEnter>>", self.show_drag_name)
        drag_lab.dnd_bind("<<DropPosition>>", self.render_drag_name)
        drag_lab.dnd_bind("<<Drop>>", self.load_dragged)
        drag_lab.dnd_bind("<<DropLeave>>", self.remove_drag_name)



if __name__ == "__main__":
    app = App()
