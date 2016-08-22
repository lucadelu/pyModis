# -*- coding: utf-8 -*-

'''
A drop-in replacement for optparse ("import optparse_gui as optparse")
Provides an identical interface to optparse(.OptionParser),
But displays an automatically generated wx dialog in order to enter the
options/args, instead of parsing command line arguments

Classes:

* :class:`OptparseDialog`
* :class:`UserCancelledError`
* :class:`Option`
* :class:`OptionParser`

Functions:

* :func:`checkLabel`

'''

# python 2 and 3 compatibility
from builtins import dict


import os
import sys
import optparse
try:
    import wx
    import wx.lib.filebrowsebutton as filebrowse
except:
    pass

__version__ = 0.2
__revision__ = '$Id$'

# for required options
from .optparse_required import STREQUIRED

TEXTCTRL_SIZE = (400, -1)


def checkLabel(option):
    """Create the label for an option, it add the required string if needed

       :param option: and Option object
    """
    label = option.dest
    label = label.replace('_', ' ')
    label = label.replace('--', '')
    label = label.capitalize()
    if option.required is True:
        return "{lab} [{req}]".format(lab=label, req=STREQUIRED)
    else:
        return label


class OptparseDialog(wx.Dialog):
    '''The dialog presented to the user with dynamically generated controls,
    to fill in the required options.

    :param optParser: the optparse object
    :param str title: the title to add in the GUI
    :param parent: the parent GUI
    :param int ID: the ID of GUI
    :param pos: the position of GUI
    :param size: the dimension of GUI
    :param style: the style of GUI

    Based on the wx.Dialog sample from wx Docs & Demos
    '''
    def __init__(self, optParser, title, parent=None, ID=0,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME):
        """Function for initialization"""

        # TODO fix icon
#        modis_icon = wx.Icon('/home/lucadelu/github/pyModis/pyModis.ico',
#                             wx.BITMAP_TYPE_ICO)
#        self.SetIcon(modis_icon)
        provider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(provider)

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)
        self.CenterOnScreen()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.args_ctrl = []
        self.option_controls = dict()

#       IN THE TOP OF GUI THERE WAS THE NAME OF THE SCRIPT, BUT NOW IT IS IN
#       THE TITLE

#        top_label_text = '%s %s' % (optParser.get_prog_name(),
#                                     optParser.get_version())
#        label = wx.StaticText(self, -1, top_label_text)
#        sizer.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        # Add a text control for entering args

        arg = self._checkArg(optParser.get_prog_name())
        sizer.Add(arg, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT |
                  wx.TOP, 5)

        self.browse_option_map = dict()
        # Add controls for all the options
        for option in optParser.list_of_option:
            if option.dest is None:
                continue

            if option.help is None:
                option.help = ''

            if checkLabel(option) == 'Formats':
                continue

            box = wx.BoxSizer(wx.HORIZONTAL)
            if 'store' == option.action:
                label = wx.StaticText(self, -1, checkLabel(option))
                label.SetHelpText(option.help.replace(' [default=%default]',
                                                      ''))
                box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

                if 'choice' == option.type:
                    choices = list(set(option.choices))
                    if optparse.NO_DEFAULT == option.default:
                        option.default = choices[0]
                    ctrl = wx.ComboBox(self, -1, choices=choices,
                                       value=option.default,
                                       size=TEXTCTRL_SIZE,
                                       style=wx.CB_DROPDOWN | wx.CB_READONLY |
                                       wx.CB_SORT)
                elif option.type in ['file', 'output']:
                    if option.type == 'file':
                        fmode = wx.OPEN
                    elif option.type == 'output':
                        fmode = wx.SAVE
                    ctrl = filebrowse.FileBrowseButton(self, id=wx.ID_ANY,
                                                       fileMask='*',
                                                       labelText='',
                                                       dialogTitle='Choose output file',
                                                       buttonText='Browse',
                                                       startDirectory=os.getcwd(),
                                                       fileMode=fmode,
                                                       size=TEXTCTRL_SIZE)
                elif option.type == 'directory':
                    ctrl = filebrowse.DirBrowseButton(self, id=wx.ID_ANY,
                                                      labelText='',
                                                      dialogTitle='Choose output file',
                                                      buttonText='Browse',
                                                      startDirectory=os.getcwd(),
                                                      size=TEXTCTRL_SIZE)
                else:
                    if 'MULTILINE' in option.help:
                        ctrl = wx.TextCtrl(self, -1, "", size=(400, 100),
                                           style=wx.TE_MULTILINE |
                                           wx.TE_PROCESS_ENTER)
                    else:
                        ctrl = wx.TextCtrl(self, -1, "", size=TEXTCTRL_SIZE)

                    if (option.default != optparse.NO_DEFAULT) and \
                       (option.default is not None):
                        ctrl.Value = str(option.default)

                box.Add(ctrl, 1, wx.ALIGN_RIGHT | wx.ALL, 5)

            elif option.action in ('store_true', 'store_false'):
                ctrl = wx.CheckBox(self, -1, checkLabel(option),
                                   size=(300, -1))
                box.Add(ctrl, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            elif option.action == 'group_name':
                label = wx.StaticText(self, -1, checkLabel(option))
                font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
                label.SetFont(font)
                box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
                ctrl = None
            else:
                raise NotImplementedError('Unknown option action: '
                                          '{act}'.format(act=repr(option.action)))
            if ctrl:
                ctrl.SetHelpText(option.help.replace(' [default=%default]',
                                                     ''))
                self.option_controls[option] = ctrl
            sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0,
                  wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def _getOptions(self):
        """Return a dictionary with the options and their values"""
        option_values = dict()
        for option, ctrl in self.option_controls.items():
            try:
                option_values[option] = ctrl.Value
            except:
                option_values[option] = ctrl.GetValue()

        return option_values

    def _checkArg(self, name):
        """Create an option in WX

        :param str name: the name of command to parse
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # check what is the module
        if name == 'modis_convert.py' or name == 'modis_parse.py' or \
           name == 'modis_quality.py':
            ltext = 'File HDF [%s]' % STREQUIRED
            self.htext = 'Select HDF file'
            self.typecont = 'file'
        elif name == 'modis_download.py' or \
             name == 'modis_download_from_list.py':
            ltext = 'Destination Folder [%s]' % STREQUIRED
            self.htext = 'Select directory where save MODIS files'
            self.typecont = 'dir'
        elif name == 'modis_mosaic.py':
            ltext = 'File containig HDF list [%s]' % STREQUIRED
            self.htext = 'Select file containig a list of MODIS file'
            self.typecont = 'file'
        elif name == 'modis_multiparse.py':
            ltext = 'List of HDF file [%s]' % STREQUIRED
            self.htext = 'List of MODIS files'
            self.typecont = 'mfile'
        else:
            ltext = 'Test'
            self.htext = 'Test'
        label = wx.StaticText(self, -1, ltext)
        label.SetHelpText(self.htext)

        sizer.Add(item=label, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL |
                  wx.ALL, border=5)

        if self.typecont == 'dir':
            self.arg_ctrl = filebrowse.DirBrowseButton(self, id=wx.ID_ANY,
                                                       labelText='',
                                                       dialogTitle=self.htext,
                                                       buttonText='Browse',
                                                       startDirectory=os.getcwd(),
                                                       changeCallback=self.onText,
                                                       size=TEXTCTRL_SIZE)
        elif self.typecont in ['file', 'mfile']:
            self.arg_ctrl = filebrowse.FileBrowseButton(self, id=wx.ID_ANY,
                                                        fileMask='*',
                                                        labelText='',
                                                        dialogTitle=self.htext,
                                                        buttonText='Browse',
                                                        startDirectory=os.getcwd(),
                                                        fileMode=wx.OPEN,
                                                        changeCallback=self.onText,
                                                        size=TEXTCTRL_SIZE)
        sizer.Add(item=self.arg_ctrl, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
        return sizer

    def onText(self, event):
        """File changed"""
        myId = event.GetId()
        me = wx.FindWindowById(myId)
        wktfile = me.GetValue()
        if len(wktfile) > 0:
            if self.typecont == 'mfile':
                self.args_ctrl.append(wktfile.split(','))
            else:
                self.args_ctrl.append(wktfile)
        event.Skip()

    def onBrowse(self, event):
        """Choose file"""
        dlg = wx.FileDialog(parent=self, message=self.htext,
                            defaultDir=os.getcwd(), style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.args_ctrl.SetValue(path)
        dlg.Destroy()
        event.Skip()

    def getOptionsAndArgs(self):
        '''Parse the options and args

        :return: a dictionary of option names and values, a sequence of args
        '''

        option_values = self._getOptions()
        args = self.args_ctrl
        return option_values, args


class UserCancelledError(Exception):
    """??"""
    pass


class Option(optparse.Option):
    """Extended optparse.Option class"""
    SUPER = optparse.Option
    TYPES = SUPER.TYPES + ('file', 'output', 'directory', 'group_name')
    ACTIONS = SUPER.ACTIONS + ('group_name',)
    TYPED_ACTIONS = SUPER.TYPED_ACTIONS + ('group_name',)
    # for required options
    ATTRS = optparse.Option.ATTRS + [STREQUIRED]

    def __init__(self, *opts, **attrs):
        if attrs.get(STREQUIRED, False):
            attrs['help'] = '(Required) ' + attrs.get('help', "")
        optparse.Option.__init__(self, *opts, **attrs)


class OptionParser(optparse.OptionParser):
    """Extended optparse.OptionParser to create the GUI for the module"""
    SUPER = optparse.OptionParser

    def __init__(self, *args, **kwargs):
        """Function to initialize the object"""
        if wx.GetApp() is None:
            self.app = wx.App(False)
        if 'option_class' not in kwargs:
            kwargs['option_class'] = Option
        self.SUPER.__init__(self, *args, **kwargs)

    def parse_args(self, args=None, values=None):
        '''This is the heart of it all overrides
        optparse.OptionParser.parse_args

        :param arg: is irrelevant and thus ignored, it's here only for
                    interface compatibility
        :param values: is irrelevant and thus ignored, it's here only for
                       interface compatibility
        '''
        # preprocess command line arguments and set to defaults
        option_values, args = self.SUPER.parse_args(self, args, values)
        self.list_of_option = self.option_list
        for group in self.option_groups:
            title = "--{n}".format(n=group.title.replace(" ", "_"))
            o = Option(title, type='group_name', dest=title, help=title,
                       metavar=title, action='group_name')
            self.list_of_option.append(o)
            for option in group.option_list:
                self.list_of_option.append(option)
        for option in self.list_of_option:
            if option.dest and hasattr(option_values, option.dest):
                default = getattr(option_values, option.dest)
                if default is not None:
                    option.default = default

        dlg = OptparseDialog(optParser=self,
                             title="{name} GUI".format(name=self.description))

        if args:
            dlg.args_ctrl.Value = ' '.join(args)

        dlg_result = dlg.ShowModal()
        if wx.ID_OK != dlg_result:
            sys.exit()

        if values is None:
            values = self.get_default_values()

        option_values, args = dlg.getOptionsAndArgs()

        for option, value in option_values.items():
            if option.required and value == "":
                self.error("The option %s is mandatory" % option)
            if ('store_true' == option.action) and (value is False):
                setattr(values, option.dest, False)
                continue
            if ('store_false' == option.action) and (value is True):
                setattr(values, option.dest, False)
                continue

            if option.takes_value() is False:
                value = None

            if isinstance(value, str):
                value = str(value)
            option.process(option, value, values, self)

        return values, args

    def error(self, msg):
        """Return an error message with wx.MessageDialog

           :param str msg: is the error string to pass to message dialog
        """
        wx.MessageDialog(None, msg, 'Error!', wx.ICON_ERROR).ShowModal()
        sys.exit()
