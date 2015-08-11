# Requires the Pillow library: https://pypi.python.org/pypi/Pillow

from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import *
from PIL import Image, ImageTk

import img
import config
import effects
import urllib.request
import os
import tempfile

def image_browse():
    file = askopenfilename(filetypes = config.filetypes)

    if file:
        image_load(file)

def image_save():
    file = asksaveasfilename(initialfile = img.filename + img.extension, filetypes = config.filetypes, defaultextension = '*' + img.extension)

    if file:
        window_busy(True)

        try:
            if config.preview_basis != "original":
                modified = eval('effects.' + img.effect + '(img.original.copy(), img)')
                modified.save(file)
            else:
                img.modified.save(file)
        except:
            display_error('Viga', 'Faili ' + file + ' salvestamine ebaõnnestus')

        window_busy(False)

def image_url():
    if len(browsebutton.grid_info()) != 0:
        # Kuvame kasti URL-i sisestamiseks

        browsebutton.grid_remove()
        savebutton.grid_remove()
        urlcancel.grid()
        urlentry.grid()
    else:
        # Kasutaja sisestas URL-i, laadime faili alla

        url = urlentry_text.get()

        try:
            tmpfile = tempfile.mkstemp()[1] # Salvestame pildi ajutise failina

            with urllib.request.urlopen(url) as response, open(tmpfile, 'wb') as outfile:
                filesize = response.info()['Content-Length']
                filesize = int(filesize if filesize else 0)
                buffersize = 2 ** 14 # Mitu baiti korraga alla laeme

                progressbar['value'] = 0
                progressbar['maximum'] = filesize
                progressbar.grid()
                root.update()

                while True:
                    buffer = response.read(buffersize)

                    if not buffer:
                        break

                    outfile.write(buffer)
                    outfile.flush()
                    progressbar['value'] += buffersize
                    root.update()

                progressbar.grid_remove()
                urlentry_text.set('')
                #shutil.copyfile(tmpfile, url.split('/')[-1])
                image_load(tmpfile, url.split('/')[-1])
                image_url_cancel()
        except:
            display_error('Viga', 'Pildifaili allalaadimine või avamine ebaõnnestus')

def image_url_cancel():
    urlentry.grid_remove()
    urlcancel.grid_remove()
    browsebutton.grid()
    savebutton.grid()

def display_error(title, text):
    messagebox.showwarning(title, text)
    window_busy(False)
    raise

def window_busy(state):
    if state:
        root.title(root.title() + ' ( töötan.. )')
        root.wm_attributes('-alpha', 0.9)
        root.update()
    else:
        root.title(root.title().replace(' ( töötan.. )', ''))
        root.wm_attributes('-alpha', 1)

def image_load(file, defaultname = None):
    global img

    window_busy(True)
    window_reset()

    try:
        img.original = Image.open(file)
    except:
        display_error('Viga', 'Pildi avamine töötlemiseks ebaõnnestus')

    (img.filename, img.extension) = os.path.splitext(defaultname if defaultname else file)

    img.original = img.original.convert('RGBA')
    img.preview = img.original.copy()
    img.preview.thumbnail(config.preview_size, Image.ANTIALIAS)
    img.preview_modified = img.preview.copy()
    img.thumbnail = img.original.copy()
    img.thumbnail.thumbnail(config.thumbnail_size, Image.ANTIALIAS)

    effects.setup(img)

    i = 0

    for (effect, description) in effects.identifiers:
        if config.thumbnail_basis != "thumbnail":
            thumbnail = eval('effects.' + effect + '(img.' + config.thumbnail_basis + '.copy(), img)')
            thumbnail.thumbnail(config.thumbnail_size, Image.ANTIALIAS)
        else:
            thumbnail = eval('effects.' + effect + '(img.thumbnail.copy(), img)')

        thumbnail = ImageTk.PhotoImage(thumbnail)
        frame = ttk.Frame(bottomframe, style = 'Thumbnail.TFrame')
        imagelabel = ttk.Label(frame, image = thumbnail, style = 'Image.TLabel', cursor = 'hand2')
        textlabel = ttk.Label(frame, text = description, style = 'ThumbnailText.TLabel')

        imagelabel.image = thumbnail # Haagime pildi vidina külge, et see funktsioonist väljudes ära ei kustuks
        imagelabel.effect = effect # Et me teaks, millist efekti rakendada
        imagelabel.bind('<Button-1>', image_effect_apply)

        frame.grid(row = 0, column = i, padx = 10, pady = 10)
        imagelabel.grid(row = 0, column = 0, padx = 5, pady = (5, 0))
        textlabel.grid(row = 1, column = 0, padx = 5, pady = (0, 2), ipady = 2, ipadx = 2)

        i += 1

    preview_display()
    window_prepare('default')
    window_busy(False)

def window_prepare(default_effect):
    savebutton.configure(state = '!disabled')
    previewframe.grid()
    scrollbar.grid()
    bottomcanvas.grid()
    bottomcanvas.xview_moveto(0)

    image_effect_apply(default_effect)

def window_reset():
    savebutton.configure(state = 'disabled')
    previewframe.grid_remove()
    scrollbar.grid_remove()
    bottomcanvas.grid_remove()
    image_url_cancel()

    for child in bottomframe.winfo_children():
        child.grid_forget()
        child.destroy()

def preview_display():
    global img, previewimage

    tmp = img.preview_modified.copy()

    if config.preview_basis != "preview":
        tmp.thumbnail(config.preview_size, Image.ANTIALIAS)

    preview = ImageTk.PhotoImage(tmp)

    previewimage.configure(image = preview)
    previewimage.image = preview
    previewimage.grid()

def image_effect_apply(event):
    global img

    if type(event) == str:
        for child in bottomframe.winfo_children():
            widget = child.winfo_children()[0]

            if widget.effect.lower() == event.lower():
                break
    else:
        window_busy(True)
        widget = event.widget

    for child in bottomframe.winfo_children():
        child.configure(style = 'Thumbnail.TFrame')
        child.winfo_children()[0].configure(cursor = 'hand2')
        child.winfo_children()[0].bind('<Button-1>', image_effect_apply)
        child.winfo_children()[1].configure(style = 'ThumbnailText.TLabel')

    widget.master.configure(style = 'Active.Thumbnail.TFrame')
    widget.master.winfo_children()[1].configure(style = 'Active.ThumbnailText.TLabel')
    widget.unbind('<Button-1>')
    widget.configure(cursor = '')

    img.preview_modified = eval('effects.' + widget.effect + '(img.' + config.preview_basis + '.copy(), img)')
    img.effect = widget.effect

    preview_display()
    window_busy(False)


## KASUTAJALIIDES ##

# Põhiaken
root = Tk()
root.title("Filter")
root.iconbitmap(default = 'images/thumb.ico')
root.geometry("+50+50")
root.rowconfigure(0, weight = 1)
root.columnconfigure(0, weight = 1)
root.resizable(0, 0)

config.preview_size = (root.winfo_screenwidth() - 40 - 2 * config.window_paddings[0],\
                root.winfo_screenheight() - config.thumbnail_size[1] - 130 - 2 * config.window_paddings[1])

# Stiiliredaktor
styles = ttk.Style()

styles.configure('Thumbnail.TFrame', padding = 20, background = '#d7d7d7')
styles.configure('Active.Thumbnail.TFrame', background = '#c14747')
styles.configure('Image.TLabel', padding = -2)
styles.configure('ThumbnailText.TLabel', background = '#d7d7d7', foreground = '#000000')
styles.configure('Active.ThumbnailText.TLabel', background = '#c14747', foreground = '#ffffff')

# Akna sisu
body = ttk.Frame(root)
body.grid(sticky = (N, S, E, W))
body.columnconfigure(0, weight = 1)

# Ülemine menüü
topframe = ttk.Frame(body)
topframe.grid(row = 0, column = 0, pady = 10, sticky = (N, S, E, W))

topframe.columnconfigure(0, weight = 1)
topframe.columnconfigure(1, weight = 1)
topframe.columnconfigure(2, weight = 1)
topframe.rowconfigure(0, weight = 1)

browsebutton = ttk.Button(topframe, text = ' Ava pilt arvutist ', command = image_browse)
browsebutton.grid(row = 0, column = 0, padx = 10)
savebutton = ttk.Button(topframe, text = 'Salvesta', command = image_save)
savebutton.grid(row = 0, column = 1, padx = 10)
savebutton.configure(state = 'disabled')

urlentry_text = StringVar()
urlentry = ttk.Entry(topframe, width = 40, textvariable = urlentry_text)
urlentry.grid(row = 0, column = 1, padx = 10)
urlentry.grid_remove()

urlframe = ttk.Frame(topframe)
urlframe.grid(row = 0, column = 2, padx = 10)
urlbutton = ttk.Button(urlframe, text = ' Ava pilt internetist ', command = image_url)
urlbutton.grid(row = 0, column = 0)
urlcancel = ttk.Button(urlframe, text = ' Tühista ', command = image_url_cancel)
urlcancel.grid(row = 0, column = 1, padx = (3, 0))
urlcancel.grid_remove()

progressbar = ttk.Progressbar(urlframe, orient = 'horizontal', mode = 'determinate')
progressbar.grid(row = 1, column = 0, pady = 5, columnspan = 2, sticky = (W, E))
progressbar.grid_remove()

# Pildi eelvaade
previewframe = ttk.Frame(body)
previewframe.columnconfigure(0, weight = 1)
previewframe.rowconfigure(0, weight = 1)
previewframe.grid(row = 2, column = 0)
previewframe.grid_remove()

previewimage = ttk.Label(previewframe, style = 'Image.TLabel')
previewimage.grid(row = 0, column = 0)

# Alumine menüü
scrollbar = ttk.Scrollbar(body, orient = HORIZONTAL)
scrollbar.grid(row = 5, column = 0, sticky = (E, W))
scrollbar.grid_remove()

bottomcanvas = Canvas(body, xscrollcommand = scrollbar.set)
bottomcanvas.grid(row = 4, column = 0, sticky = (E, W))
bottomcanvas.grid_remove()

bottomframe = ttk.Frame(bottomcanvas)
bottomframe.grid(row = 0, column = 0)
bottomframe_id = bottomcanvas.create_window(0, 0, window = bottomframe, anchor = NW)
scrollbar.config(command = bottomcanvas.xview)

def _configure_frame(event):
    reqsize = (bottomframe.winfo_reqwidth(), bottomframe.winfo_reqheight())
    bottomcanvas.config(scrollregion = "0 0 %s %s" %reqsize)

    if reqsize[1] != bottomcanvas.winfo_height():
        bottomcanvas.config(height = reqsize[1])

def _configure_canvas(event):
    if bottomframe.winfo_reqheight() != bottomcanvas.winfo_height():
        bottomcanvas.itemconfigure(bottomframe_id, height = bottomcanvas.winfo_height())

    if bottomframe.winfo_reqwidth() <= previewframe.winfo_reqwidth():
        scrollbar.grid_remove()

bottomcanvas.bind('<Configure>', _configure_canvas)
bottomframe.bind('<Configure>', _configure_frame)

if config.debug:
    image_load("demo.jpg")

root.mainloop()
