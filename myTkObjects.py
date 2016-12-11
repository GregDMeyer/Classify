import Tkinter as tk
import tkFont
import string

FONT_FAMILY = ''

class Button( tk.Text, object ):

    def __init__(self,master,text='',command=None,color='green',disabled=False,staydown=False,down=False,*args,**kwargs):

        tk.Text.__init__(self,master,*args,**kwargs)

        self.tag_configure("center", justify='center')
        self.insert(tk.END,text,"center")
        self.command = command
        self.disabled = disabled
        self.state = 'inactive'
        self.staydown = staydown
        self.down = down
        if self.down and not self.staydown:
            raise Exception('Can\'t start down if staydown flag is False!')

        if color == 'green':
            self.bg = 'dark green'
            self.fg = 'papaya whip'
            self.activeColor = 'forest green'
            pass
        elif color == 'gray':
            self.bg = 'gray30'
            self.fg = 'papaya whip'
            self.activeColor = 'gray45'
            self.highlight = 'sky blue'
            self.disabledFg = 'slate gray'
            self.disabledBg = 'gray20'
            pass
        elif color == 'light gray':
            self.bg = 'gray70'
            self.fg = 'dark slate gray'
            self.activeColor = 'gray85'
            self.disabledFg = 'slate gray'
            self.disabledBg = 'gray78'
        elif color == 'dark blue':
            self.bg = 'navy'
            self.fg = 'light sky blue'
            self.activeColor = 'RoyalBlue4'
        else:
            raise Exception(color+' is not a valid color.')
            pass

        self.config(
            font=(FONT_FAMILY,20),
            state='disabled',
            cursor='arrow',
            height=1,
            relief='flat',
            bd=2,
            width=20,
            pady=2,
            highlightthickness=2,
            highlightcolor=self.bg,
            highlightbackground=self.bg,
            )
        if self.disabled:
            self.config(
                bg=self.disabledBg,
                fg=self.disabledFg,
                )
        else:
            self.config(
                bg=self.bg,
                fg=self.fg,
                )
        self.config(*args,**kwargs)

        if not self.disabled:
            self.bind('<Enter>',self._mouse_in)
            self.bind('<Leave>',self._mouse_out)
            self.bind('<Button-1>',self._mouse_down)
            self.bind('<ButtonRelease-1>',self._mouse_up)
            pass

        self.mouse = {
            'in':False,
            'down':False
        }

        self.active = False

    def _mouse_in(self,event):

        #print 'Mouse in.'
        self.mouse['in'] = True
        if not self.active:
            self.config(highlightcolor=self.activeColor,highlightbackground=self.activeColor)
            self.config(bg=self.activeColor,)
        if self.state == 'clicking':
            self.config(relief='sunken')
        pass

    def _mouse_out(self,event):

        #print 'Mouse out.'
        self.mouse['in'] = False
        if not self.staydown:
            self.config(relief='flat')
        if not self.active:
            self.config(bg=self.bg,)
            self.config(highlightcolor=self.bg,highlightbackground=self.bg)
        pass

    def _mouse_down(self,event):

        #print 'Mouse down.'
        self.mouse['down'] = True
        if self.mouse['in']:
            self.config( relief='sunken' )
            self.state = 'clicking'
            pass
        else:
            if not self.staydown:
                self.config( relief='flat' )
            elif self.state == 'down':
                self.config( relief='sunken')
        pass

    def _mouse_up(self,event):

        #print 'Mouse up.'
        self.mouse['down'] = False
        if not self.staydown:
            self.config(relief='flat')
        if self.mouse['in']:
            if self.staydown:
                self.state = 'down'
            else:
                self.state = 'active'
            pass
        else:
            self.state = 'inactive'
            pass
        if self.mouse['in'] and self.command:
            self.command( event )
            pass
        pass

    def unset(self):

        if not self.staydown:
            raise Exception('Can\'t call unset on a button without staydown=True.')

        self.state = 'inactive'
        self.config( relief = 'flat')

    def set(self):

        self.state = 'down'
        self.config( relief = 'sunken' )

    def make_active(self):

        self.active = True

        self.config(bg=self.highlight)
        pass

    def make_inactive(self):

        self.active = False

        self.config(bg=self.bg)

        pass

    def disable(self):

        self.config(
                bg=self.disabledBg,
                fg=self.disabledFg,
                )

        self.unbind('<Enter>',)
        self.unbind('<Leave>',)
        self.unbind('<Button-1>',)
        self.unbind('<ButtonRelease-1>',)

    def enable(self):

        self.config(
                bg=self.bg,
                fg=self.fg,
                )

        self.bind('<Enter>',self._mouse_in)
        self.bind('<Leave>',self._mouse_out)
        self.bind('<Button-1>',self._mouse_down)
        self.bind('<ButtonRelease-1>',self._mouse_up)

    def change_text(self, newtext):

        self.config(state='normal')
        self.delete(1.0,tk.END)
        self.insert(tk.END,newtext,"center")
        self.config(state='disabled')


    def pack(self,*args,**kwargs):

        kwargs['fill'] = 'x'

        super(Button,self).pack(*args,**kwargs)
        pass



class Entry( tk.Entry, object ):

    def __init__(self,master,text='',default_text=False,*args,**kwargs):

        tk.Entry.__init__(self,master,*args,**kwargs)

        self.bg='light sky blue'
        self.default_text = default_text

        self.config(
            font=(FONT_FAMILY,20),
            width=20,
            relief='flat',
            bg='light sky blue',
            highlightthickness=2,
            highlightcolor=self.bg,
            highlightbackground=self.bg,
            fg='dodger blue',
            )
        self.config(
            *args,
            **kwargs
            )


        self.text = text
        self.empty = not default_text
        self.insert(tk.END,self.text)
        if self.default_text:
            self.config(fg='navy')

        self.bind('<FocusIn>', self.FocusIn )
        self.bind('<FocusOut>', self.FocusOut )

    def FocusIn( self, event=None ):

        if self.empty:
            self.delete(0,tk.END)
            self.config(fg='navy')
            self.empty = False

        pass

    def FocusOut( self, event ):

        if not self.get():

            self.empty = True

            # make sure its not already in there
            if not self.default_text and not super(Entry,self).get() == self.text:
                self.config(fg='dodger blue')
                self.insert(tk.END,self.text)

        else:

            self.empty = False
            pass

    def pack(self,*args,**kwargs):

        if not 'ipady' in kwargs.keys():
            kwargs['ipady'] = 5
            pass

        kwargs['fill'] = 'x'

        super(Entry,self).pack(*args,**kwargs)
        pass

    def get(self,*args,**kwargs):

        if self.empty:
            return ''
        else:
            return super(Entry,self).get(*args,**kwargs)
            pass

    def clear(self):

        self.delete(0,tk.END)
        self.empty = True

        # should only do this when focus is out...
        if not self.default_text:
            self.config(fg='dodger blue')
            self.insert(tk.END,self.text)

    def insert_dry(self,text):
        self.FocusIn()
        self.insert(tk.END,text)


class Title( tk.Text ):

    def __init__(self,master,text='',**options):

        tk.Text.__init__(self,master,**options)

        self.tag_configure("center", justify='center')
        self.insert(tk.END,text,"center")

        self.bg='old lace'

        self.config(
            font=(FONT_FAMILY,25),
            state='disabled',
            cursor='arrow',
            height=1,
            relief='flat',
            bd=1,
            width=20,
            pady=10,
            bg='old lace',
            highlightthickness=2,
            highlightcolor=self.bg,
            highlightbackground=self.bg,
            fg='OrangeRed4',
            )


class Message( tk.Text, object ):

    def __init__(self,master,text='',*args,**kwargs):

        tk.Text.__init__(self,master,*args,**kwargs)

        self.tag_configure("center", justify='center')
        self.insert(tk.END,text,"center")

        self.bg='old lace'

        self.config(
            font=(FONT_FAMILY,15),
            state='disabled',
            cursor='arrow',
            relief='flat',
            bd=1,
            height=1,
            width=30,
            bg='old lace',
            highlightthickness=2,
            highlightcolor=self.bg,
            highlightbackground=self.bg,
            fg='OrangeRed4',
            )
        self.config(*args,**kwargs)

    def pack( self,*args,**kwargs ):

        kwargs[ 'fill' ] = 'x'

        super(Message,self).pack(*args,**kwargs)


class WarningManager( tk.Frame, object ):

    def __init__(self, master):

        self.master = master

        tk.Frame.__init__(self,self.master,height=0)

        self.warnings = {}

    # show a new warning
    def display_warning(self, name, text):

        # if this one already exists, it is cleared and replaced.
        if name in self.warnings.keys():
            self.warnings[ name ].pack_forget()
            self.warnings[ name ].destroy()
            pass

        numLines = text.count('\n') + 1

        self.warnings[ name ] = Message( self, text = text, height = numLines)
        self.warnings[ name ].pack(fill='x')

        if not self.winfo_ismapped():
            self._my_pack()
            pass

    # clear warning with name 'name'
    def clear(self, name):

        if not name in self.warnings.keys():

            raise Exception('There is no warning with name \''+name+'\'.')

        self.warnings[ name ].pack_forget()
        self.warnings[ name ].destroy()

        self.warnings.pop( name )

        if not self.warnings:
            self.pack_forget()
            pass


    # try to clear warning with name 'name', if it doesn't exist, that's fine.
    def try_clear(self, name):

        if not name in self.warnings.keys():

            return

        self.warnings[ name ].pack_forget()
        self.warnings[ name ].destroy()

        self.warnings.pop( name )

        if not self.warnings:
            self.pack_forget()
            pass


    # clear all warnings present.
    def clear_all(self):

        for child in self.winfo_children():
            child.pack_forget()
            child.destroy()

        self.warnings = {}

        self.pack_forget()


    def _my_pack(self):

        if self.packing:
            super(WarningManager,self).pack(*self.pack_args,**self.pack_kwargs)
            pass

        return


    def pack(self,*args,**kwargs):

        self.pack_args = args
        self.pack_kwargs = kwargs
        self.packing = True

