from soundtools import Music, SoundBuffer, Dtype
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
from pydub.audio_segment import AudioSegment
from icon import daIconFile
from tempfile import mkstemp
from pyaudio import Stream
from subprocess import check_output, run
from keyboard import is_pressed
from time import perf_counter


class Tk(ctk.CTk, DnDWrapper):
    def __init__(self, *args, **kwargs) -> None:
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
        self.loaded_buffer: SoundBuffer = np.array([])
        self.space_timeout = 0
        self.space_timeout_delay = 0.3
        
        self.loaded_file: str = ""
        self.original_wave: SoundBuffer = np.array([])
        self.chunk: int = self.default_chunk
        self.sample_rate: int = 1
        
        self.bcr = 8 # button_corner_radius
        self.export_buttons_pady = 2
        self.temp_wav_file = ""
        self.image_label = ctk.CTkLabel(self.window, text="", text_color="#409a73")
        self.offset = 8
        
        self.label_at_02 = ctk.CTkLabel(self.window, text="", text_color="#409a73")
        self.label_at_02.place(x=10, y=0)
        
        
        if len(argv) > 1 and exists(argv[1]):
            self.song_duration = 0
            self.loaded_file = argv[1]
            self.label_at_02.configure(text=f"Loaded: {split(self.loaded_file)[1]}")
            x = Thread(target=self.play, args=(argv[1],))
            x.start()
            self.window.after(self.timer_step_ms, self.update_time)
        
        self.main()
        
        self.image_label.tkraise()
        
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
        if not self.loaded_buffer.all():
            self.song_duration = self.loaded_buffer.size / self.m.input_rate
            minuts = int(self.song_duration/60)
            seconds = self.song_duration - minuts*60
            timer_text = f"{minuts}:{round(seconds, 2)}"
            self.duration.configure(text=timer_text)
            self.window.after(self.timer_step_ms, self.update_time)
            
            y = Thread(target=self.play_buffer, args=(self.loaded_buffer,))
            y.start()
        
        elif self.loaded_file:
            y = Thread(target=self.play, args=(self.loaded_file,))
            y.start()
        
        else:
            self.play_file()
    
    
    def play_buffer(self, wave: SoundBuffer|bytes, chunk:int|None=None) -> None:
        self.playing = True
        
        self.play_btn.configure(text="pause", command=self.stop_playing)
        
        if type(wave) == bytes:
            wave = np.frombuffer(wave, self.m.dtype)
        
        chunk = self.default_chunk if not chunk else chunk
        self.chunk = chunk
        self.n_chunks = int(wave.size / chunk)
        for i in range(self.n_chunks):
            self.i += 1
            if is_pressed("space") and perf_counter() > self.space_timeout:
                self.stop_playing()
                self.space_timeout = perf_counter()+self.space_timeout_delay
            if not self.playing:
                return
            
            b = wave[i*chunk : (i+1)*chunk].data.tobytes()
            self.m.stream.write(b)
        
        b = wave[(i+1)*chunk : ].data.tobytes()
        self.m.stream.write(b)
        
        self.playing = False
        self.stop_playing()
    
    
    def check_for_resume(self) -> None:
        if is_pressed("space") and perf_counter() > self.space_timeout:
            self.space_timeout = perf_counter()+self.space_timeout_delay
            self.resume(self.original_wave[self.i*self.chunk:])
            return
        
        if not self.playing:
            self.window.after(self.timer_step_ms, self.check_for_resume)
    
    
    def resume(self, wave: SoundBuffer) -> None:
        self.playing = True
        
        self.window.after(self.timer_step_ms, self.update_time)
        
        y = Thread(target=self.play_buffer, args=(wave,))
        y.start()
    
    
    def stop_playing(self) -> None:
        self.go_on = False
        if not self.playing:
            self.play_btn.configure(text="play", command=self.play_loaded)
        else:
            self.playing = False
            self.play_btn.configure(text="resume", command=lambda: self.resume(self.original_wave[self.i*self.chunk:]))
            self.window.after(self.timer_step_ms, self.check_for_resume)
    
    
    def play(self, file_path: str, chunk:int|None=None) -> None:
        self.playing = True
        self.timer_text = 0
        
        fformat = splitext(file_path)[1]
        fformat = fformat.removeprefix(".")
        
        chunk = self.default_chunk if not chunk else chunk
        self.chunk = chunk
        
        self.window.after(self.timer_step_ms, self.update_time)
        self.play_buffer(self.wave)
    
    
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
        self.stop_playing()
        try:
            with open(self.ICON_PATH, "wb") as f:
                f.truncate(0)
            remove(self.ICON_PATH)
            self.iconFile.close()
        except Exception:
            pass
        self.m.done()
        self.window.quit()
        sysExit()
    
    
    def setup_song_wave_duration(self, file_path: str) -> None:
        fformat = splitext(file_path)[1]
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
            minuts = int(self.song_duration/60)
            seconds = self.song_duration - minuts*60
            timer_text = f"{minuts}:{round(seconds, 2)}"
            self.duration.configure(text=timer_text)
            
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
            minuts = int(self.song_duration/60)
            seconds = self.song_duration - minuts*60
            timer_text = f"{minuts}:{round(seconds, 2)}"
                
            self.duration.configure(text=timer_text)
            
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
            
            minuts = int(self.song_duration/60)
            seconds = self.song_duration - minuts*60
            timer_text = f"{minuts}:{round(seconds, 2)}"
            self.duration.configure(text=timer_text)
            
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
            
            self.label_at_02.configure(text=f"Loaded: {split(file)[1]}")
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
    
    
    def get_sampwith_from_dtype(self, dtype: Dtype) -> int:
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
            self.timer_text = (self.original_wave.size - self.original_wave[self.i*self.chunk:].size) / self.sample_rate
            
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
    
    
    def save_recording(self, fformat: str="wav", bitrate: int=320) -> None:
        file_save_path = asksaveasfilename(title="save to:",
                                            initialfile="output",
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
        
        file_save_name, fformat = splitext(file_save_path)
        fformat = fformat.removeprefix(".")
        
        if fformat == "erfan":
            self.m.export_to_erfan(file_save_path,
                                   self.loaded_buffer,
                                   self.m.input_rate,
                                   self.m.input_dtype,
                                   self.loaded_buffer.ndim)
            return
        
        codec = fformat
        
        if fformat in ["aac", "m4a", "wma"]:
            codec = "adts"
        
        elif fformat in ["aiff", "aifc", "aif"]:
            codec = "aiff"
        
        file_save_wav = f"{file_save_name}.wav"
        remove_temp_file = False
        if not exists(file_save_wav):
            remove_temp_file = True
        
        self.m.export_to_wav(file_save_wav, self.loaded_buffer, self.m.input_rate, self.m.input_dtype)
        
        if fformat != "wav":
            file_save_name = splitext(file_save_path)[0]
            file_export_path = f"{file_save_name}.{fformat}"
            
            if codec in ["adts", "mp3"]:
                AudioSegment.from_file(file_save_wav, "wav").export(file_export_path,
                                                                     format=codec,
                                                                     bitrate=str(bitrate)+"k")
            else:
                AudioSegment.from_file(file_save_wav, "wav").export(file_export_path,
                                                                     format=codec)
            
            if remove_temp_file:
                remove(file_save_wav)

        self.label_at_02.configure(text="successfully exported")
    
    
    def save_file(self, file_path: str|None=None, fformat: str="wav", bitrate: int=320) -> None:
        remove_temp_file = False
        
        if not file_path:
            if not self.loaded_file:
                self.load_file()
                if not self.loaded_file:
                    return
            
            file_path = self.loaded_file
        
        direc, file_name = split(file_path)
        file_name, file_format = splitext(file_name)
        file_format = file_format.removeprefix(".")
        
        if file_format == fformat:
            return
        
        if direc:
            direc += "/"
        
        
        file_save_path = asksaveasfilename(title="save to:",
                                           initialdir=direc,
                                           initialfile=file_name,
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
        
        fformat = splitext(file_save_path)[1]
        fformat = fformat.removeprefix(".")
        
        codec = fformat
        
        if fformat in ["aac", "m4a", "wma"]:
            codec = "adts"
        
        elif fformat in ["aiff", "aifc", "aif"]:
            codec = "aiff"
        
        
        if file_format == "erfan":
            wav_file_full_name = direc+file_name+".wav"
            if not exists(wav_file_full_name) and fformat != "wav":
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
        
        elif codec in ["adts", "mp3"]:
            AudioSegment.from_file(file_path, file_format).export(file_save_path,
                                                                  format=codec,
                                                                  bitrate=str(bitrate)+"k")
        else:
            AudioSegment.from_file(file_path, file_format).export(file_save_path,
                                                                  format=codec)
        
        self.label_at_02.configure(text="successfully exported")
        
        if remove_temp_file:
            remove(wav_file_full_name)
    
    
    def save_as(self, file_path: str|None=None, fformat: str="wav", bitrate: int=320) -> None:
        if not self.loaded_buffer.all():
            self.save_recording(fformat, bitrate)
        
        else:
            self.save_file(file_path, fformat, bitrate)
        
    
    def load_dragged(self, event) -> None:
        self.image_label.place_forget()
        files = event.data.split("} {")
        for file_path in files:
            file_path = file_path.strip("{}")
            file_format = splitext(split(file_path)[1])[1][1:]
            if file_format in ["mp3", "wav", "ogg", "m4a", "aiff", "aifc", "aif", "flac", "wma", "aac", "erfan"]:
                break
        else:
            return
        
        self.i = 0
        self.playing = False
        self.stop_playing()
        
        self.loaded_file = file_path
        self.label_at_02.configure(text=f"Loaded: {split(file_path)[1]}")
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
        file_name = split(event.data.strip("}{"))[1]
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
            if is_pressed("space"):
                self.stop_record_func()
                return
            
            data = self.m.input_stream.read(self.m.input_chunk)
            self.recording += data
        
        self.m.input_stream.stop_stream()
        self.wave = np.frombuffer(self.recording, dtype=self.m.input_dtype)
        self.sample_rate = self.m.input_rate
    
    
    def stop_record_func(self) -> None:
        self.stop_record = True
        
        self.record_btn.configure(text="record",
                                  command=self.record_mic)
        
        self.label_at_02.configure(text="sound loaded")
        
        self.loaded_buffer = np.frombuffer(self.recording, self.m.input_dtype)
    
    
    def record_mic(self) -> None:
        self.record_btn.configure(text="stop",
                                  command=self.stop_record_func)
        
        x = Thread(target=self.record)
        x.start()
    
    
    def secs2time(self, secs) -> str:
        minuts = int(secs/60)
        seconds = secs - minuts*60
        return "%d:%.2f" % (minuts, seconds)
    
    
    def go_to(self, event) -> None:
        if self.playing:
            self.stop_playing()
            self.go_on = True
        self.slider_pos = event
        
        self.i = int(self.slider_pos * int(self.original_wave.size / self.chunk))
        self.timer_text = (self.original_wave.size - self.original_wave[self.i*self.chunk:].size) / self.sample_rate
        self.timer.configure(text=self.secs2time(self.timer_text))
    
    
    def end_go_to(self, event) -> None:
        self.wave = self.original_wave[int(self.original_wave.size*self.slider_pos):]
        self.i = int(self.slider_pos * int(self.original_wave.size / self.chunk))
        
        if not self.wave.size:
            self.playing = False
            self.stop_playing()
            return
        if self.go_on:
            self.resume(self.wave)
    
    
    def main(self) -> None:
        open_btn = ctk.CTkButton(self.window,
                                 text="open file",
                                 command=self.load_file,
                                 width=80,
                                 corner_radius=self.bcr)
        open_btn.place(relx=0.12, rely=0.12, anchor="center")
        
        export_btn = ctk.CTkButton(self.window,
                                   text="export",
                                   command=self.export,
                                   width=80,
                                   corner_radius=self.bcr)
        export_btn.place(relx=0.12, rely=0.22, anchor="center")
        
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
                                          height=18,
                                          command=self.go_to)
        self.progress_bar.place(relx=0.5, rely=0.92, anchor=ctk.CENTER)
        self.progress_bar.set(0)
        self.progress_bar.bind("<ButtonRelease-1>", self.end_go_to)



if __name__ == "__main__":
    App()
