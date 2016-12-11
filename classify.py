#!/usr/bin/env python
'''
Written by Greg Meyer and Allison Hsiang
'''

import Tkinter as tk
import tkMessageBox
from os import listdir
from os.path import isfile,join
import string
from getpass import getuser
import tkFileDialog
import glob
import sys
import csv
from PIL import ImageTk, Image
import myTkObjects as mtk
from tkentrycomplete import AutocompleteEntry

CLASSIFY_FIELDS = [
    'obj_num',
    'damage',
    'taxonomy',
    'taxonomy-conf'
]

ADDINFO_FIELDS = [
    'taphonomy',
    'predation',
    'encrusters'
]

FIELDS = CLASSIFY_FIELDS + ADDINFO_FIELDS + ['user']

class App(object):

    def __init__(self,master):

        self.master = master

        self.warning_manager = mtk.WarningManager( self.master )
        self.warning_manager.pack(side='bottom',fill='x')

        self.current = None
        self.change_state(Welcome)

        # get directory of images from user
        if len(sys.argv) == 1:
            self.image_dir = tkFileDialog.askdirectory()
        else:
            self.image_dir = sys.argv[1]

        self.scan = None
        self.ext = None
        self.age = None
        self.user = getuser() # get user name on the computer--some indicator of who is classifying
        self.data = {}
        self.image_list = []
        self.cur_img = None
        self.image_window = None

        self.add_info = False

        self.master.bind_all('<Command-w>',self.on_closing)
        
        # check if restarting from existing file
        files_in_dir = glob.glob(join(self.image_dir,'*_classification.csv'))
        
        if files_in_dir and tkMessageBox.askyesno('Classify','Classify file exists; load?'):

            if len(files_in_dir) == 1:
                self.filename = files_in_dir[0]
            else:
                tkMessageBox.showerror('Classify','Multiple Classify files exist; please choose which file you would like to load.')
                # TODO: make a list for them?
                self.filename = tkFileDialog.askopenfilename(initialdir=self.image_dir)
                while not self.filename.endswith('_classification.csv'):
                    tkMessageBox.showerror('That is not a classification file. Try again.')
                    self.filename = tkFileDialog.askopenfilename(initialdir=self.image_dir)

            self.append = True

            with open(self.filename) as f:
                # get image extension from file
                # don't forget to write this out!!!
                self.ext = f.readline().strip().split(',')[-1] # case insensitive

            self.skip_done = tkMessageBox.askyesno('Classify','Skip images with already complete classification?')
            
            print 'Restarting from file.'

            self.change_state(DataEntry)

        else:
            self.append = False
            self.change_state(GetScanName)


    def change_state(self,NewState):

        if self.current is not None:
            # get rid of any bindings that were still around
            for char in string.ascii_letters+string.digits+string.punctuation:
                if char == '<':
                    char = '<less>'
                self.current.frame.unbind_all(char)

            self.current.frame.unbind_all('<space>')
            self.current.frame.unbind_all('<BackSpace>')
            self.current.frame.unbind_all('<Return>')

            self.current.frame.pack_forget()
            self.current.frame.destroy()

            self.warning_manager.clear_all()

        self.current = NewState(self.master,self)
        return

    def write_data(self):
        with open(self.filename,'w') as f:
            w = csv.writer(f)
            w.writerow(FIELDS+[self.ext])
            for img_name in self.image_list:
                if img_name in self.data:
                    w.writerow([self.data[img_name][field] if field in self.data[img_name] else '' for field in FIELDS])

    def on_closing(self):
        '''close both windows when either is closed'''
        if self.image_window is not None:
            self.image_window.destroy()
        self.master.destroy()


class Welcome(object):

    def __init__(self,root,app):

        self.app = app
        self.frame = tk.Frame( root )
        self.frame.pack( fill='both',expand=True )

        self.scan_in = mtk.Message(self.frame,text='Welcome to Classify!')
        self.scan_in.pack()


class GetScanName(object):

    def __init__(self,root,app):

        self.app = app
        self.frame = tk.Frame( root )
        self.frame.pack( fill='both',expand=True )

        self.scan_in = mtk.Entry(self.frame,text='Scan name')
        self.scan_in.pack()

        self.age_in = mtk.Entry(self.frame,text='Age (optional)')
        self.age_in.pack()

        self.ext_in = mtk.Entry(self.frame,text='Extension')
        self.ext_in.pack()

        self.submit = mtk.Button(self.frame,text='Done',command=self._submit)
        self.frame.bind_all("<Return>",self._submit)  # bind enter to this also
        self.submit.pack()

    def _submit(self,event=None):

        if self.scan_in.get().strip() == "":
            tkMessageBox.showerror("Classify", "Enter a scan name.")
            return
        if self.ext_in.get().strip() == "":
            tkMessageBox.showerror("Classify", "Enter an image file extension.")
            return

        self.app.scan = self.scan_in.get().strip()
        self.app.ext = self.ext_in.get().strip().lower().lstrip('.')
        self.app.age = self.age_in.get().strip()

        # make sure this one doesn't already exist
        if isfile(join(self.app.image_dir,self.app.scan + '_classification.csv')):
            self.app.warning_manager.display_warning("name_taken", "That name is already taken!")
            self.app.scan = None
            self.app.ext = None
            # TODO: maybe see if they just want to use the existing one
            return

        # make sure files exist with that extension. .lower() makes it case insensitive
        if not any([x.split('.')[-1].lower() == self.app.ext for x in listdir(self.app.image_dir)]):
            self.app.warning_manager.display_warning("no_files", "No images found with that extension!")
            self.app.scan = None
            self.app.ext = None
            return

        print 'Scan name set to \'' + self.app.scan + '\''
        print 'File extension set to \'' + self.app.ext + '\''

        self.app.filename = join(self.app.image_dir,self.app.scan + '_classification.csv')

        self.app.change_state(DataEntry)


class DataEntry(object):

    def __init__(self,root,app):

        self.app = app
        self.frame = tk.Frame( root )
        self.frame.pack( fill='both',expand=True )

        # get list of images, and sort it (listdir sometimes gives different orders!)
        self.app.image_list = sorted([x for x in listdir(self.app.image_dir) if x.split('.')[-1].lower()==self.app.ext])

        # set up output file, and get data if it exists
        if self.app.append:
            # get data from file
            with open(self.app.filename) as f:
                f.readline() # to skip the headers
                for row in f.readlines():
                    row = row.strip().split(',')
                    if row[0] in self.app.data:
                        print 'Warning: same image num',row[0],'appears twice in file! overwriting...'
                    self.app.data[row[0]] = {FIELDS[n]:val for n,val in enumerate(row) if val!=''}

        # make frames for each of the modules
        self.module_frames = {'classify':tk.Frame(self.frame)}
        self.module_frames['classify'].pack(side='left',fill='both',expand=True)
        self.modules = {'classify':Classify(self.module_frames['classify'],self.app)}

        self.app.add_info = tkMessageBox.askyesno('Classify','Include additional information (taphonomy, predation, encrusters)?')
        if self.app.add_info:
            self.module_frames['add_info'] = tk.Frame(self.frame)
            self.module_frames['add_info'].pack(side='right',fill='both',expand=True)
            self.modules['add_info'] = AddInfo(self.module_frames['add_info'],self.app)

        
class Classify(object):

    def __init__(self,root,app):

        self.app = app
        self.frame = tk.Frame( root )
        self.frame.pack( fill='both',expand=True )

        # set up image display
        self.app.image_window = tk.Toplevel()
        self.app.image_window.geometry('+370+100')

        # close both when either is closed
        self.app.image_window.protocol("WM_DELETE_WINDOW", self.app.on_closing)
        self.app.master.protocol("WM_DELETE_WINDOW",self.app.on_closing)

        # bind keys to next/prev image
        self.frame.bind_all('<Left>',lambda event=None:self.next_image(forward=False))
        self.frame.bind_all('<Right>',lambda event=None:self.next_image())

        # now set up input interface
        self.this_img_data = None

        self.buttons = {}

        # damage level
        full = ['complete','fragment']
        damaged = ['damaged-outline intact','damaged-length intact','damaged-width intact']
        other = ['unidentifiable', 'junk image']
        colors = ['green','gray','dark blue']
        keys = string.lowercase

        button_count = 0

        for color,lst in zip(colors,[full,damaged,other]):
            for name in lst:
                self.buttons[name] = mtk.Button(self.frame, 
                                                text=name,
                                                command=self._make_selection_fn(name),
                                                color=color,
                                                staydown=True)
                self.buttons[name].pack()
                # attach key to button--can't do this with species entry!!
                # self.frame.bind_all(keys[button_count],self._make_selection_fn(name))
                button_count += 1

        # taxon ID
        # get the species list
        with open('app_species_list.csv') as f:
            r = csv.DictReader(f)
            species_data = [row['specName'] for row in r]

        # TODO: narrow by date (though the species file doesn't have dates...)
        self.species_entry = AutocompleteEntry(self.frame,
                                               keyrelease_callback=self._species_change_callback,
                                               text='Species ID')
        self.species_entry.set_completion_list(species_data)
        self.species_entry.pack()

        # confidence level
        self.confidence_label = mtk.Message(self.frame,text='Confidence:')
        self.confidence_label.pack()

        confidence = ['very','somewhat','not']
        #conf_keys = ['1','2','3']
        for name in confidence:
            # fix command here
            self.buttons[name] = mtk.Button(self.frame, 
                                            text=name, 
                                            color='light gray', 
                                            command=self._make_confidence_callback(name),
                                            staydown=True)
            # self.frame.bind_all(conf_keys[n],self._make_confidence_callback(name))
            self.buttons[name].pack()

        # display first image
        self.app.cur_img = -1 # to start at 0
        self.next_image()

    def _make_selection_fn(self,new_selection):

        def _f(event=None):

            if 'damage' in self.this_img_data:
                self.buttons[self.this_img_data['damage']].unset()
                # if it is the same one as before, unselect it
                if self.this_img_data['damage'] == new_selection:
                    self.this_img_data.pop('damage')
                    return

            self.this_img_data['damage'] = new_selection
            self.buttons[new_selection].set()

        return _f

    def _make_confidence_callback(self,conf):

        def _f(event=None):

            if self.species_entry.get() == '':
                tkMessageBox.showerror("Fragment", "Enter a taxon ID first!")
                self.buttons[conf].unset()
                return

            if 'taxonomy-conf' in self.this_img_data:
                self.buttons[self.this_img_data['taxonomy-conf']].unset()
                # if it is the same one as before, unselect it
                if self.this_img_data['taxonomy-conf'] == conf:
                    self.this_img_data.pop('taxonomy-conf')
                    return

            self.this_img_data['taxonomy-conf'] = conf

            self.buttons[conf].set()

        return _f

    # make sure we are keeping track of the contents in our data structure
    def _species_change_callback(self):
        spec_name = self.species_entry.get()
        if spec_name == '':
            if 'taxonomy' in self.this_img_data:
                self.this_img_data.pop('taxonomy')
        else:
            self.this_img_data['taxonomy'] = spec_name

        # and unpop the confidence button
        if 'taxonomy-conf' in self.this_img_data:
            self.buttons[self.this_img_data['taxonomy-conf']].unset()
            self.this_img_data.pop('taxonomy-conf')
        

    def display_image(self):

        # TODO: maybe the image window should really be its own class...
        # could easily just pass it the image name

        if hasattr(self,'iw_frame'):
            self.iw_frame.destroy()

        self.iw_frame = tk.Frame(self.app.image_window)
        self.iw_frame.pack()
        
        self.img = Image.open(join(self.app.image_dir,self.app.image_list[self.app.cur_img]))
        # resize while maintaining aspect ratio
        width,height = self.img.size
        adj_height = int(height * 600/float(width))
        self.img.resize((600,adj_height),Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(self.img)

        self.name = mtk.Message(self.iw_frame,text=str(self.app.cur_img + 1) + '/' + str(len(self.app.image_list)) + ': '+ self.app.image_list[self.app.cur_img])
        self.name.pack()
        
        self.panel = tk.Label(self.iw_frame,image=self.img,width=600)
        self.panel.pack(fill='both',expand='yes')

        self.app.master.wm_attributes("-topmost", 1)
        self.app.master.focus_force()

    def next_image(self,forward=True):

        next_image = self.app.cur_img + (1 if forward else -1)

        # if this one is done, iterate until we find one that isn't
        if self.app.append and self.app.skip_done:
            while True:
                if self.app.image_list[next_image] not in self.app.data:
                    break
                else:
                    this_img_data = self.app.data[self.app.image_list[next_image]]
                    # see if there are missing fields
                    if 'damage' not in this_img_data:
                        break
                    elif this_img_data['damage'] not in ['unidentifiable', 'junk image']: 
                        if 'taxonomy' not in this_img_data:
                            break
                        if 'taxonomy-conf' not in this_img_data:
                            break
                    elif self.app.add_info and any([field not in this_img_data for field in ADDINFO_FIELDS]):
                        break

                # otherwise this one was done
                next_image += 1 if forward else -1

        # we hit the end of the road. don't change anything
        if next_image < 0:
            return

        # unfortunately we have to actually rewrite the whole file on each save. that sucks but what can you do.
        # only do it if there is actually data to save though
        if self.this_img_data is not None:
            self.app.write_data()
            self.species_entry.clear()
            
        if next_image > len(self.app.image_list)-1:
            tkMessageBox.showinfo('Classify','All done!')
            self.app.on_closing()
            return

        self.app.cur_img = next_image

        # keep track of this image's data dict
        img_name = self.app.image_list[self.app.cur_img]
        if img_name not in self.app.data:
            self.app.data[img_name] = {'obj_num':img_name}
        self.this_img_data = self.app.data[img_name]
        # keep track of who is classifying it
        self.this_img_data['user'] = self.app.user

        for name,b in self.buttons.iteritems():
            b.unset()
            if 'damage' in self.this_img_data and self.this_img_data['damage'] == name:
                b.set()
            if 'taxonomy-conf' in self.this_img_data and self.this_img_data['taxonomy-conf'] == name:
                b.set()

        # put the text in the species box
        if 'taxonomy' in self.this_img_data:
            self.species_entry.insert_dry(self.this_img_data['taxonomy'])

        self.display_image()


class AddInfo(object):

    def __init__(self,root,app):

        self.app = app
        self.frame = tk.Frame( root )
        self.frame.pack( fill='both',expand=True )

        self.title = mtk.Title(self.frame,text='Additional Info')
        self.title.pack()

        self.sorry = mtk.Message(self.frame,text='Coming soon!')
        self.sorry.pack()



if __name__ == '__main__':

    root = tk.Tk()
    root.title('Classify')
    app = App(root)

    root.mainloop()
