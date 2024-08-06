import soundtools
import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import customtkinter as ctk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinterdnd2 import DND_FILES, TkinterDnD
from soundfile import read as sfRead
from threading import Thread
from pydub.audio_segment import AudioSegment
from time import time, ctime
from tempfile import mkstemp
from typing import Literal, NoReturn
from pyaudio import Stream
from icon import daIconFile


class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class App:
    WIDTH = 480
    HEIGHT = 360
    def __init__(self) -> None:
        if sys.platform == "win32":
            if not b"\n.erfan=" in subprocess.check_output("assoc", shell=True):
                subprocess.run(f"assoc .erfan={__file__}")

        
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
        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.window.iconbitmap(default=self.ICON_PATH)
        
        self.m = soundtools.Music()
        self.m.init()
        self.window.protocol("WM_DELETE_WINDOW", self.on_quit)
        
        self.timer_text: float = 0.0
        self.timer_step_ms: int = 10
        
        self.timer = ctk.CTkLabel(self.window,
                                  text="0:0.00")
        self.timer.place(relx=0.02, rely=0.92, anchor=ctk.W)
        
        self.duration = ctk.CTkLabel(self.window,
                                     text="")
        self.duration.place(relx=0.98, rely=0.92, anchor=ctk.E)
        
        self.default_chunk = 1600
        self.i = 0
        self.go_on = False
        self.playing = False
        self.stop_record = False
        self.recording: bytes = bytes()
        self.loaded_buffer: soundtools.SoundBuffer = np.array([])
        self.space_timeout = 0
        self.space_timeout_delay = 0.3
        
        self.loaded_file: str = ""
        self.original_wave: soundtools.SoundBuffer = np.array([])
        self.chunk: int = self.default_chunk
        self.sample_rate: int = 1
        
        self.bcr = 8 # button_corner_radius
        self.export_buttons_pady = 2
        self.temp_wav_file = ""
        self.image_label = ctk.CTkLabel(self.window, text="", text_color="#409a73")
        self.offset = 8
        
        self.label_at_02 = ctk.CTkLabel(self.window, text="", text_color="#409a73")
        self.label_at_02.place(x=10, y=0)
        
        self.main()
        
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            self.i = 0
            self.playing = False
            self.stop_playing()
            
            self.loaded_file = sys.argv[1]
            self.setup_song_wave_duration(sys.argv[1])
            
            self.label_at_02.configure(text=f"Loaded: {os.path.split(sys.argv[1])[1]}")
            self.loaded_buffer = np.array([])
            
            x = Thread(target=self.play, args=(sys.argv[1],))
            x.start()
            self.window.after(self.timer_step_ms, self.update_time)
        
        self.image_label.tkraise()
        
        self.window.mainloop()
    
    
    def visualize_sound(self, wave: soundtools.SoundBuffer, duration: float) -> None:
        times = np.linspace(0, duration, wave.size)
        
        plt.figure(figsize=(15, 5))
        plt.plot(times, wave)
        plt.title('wave:')
        plt.ylabel('Signal Value')
        plt.xlabel('Time (s)')
        plt.xlim(0, duration)
        plt.get_current_fig_manager().window.wm_iconbitmap(self.ICON_PATH)
        plt.show()
    
    
    def config_stream(self, samp_width: Literal[1, 4, 8, 32, "uint8", "int16", "int24", "float32"], channels: int, sample_rate: int) -> Stream:
        if type(samp_width) == str:
            samp_width = self.m.AUDIO_OBJECT.get_format_from_width(self.get_sampwidth_from_str(samp_width))
        
        return self.m.AUDIO_OBJECT.open(format=samp_width,
                                        channels=channels,
                                        rate=sample_rate,
                                        output=True)
    
    
    def play_loaded(self) -> None:
        if not self.loaded_buffer.all():
            self.song_duration = self.loaded_buffer.size / self.m.input_rate
            self.duration.configure(text=self.secs2time(self.song_duration))
            self.window.after(self.timer_step_ms, self.update_time)
            
            Thread(target=self.play_buffer, args=(self.loaded_buffer,)).start()
        
        elif self.loaded_file:
            Thread(target=self.play, args=(self.loaded_file,)).start()
        
        else:
            self.play_file()
    
    
    def play_buffer(self, wave: soundtools.SoundBuffer|bytes, chunk:int|None=None) -> None:
        self.playing = True
        
        self.play_btn.configure(text="pause", command=self.stop_playing)
        
        if type(wave) == bytes:
            wave = np.frombuffer(wave, self.m.dtype)
        
        chunk = self.default_chunk if not chunk else chunk
        self.chunk = chunk
        self.n_chunks = int(wave.size / chunk)
        for i in range(self.n_chunks):
            self.i += 1
            # if is_pressed("space") and perf_counter() > self.space_timeout:
            #     self.stop_playing()
            #     self.space_timeout = perf_counter()+self.space_timeout_delay
            if not self.playing:
                return
            
            b = wave[i*chunk : (i+1)*chunk].data.tobytes()
            self.m.stream.write(b)
        
        b = wave[(i+1)*chunk : ].data.tobytes()
        self.m.stream.write(b)
        
        self.playing = False
        self.stop_playing()
    
    
    def check_for_resume(self) -> None:
        # if is_pressed("space") and perf_counter() > self.space_timeout:
        #     self.space_timeout = perf_counter()+self.space_timeout_delay
        #     self.resume(self.original_wave[self.i*self.chunk:])
        #     return
        
        if not self.playing:
            self.window.after(self.timer_step_ms, self.check_for_resume)
    
    
    def resume(self, wave: soundtools.SoundBuffer) -> None:
        self.playing = True
        
        self.window.after(self.timer_step_ms, self.update_time)
        
        y = Thread(target=self.play_buffer, args=(wave,))
        y.start()
    
    
    def stop_playing(self) -> None:
        self.go_on = False
        if not self.playing:
            self.i = 0
            self.wave = self.original_wave
            self.play_btn.configure(text="play", command=self.play_loaded)
        else:
            self.playing = False
            self.play_btn.configure(text="resume", command=lambda: self.resume(self.original_wave[self.i*self.chunk:]))
            self.window.after(self.timer_step_ms, self.check_for_resume)
    
    
    def play(self, file_path: str, chunk:int|None=None) -> None:
        self.playing = True
        self.timer_text = 0
        
        fformat = os.path.splitext(file_path)[1]
        fformat = fformat.removeprefix(".")
        
        self.chunk = self.default_chunk if not chunk else chunk
        
        self.window.after(self.timer_step_ms, self.update_time)
        self.play_buffer(self.wave)
    
    
    def play_file(self) -> None:
        self.load_file()
        
        if self.loaded_file:
            y = Thread(target=self.play, args=(self.loaded_file,))
            y.start()
    
    
    def visualize_sound_file(self) -> None:
        if not self.loaded_buffer.all():
            self.visualize_sound(self.loaded_buffer, self.song_duration)
            return
        
        
        if not self.loaded_file:
            self.load_file()
            if not self.loaded_file:
                return
        
        self.visualize_sound(self.wave, self.song_duration)
    
    
    def on_quit(self) -> NoReturn:
        self.stop_playing()
        try:
            self.iconFile.close()
            with open(self.ICON_PATH, "wb") as f:
                f.truncate(0)
            os.remove(self.ICON_PATH)
        except Exception:
            pass
        self.m.done()
        self.window.quit()
        sys.exit()
    
    
    def setup_song_wave_duration(self, file_path: str) -> None:
        fformat = os.path.splitext(file_path)[1]
        fformat = fformat.removeprefix(".")
        
        #-- for ".erfan" files --#
        if fformat == "erfan":
            with open(file_path, "rb") as f:
                data = f.read()
                self.sample_rate = int.from_bytes(data[0:4], "little")
                dtype = int.from_bytes(data[4:6], "little")
                strdtype = self.get_sampwidth_from_number(dtype)
                n_channels = int.from_bytes(data[6:8], "little")
                data = np.frombuffer(data[8:], dtype=strdtype)
            
            self.song_duration = data.size/self.sample_rate/data.ndim
            self.duration.configure(text=self.secs2time(self.song_duration))
            
            self.original_wave = self.wave = self.m.read_from_erfan(file_path)
            
            self.m.stream.stop_stream()
            self.m.stream.close()
            self.m.stream = self.config_stream(samp_width=self.m.AUDIO_OBJECT.get_format_from_width(dtype),
                                               channels=n_channels,
                                               sample_rate=self.sample_rate)
        
        #-- for adts files --#
        elif fformat in ["aac", "wma", "m4a"]:
            sound = AudioSegment.from_file(file_path, fformat)
            
            self.song_duration = sound.duration_seconds
            self.duration.configure(text=self.secs2time(self.song_duration))
            
            self.sample_rate = sound.frame_rate
            self.original_wave = self.wave = np.frombuffer(sound._data, self.get_sampwidth_from_number(sound.sample_width))

            self.m.stream.stop_stream()
            self.m.stream.close()
            self.m.stream = self.config_stream(samp_width=self.m.AUDIO_OBJECT.get_format_from_width(sound.sample_width),
                                               channels=sound.channels,
                                               sample_rate=self.sample_rate)
        
        #-- other files such as mp3, ogg, wav, aiff, flac --#
        else:
            data, self.sample_rate = sfRead(file_path)
            self.song_duration = data.size/self.sample_rate/data.ndim
            self.duration.configure(text=self.secs2time(self.song_duration))
            
            if data.dtype == "float64":
                data = data.astype(np.float32)
            
            self.original_wave = self.wave = data
            
            dtype = self.get_sampwidth_from_str(data.dtype)
            
            self.m.stream.stop_stream()
            self.m.stream.close()
            self.m.stream = self.config_stream(samp_width=self.m.AUDIO_OBJECT.get_format_from_width(dtype),
                                               channels=data.ndim,
                                               sample_rate=self.sample_rate)
    
    
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
            self.setup_song_wave_duration(file)
            
            self.i = 0
            self.playing = False
            self.stop_playing()
            
            self.label_at_02.configure(text=f"Loaded: {os.path.split(file)[1]}")
            self.loaded_buffer = np.array([])
    
    
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
    
    
    def get_sampwith_from_dtype(self, dtype: soundtools.Dtype) -> int:
        match dtype:
            case np.uint8:
                dtype = 1
            case np.int16:
                dtype = 2
            case np.float32:
                dtype = 4
        
        return dtype
    
    
    def update_time(self) -> None:
        if not self.playing:
            return
        
        if self.song_duration and self.timer_text < self.song_duration:
            self.timer_text = (self.original_wave.size - self.original_wave[self.i*self.chunk:].size) / self.sample_rate / self.original_wave.ndim
            
            self.timer.configure(text=self.secs2time(self.timer_text))
            self.window.after(self.timer_step_ms, self.update_time)
            
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
        
        file_path = file_path.removesuffix(".erfan") + ".wav"
        self.m.export_to_wav(file_path, data, sample_rate, dtype)
    
    
    def save_as(self, fformat: str="wav", bitrate: int=320) -> None:
        file_save_path = asksaveasfilename(title="save to:",
                                           initialfile=f"output.{fformat}",
                                           defaultextension=fformat,
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
        
        direc, file_name = os.path.split(file_save_path)
        file_name, file_format = os.path.splitext(file_name)
        file_format = file_format.removeprefix(".")
        
        temp_file_path = os.path.join(direc, f"temp {ctime(time()).replace(":", "-")}.wav")
        self.m.export_to_wav(temp_file_path, self.original_wave, self.sample_rate, self.original_wave.dtype)
        
        if file_format in ["aac", "m4a", "wma"]:
            codec = "adts"
        
        elif file_format in ["aiff", "aifc", "aif"]:
            codec = "aiff"
        
        else:
            codec = file_format
        
        
        if file_format == "erfan":
            self.m.wav_to_erfan(temp_file_path, file_save_path)
        
        elif codec in ["adts", "mp3"]:
            AudioSegment.from_file(temp_file_path, "wav").export(file_save_path,
                                                                 format=codec,
                                                                 bitrate=str(bitrate)+"k")
        else:
            AudioSegment.from_file(temp_file_path, "wav").export(file_save_path,
                                                                 format=codec)
        
        self.label_at_02.configure(text="successfully exported")

        os.remove(temp_file_path)
    

    def load_dragged(self, event) -> None:
        self.image_label.place_forget()
        files = event.data.split("} {")
        for file_path in files:
            file_path = file_path.strip("{}")
            file_format = os.path.splitext(os.path.split(file_path)[1])[1][1:]
            if file_format in ["mp3", "wav", "ogg", "m4a", "aiff", "aifc", "aif", "flac", "wma", "aac", "erfan"]:
                break
        else:
            return
        
        self.i = 0
        self.playing = False
        self.stop_playing()
        
        self.loaded_file = file_path
        self.setup_song_wave_duration(file_path)
        
        self.label_at_02.configure(text=f"Loaded: {os.path.split(file_path)[1]}")
        self.loaded_buffer = np.array([])
    
    
    def on_quit_TopLevel(self) -> None:
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
        self.export_window.geometry("220x390")
        
        self.export_window.protocol("WM_DELETE_WINDOW", self.on_quit_TopLevel)
        
        
        ctk.CTkLabel(self.export_window,
                     text="Export to:").grid(row=0, column=0)
        
        ctk.CTkButton(self.export_window,
                      text="erfan",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="erfan")).grid(row=1,
                                                                          column=0,
                                                                          pady=self.export_buttons_pady,
                                                                          padx=30)
        
        ctk.CTkButton(self.export_window,
                      text="wav",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as()).grid(row=2,
                                                           column=0,
                                                           pady=self.export_buttons_pady,)
        
        ctk.CTkButton(self.export_window,
                      text="mp3",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="mp3")).grid(row=3,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="aiff",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="aiff")).grid(row=4,
                                                                         column=0,
                                                                         pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="aifc",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="aifc")).grid(row=5,
                                                                         column=0,
                                                                         pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="aif",
                      corner_radius=self.bcr,
                      command=lambda: self.save_as(fformat="aif")).grid(row=6,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="flac",
                      command=lambda: self.save_as(fformat="flac")).grid(row=7,
                                                                         column=0,
                                                                         pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="ogg",
                      command=lambda: self.save_as(fformat="ogg")).grid(row=8,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="m4a",
                      command=lambda: self.save_as(fformat="m4a")).grid(row=9,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="aac",
                      command=lambda: self.save_as(fformat="aac")).grid(row=10,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
        
        ctk.CTkButton(self.export_window,
                      text="wma",
                      command=lambda: self.save_as(fformat="wma")).grid(row=11,
                                                                        column=0,
                                                                        pady=self.export_buttons_pady)
    
    
    def render_drag_name(self, event) -> None:
        x, y = self.window.winfo_pointerxy()
        self.image_label.place_configure(x=x - self.window.winfo_rootx() + self.offset,
                                         y=y - self.window.winfo_rooty() + self.offset)
        
    
    def show_drag_name(self, event) -> None:
        file_name = os.path.split(event.data.strip("}{"))[1]
        self.label_at_02.configure(text=file_name)
        self.image_label.configure(text=file_name)
        self.image_label.place()
    
    
    def remove_drag_name(self, event) -> None:
        self.image_label.configure(text="")
        self.image_label.place_forget()
        self.label_at_02.configure(text="")
    
    
    def record(self) -> bytes:
        self.recording: bytes = bytes()
        
        while not self.stop_record:
            # if is_pressed("space"):
            #     self.stop_record_func()
            #     return
            
            data = self.m.input_stream.read(self.m.input_chunk)
            self.recording += data
        
        self.m.input_stream.stop_stream()
        self.wave = np.frombuffer(self.recording, dtype=self.m.input_dtype)
        self.original_wave = self.wave
        self.sample_rate = self.m.input_rate
        
        self.i = 0
        
        self.play_btn.configure(text="play", command=self.play_loaded)
    
    
    def stop_record_func(self) -> None:
        self.stop_record = True
        
        self.record_btn.configure(text="record",
                                  command=self.record_mic)
        
        self.label_at_02.configure(text="sound loaded")
        
        self.loaded_buffer = np.frombuffer(self.recording, self.m.input_dtype)
        self.song_duration = self.loaded_buffer.size / self.m.input_rate
    
    
    def record_mic(self) -> None:
        self.record_btn.configure(text="stop",
                                  command=self.stop_record_func)
        
        x = Thread(target=self.record)
        x.start()
    
    
    def secs2time(self, secs) -> str:
        minuts = int(secs/60)
        seconds = secs - minuts*60
        return f"{minuts}:{seconds:0>5.2f}"
    
    
    def go_to(self, event) -> None:
        if self.playing:
            self.stop_playing()
            self.go_on = True
        self.slider_pos = event
        
        self.i = int(self.slider_pos * int(self.original_wave.size / self.chunk / self.original_wave.ndim))
        self.timer_text = (self.original_wave.size - self.original_wave[self.i*self.chunk:].size) / self.sample_rate / self.original_wave.ndim
        self.timer.configure(text=self.secs2time(self.timer_text))
    
    
    def end_go_to(self, event) -> None:
        self.wave = self.original_wave[int(self.original_wave.size*self.slider_pos/self.original_wave.ndim):]
        self.i = int(self.slider_pos * int(self.original_wave.size / self.chunk / self.original_wave.ndim))
        
        if not self.wave.size:
            self.playing = False
            self.stop_playing()
            return
        if self.go_on:
            self.resume(self.wave)
    
    
    def reverse(self) -> None:
        self.wave = np.flip(self.wave)
        self.original_wave = np.flip(self.original_wave)
        self.label_at_02.configure(text="successfully reversed")
    
    
    def main(self) -> None:
        open_btn = ctk.CTkButton(self.window,
                                 text="open file",
                                 command=self.load_file,
                                 width=80,
                                 corner_radius=self.bcr)
        open_btn.place(relx=0.12, rely=0.12, anchor=ctk.CENTER)
        
        export_btn = ctk.CTkButton(self.window,
                                   text="export",
                                   command=self.export,
                                   width=80,
                                   corner_radius=self.bcr)
        export_btn.place(relx=0.12, rely=0.22, anchor=ctk.CENTER)
        
        self.play_btn = ctk.CTkButton(self.window,
                                      text="play",
                                      command=self.play_loaded,
                                      width=80,
                                      corner_radius=self.bcr)
        self.play_btn.place(relx=0.5, rely=0.22, anchor=ctk.CENTER)
        
        self.record_btn = ctk.CTkButton(self.window,
                                        text="record",
                                        command=self.record_mic,
                                        width=80,
                                        corner_radius=self.bcr)
        self.record_btn.place(relx=0.5, rely=0.12, anchor=ctk.CENTER)
        
        visualize_btn = ctk.CTkButton(self.window,
                                      text="visualize",
                                      command=self.visualize_sound_file,
                                      width=80,
                                      corner_radius=self.bcr)
        visualize_btn.place(relx=0.87, rely=0.12, anchor=ctk.CENTER)
        
        reverse_btn = ctk.CTkButton(self.window,
                                    text="reverse",
                                    command=self.reverse,
                                    width=80,
                                    corner_radius=self.bcr)
        reverse_btn.place(relx=0.87, rely=0.22, anchor=ctk.CENTER)
        
        drag_lab = ctk.CTkLabel(self.window,
                                text="drag",
                                width=440,
                                height=190,
                                fg_color=self.COLOR1,
                                text_color=self.GREY)
        drag_lab.place(relx=0.5, rely=0.57, anchor=ctk.CENTER)
        drag_lab.drop_target_register(DND_FILES)
        drag_lab.dnd_bind("<<DropEnter>>", self.show_drag_name)
        drag_lab.dnd_bind("<<DropPosition>>", self.render_drag_name)
        drag_lab.dnd_bind("<<Drop>>", self.load_dragged)
        drag_lab.dnd_bind("<<DropLeave>>", self.remove_drag_name)
        
        self.progress_bar = ctk.CTkSlider(self.window,
                                          width=370,
                                          height=17,
                                          command=self.go_to)
        self.progress_bar.place(relx=0.5, rely=0.92, anchor=ctk.CENTER)
        self.progress_bar.set(0)
        self.progress_bar.bind("<ButtonRelease-1>", self.end_go_to)



if __name__ == "__main__":
    App()
