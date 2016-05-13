#!/usr/bin/python

from Tkinter import *
from xml.dom import minidom

import ttk

def sortby(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    """From: https://code.google.com/p/python-ttk/source/browse/trunk/pyttk-samples/treeview_multicolumn.py?r=21"""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # reorder data
    data.sort(reverse=descending)
    for indx, item in enumerate(data):
        tree.move(item[1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
        command=lambda col=col: sortby(tree, col, int(not descending)))

  
class IDMapper_frame_gui(Frame):
    
    def __init__(self, parent):
        """Initialize the application"""
        Frame.__init__(self, parent)
        self.parent = parent
        
        # Initialize all the wxPython components
        self.InitUI()
        
        # Set up the dictionary map
        self.IDMap = {}

        # Load the data
        self.LoadXML("candidates.xml")

     
    def InitUI(self):
        
        self.frame = Frame(self.parent)
        self.frame.grid(column=0, row=0, padx=0, pady=0, sticky=N+S+E+W)
 
        for i in range(0, 3):
            self.frame.columnconfigure(i, weight=6)
        self.frame.columnconfigure(3, weight=1)
        
        for i in range(3, 4):
            self.frame.rowconfigure(i, weight=1)

        self.labelID   = Label(self.frame, text=u'Identifier')
        self.labelName = Label(self.frame, text=u'Real Name')
        self.labelDoB  = Label(self.frame, text=u'Date of Birth')

        self.buttonAdd    = Button(self.frame, width=12,
                                   text=u'Add candidate',
                                   command=self.AddIdentifierEvent
                                  )
        self.buttonClear  = Button(self.frame, width=12,
                                   text=u'Clear fields',
                                   command=self.clear
                                  )
        self.buttonSearch = Button(self.frame, width=12,
                                   text=u'Search candidate',
                                   command=self.search
                                  )
        self.buttonEdit   = Button(self.frame, width=12,
                                   text=u'Edit candidate',
                                   command=self.edit
                                  )

        self.textCandId  = StringVar()
        self.candidateid = Entry(self.frame,
                                 textvariable=self.textCandId,
                                 width=20
                                )
        self.candidateid.focus_set()

        self.textCandName  = StringVar()
        self.candidatename = Entry(self.frame,
                                   textvariable=self.textCandName,
                                   width=20
                                  )

        self.textCandDoB  = StringVar()
        self.candidateDoB = Entry(self.frame,
                                  textvariable=self.textCandDoB,
                                  width=20
                                 )

        self.tableColumns = ("Identifier", "Real Name", "Date of Birth")
        self.datatable    = ttk.Treeview(self.frame,
                                         selectmode='browse',
                                         columns=self.tableColumns,
                                         show="headings")
        for col in self.tableColumns:
            self.datatable.heading(col, text=col.title(), 
                                   command=lambda c=col: sortby(self.datatable, c, 0))

        self.datatable.bind("<<TreeviewSelect>>", self.OnRowClick)
      
        self.ErrorMessage = StringVar()
        self.error = Label(self.frame, textvariable=self.ErrorMessage, fg='red')

        self.labelID.grid(row=0, column=0, padx=(0,4), sticky=E+W)
        self.labelName.grid(row=0, column=1, padx=(4,4), sticky=E+W)
        self.labelDoB.grid(row=0, column=2, padx=(4,4), sticky=E+W)

        self.candidateid.grid(row=1, column=0, padx=(0,4), pady=(0,10), sticky=E+W)
        self.candidatename.grid(row=1, column=1, padx=(4,4), pady=(0,10), sticky=E+W)
        self.candidateDoB.grid(row=1, column=2, padx=(4,4), pady=(0,10), sticky=E+W)
 
        self.buttonAdd.grid(row=2, column=1, padx=(4,0), sticky=E+W)
        self.buttonClear.grid(row=1, column=3, padx=(4,0), sticky=E+W)
        self.buttonSearch.grid(row=2, column=0, padx=(4,0), sticky=E+W)
        self.buttonEdit.grid(row=2, column=2, padx=(4,0), sticky=E+W)

        self.datatable.grid(row=3, column=0, columnspan=3, pady=10, sticky='nsew')
        self.error.grid(row=3, column=3)


    def LoadXML(self, file):
        global xmlitemlist
        global xmldoc
        
        """Parses the XML file and loads the data into the current window"""
        try:
            xmldoc   = minidom.parse(file)
            xmlitemlist = xmldoc.getElementsByTagName('Candidate')
            for s in xmlitemlist:
                identifier = s.getElementsByTagName("Identifier")[0].firstChild.nodeValue
                realname = s.getElementsByTagName("RealName")[0].firstChild.nodeValue
                dob = s.getElementsByTagName("DateOfBirth")[0].firstChild.nodeValue
                self.AddIdentifierAction(identifier, realname, dob, False)
        except:
            pass


    def SaveMapAction(self):
        
        """Function which performs the action of writing the XML file"""
        f = open("candidates.xml", "w")
        f.write("<?xml version=\"1.0\"?>\n<data>\n")
        for key in self.IDMap:
            f.write("\t<Candidate>\n")
            f.write("\t\t<Identifier>%s</Identifier>\n" % key)
            f.write("\t\t<RealName>%s</RealName>\n" % self.IDMap[key][1])
            f.write("\t\t<DateOfBirth>%s</DateOfBirth>\n" % self.IDMap[key][2])
            f.write("\t</Candidate>\n")
        f.write("</data>")


    def SaveMapEvent(self, event):
        """Handles any wxPython event which should trigger a save action"""
        self.SaveMapAction()


    def AddIdentifierEvent(self):
        
        name = self.candidatename.get()
        candid = self.candidateid.get()
        dob = self.candidateDoB.get()
        self.AddIdentifierAction(candid, name, dob)


    def AddIdentifierAction(self, candid, realname, dob, save=True):
        """
        Adds the given identifier and real name to the mapping. If
        the "save" parameter is true, this also triggers the saving
        of the XML file. 
        This is set to False on initial load.
        """
        self.ErrorMessage.set("")
        if candid in self.IDMap:
            self.ErrorMessage.set("ERROR: Candidate\nID key already exists")
            return

        mapList = [candid, realname, dob]
        self.IDMap[candid] = mapList
                        
        insertedList = [(candid, realname, dob)]
        for item in insertedList:
            self.datatable.insert('', 'end', values=item)
        
        if(save):
            self.SaveMapAction()


    def OnRowClick(self, event):
        
        """Update the text boxes' data on row click"""
        item_id = str(self.datatable.focus())
        item = self.datatable.item(item_id)['values']
        
        self.textCandId.set(item[0])
        self.textCandName.set(item[1])
        self.textCandDoB.set(item[2])


    def clear(self):
        
        self.textCandId.set("")
        self.textCandName.set("")
        self.textCandDoB.set("")
        self.candidateid.focus_set()


    def search(self):
        #  Find a candidate based on its ID if it is set in text box
        if self.textCandId.get():
            (candid, name, dob) = self.FindCandidate("candid",
                                                     self.textCandId.get()
                                                    )
        # or based on its name if it is set in text box
        elif self.textCandName.get():
            (candid, name, dob) = self.FindCandidate("name",
                                                     self.textCandName.get()
                                                    )
        # print the values in the text box
        self.textCandId.set(candid)
        self.textCandName.set(name)
        self.textCandDoB.set(dob)


    def FindCandidate(self, key, value):
        # Loop through the candidate tree and return the candid, name and dob
        # that matches a given value
        for s in xmlitemlist:
            candid = s.getElementsByTagName("Identifier")[0].firstChild.nodeValue
            name = s.getElementsByTagName("RealName")[0].firstChild.nodeValue
            dob = s.getElementsByTagName("DateOfBirth")[0].firstChild.nodeValue
            if (key == "candid" and value == candid):
                return (candid, name, dob)
            elif (key == "name" and value == name):
                return (candid, name, dob)
            elif (key == "dob" and value == dob):
                return (candid, name, dob)
            else:
                continue
        # if candidate was not found, return empty strings
        return ("", "", "")


    def edit(self):
        self.EditIdentifierAction(self.textCandId.get(),
                                  self.textCandName.get(),
                                  self.textCandDoB.get()
                                 )

    def EditIdentifierAction(self, identifier, realname, realdob, edit=True):
        # Loop through the candidate tree, find a candidate based on its ID
        # and check if name or DoB needs to be updated
        for s in xmlitemlist:
            candid = s.getElementsByTagName("Identifier")[0].firstChild.nodeValue
            name = s.getElementsByTagName("RealName")[0].firstChild.nodeValue
            dob = s.getElementsByTagName("DateOfBirth")[0].firstChild.nodeValue

            # if name of candidate is changed
            if (candid == identifier) and not (realname == name):
                # update in the XML file
                s.getElementsByTagName("RealName")[0].firstChild.nodeValue = realname
                f = open("candidates.xml", "w")
                xmldoc.writexml(f)

                # update IDMap dictionary
                mapList = [candid, realname, dob]
                self.IDMap[candid] = mapList

                insertedList = [(candid, realname, dob)]
                print self.datatable.__dict__
                for item in insertedList:
                    #self.datatable.delete([candid, name, dob])
                    self.datatable.insert('', 'end', values=item)
                    print self.datatable



            # if candidate's date of birth is changed
            if (candid == identifier) and not (realdob == dob):
                # update in the XML file
                s.getElementsByTagName("DateOfBirth")[0].firstChild.nodeValue = realdob
                f = open("candidates.xml", "w")
                xmldoc.writexml(f)




def main():
       
    root = Tk()
    app = IDMapper_frame_gui(root)
    root.mainloop()
 

if __name__ == "__main__":
    main()
