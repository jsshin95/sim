import tkinter as tk
from tkinter import messagebox
import pandas as pd
import tkinter.ttk
import os
from datetime import datetime
import PIL
from PIL import Image, ImageGrab, ImageTk
from tkinter import filedialog
import csv
import math

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        """
        def OnMouseWheel(event):
            s=-0.01
            canvas.yview("scroll",round(s*event.delta),"units")
        """
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        #canvas.bind("<MouseWheel>", OnMouseWheel)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class Model:
    def __init__(self):
        self.type='' #unit | 1block | 2block | meshed
        self.n=0
        self.x=0.0
        self.y=0.0
        self.a=0.0
        self.b=0.0
        self.c=0.0
        self.gravity=0
        self.row=0
        self.col=0
        self.folder=''
        self.project=''
        self.step=[]
    def Init(self):
        self.type='' #unit | 1block | 2block | meshed
        self.n=0
        self.x=0.0
        self.y=0.0
        self.a=0.0
        self.b=0.0
        self.c=0.0
        self.gravity=0
        self.row=0
        self.col=0
        self.folder=''
        self.project=''
        del self.step[0:]

class Layer:
    def __init__(self, material='', thickness=0.0, modulus=0.0, cte=0.0, poisson=0.0, density=0.0, fill='', row=0, col=0, modulus2=0.0,cte2=0.0,Tg=0):
        self.material=material # SR | Cu | PPG
        self.thickness=thickness
        self.modulus=modulus
        self.cte=cte
        self.poisson=poisson
        self.density=density
        self.fill=fill #Cu
        self.modulus2=modulus2
        self.cte2=cte2
        self.Tg=Tg
        if (row>0)&(col>0):
            self.section= [[Part() for _ in range(col)] for _ in range(row)] #meshed
        else:
            self.unit=Part() #unit,1block,2block
            self.dummy=Part() #1block,2block

class Part:
    def __init__(self):
        self.portion=0.0
        self.modulus=0.0
        self.cte=0.0
        self.poisson=0.0
        self.density=0.0
        self.modulus2=0.0
        self.cte2=0.0
        self.Elastic=[] # [Modulus, Poisson, Temp.]
        self.Expansion=[] # [CTE, Temp.]

class LayerSQBC:
    def __init__(self, thickness=0.0, portion=0.0, modulus=0.0, cte=0.0, distance=0.0, color='', fill=''):
        self.thickness=thickness
        self.portion=portion
        self.modulus=modulus
        self.cte=cte
        self.distance=distance
        self.color=color
        self.fill=fill

    def Etd(self):
        return self.modulus * self.thickness * self.distance
    
    def Et(self):
        return self.modulus * self.thickness
    
    def AEt(self):
        return self.cte * self.modulus * self.thickness

def Init():
    os.chdir(cwd)
    model.Init()

    entry_nLayer.delete(0, tk.END)
    entry_x.delete(0, tk.END)
    entry_y.delete(0, tk.END)
    entry_a.delete(0, tk.END)
    entry_b.delete(0, tk.END)
    entry_c.delete(0, tk.END)
    entry_row.delete(0, tk.END)
    entry_col.delete(0, tk.END)
    entry_folder.delete(0, tk.END)
    check_gravity.deselect()
    cb_customer.set('')
    entry_modelname.delete(0, tk.END)
    cb_structure.set('')

    label_img_unit.place_forget()
    label_img_1block.place_forget()
    label_img_2block.place_forget()
    label_img_meshed.place_forget()
    label_a.place_forget()
    entry_a.place_forget()
    label_b.place_forget()
    entry_b.place_forget()
    label_c.place_forget()
    entry_c.place_forget()
    label_row.place_forget()
    entry_row.place_forget()
    label_col.place_forget()
    entry_col.place_forget()
    label_folder.place_forget()
    entry_folder.place_forget()
    check_gravity.place_forget()

    label_No.place_forget()
    label_Layer.place_forget()
    label_Thickness.place_forget()
    label_Modulus.place_forget()
    label_CTE.place_forget()
    label_Poisson.place_forget()
    label_Density.place_forget()
    label_Fill.place_forget()
    label_Portion_unit.place_forget()       #col 8 (Cu, SR) - unit, 1block, 2block
    label_Portion_dummy.place_forget()      #col 9 (Cu,SR) - 1block, 2block

    #output
    label_Modulus_unit.place_forget()       #col 10 - unit, 1block, 2block
    label_CTE_unit.place_forget()           #col 11
    label_Poisson_unit.place_forget()       #col 12
    label_Density_unit.place_forget()       #col 13
    label_Modulus_dummy.place_forget()      #col 14 - 1block, 2block
    label_CTE_dummy.place_forget()          #col 15
    label_Poisson_dummy.place_forget()      #col 16
    label_Density_dummy.place_forget()      #col 17

    if len(list_No)>0:
        for i in range(len(list_No)):
            list_No[i].grid_forget()
    del list_No[0:]

    if len(list_Layer)>0:
        for i in range(len(list_Layer)):
            list_Layer[i].grid_forget()
    del list_Layer[0:]

    if len(list_Thickness)>0:
        for i in range(len(list_Thickness)):
            list_Thickness[i].grid_forget()
    del list_Thickness[0:]

    if len(list_Modulus)>0:
        for i in range(len(list_Modulus)):
            list_Modulus[i].grid_forget()
    del list_Modulus[0:]

    if len(list_CTE)>0:
        for i in range(len(list_CTE)):
            list_CTE[i].grid_forget()
    del list_CTE[0:]

    if len(list_Poisson)>0:
        for i in range(len(list_Poisson)):
            list_Poisson[i].grid_forget()
    del list_Poisson[0:]

    if len(list_Density)>0:
        for i in range(len(list_Density)):
            list_Density[i].grid_forget()
    del list_Density[0:]

    if len(list_Fill)>0:
        for i in range(len(list_Fill)):
            list_Fill[i].grid_forget()
    del list_Fill[0:]

    if len(list_Portion_unit)>0:
        for i in range(len(list_Portion_unit)):
            list_Portion_unit[i].grid_forget()
    del list_Portion_unit[0:]

    if len(list_Portion_dummy)>0:
        for i in range(len(list_Portion_dummy)):
            list_Portion_dummy[i].grid_forget()
    del list_Portion_dummy[0:]

    if len(list_Modulus_unit)>0:
        for i in range(len(list_Modulus_unit)):
            list_Modulus_unit[i].grid_forget()
    del list_Modulus_unit[0:]

    if len(list_CTE_unit)>0:
        for i in range(len(list_CTE_unit)):
            list_CTE_unit[i].grid_forget()
    del list_CTE_unit[0:]

    if len(list_Poisson_unit)>0:
        for i in range(len(list_Poisson_unit)):
            list_Poisson_unit[i].grid_forget()
    del list_Poisson_unit[0:]

    if len(list_Density_unit)>0:
        for i in range(len(list_Density_unit)):
            list_Density_unit[i].grid_forget()
    del list_Density_unit[0:]

    if len(list_Modulus_dummy)>0:
        for i in range(len(list_Modulus_dummy)):
            list_Modulus_dummy[i].grid_forget()
    del list_Modulus_dummy[0:]

    if len(list_CTE_dummy)>0:
        for i in range(len(list_CTE_dummy)):
            list_CTE_dummy[i].grid_forget()
    del list_CTE_dummy[0:]

    if len(list_Poisson_dummy)>0:
        for i in range(len(list_Poisson_dummy)):
            list_Poisson_dummy[i].grid_forget()
    del list_Poisson_dummy[0:]

    if len(list_Density_dummy)>0:
        for i in range(len(list_Density_dummy)):
            list_Density_dummy[i].grid_forget()
    del list_Density_dummy[0:]

    if len(L)>0: del L[0:]
    if len(Ls)>0: del Ls[0:]

    label_nLayer.place_forget()
    entry_nLayer.place_forget()
    label_x.place_forget()
    entry_x.place_forget()
    label_y.place_forget()
    entry_y.place_forget()

    label_customer.place_forget()
    cb_customer.place_forget()

    label_modelname.place_forget()
    entry_modelname.place_forget()

    label_structure.place_forget()
    cb_structure.place_forget()
    
    button_enter.place_forget()
    button_calc.place_forget()
    button_save_input.place_forget()
    button_load_input.place_forget()

    entry_project.delete(0,tk.END)
    label_result_SQBC.config(text='')
    label_result_warpage.config(text='')
    label_result_CTE.config(text='')
    label_result_modulus.config(text='')

    check_SQBC.deselect()
    check_warpage.deselect()
    check_CTE.deselect()
    check_modulus.deselect()
    check_cpu.deselect()
    check_gui.select()
    check_job.select()

    label_project.place_forget()
    entry_project.place_forget()
    button_SQBC.place_forget()
    button_warpage.place_forget()
    button_CTE.place_forget()
    button_modulus.place_forget()
    label_modeling.place_forget()
    button_shell.place_forget()
    button_solid.place_forget()

    label_result_SQBC.place_forget()
    label_result_warpage.place_forget()
    label_result_CTE.place_forget()
    label_result_modulus.place_forget()

    button_result_SQBC.place_forget()
    button_result_warpage.place_forget()
    button_result_CTE.place_forget()
    button_result_modulus.place_forget()

    check_SQBC.place_forget()
    check_warpage.place_forget()
    check_CTE.place_forget()
    check_modulus.place_forget()
    check_cpu.place_forget()
    check_gui.place_forget()
    check_job.place_forget()


def selectmodel(event):
    Init()
    if cb_model.get()=="unit":
        label_img_unit.place(x=170, y=5, width=300, height=180)
    elif cb_model.get()=="1block":
        label_img_1block.place(x=170, y=5, width=300, height=180)
        label_a.place(x=15, y=130, width=50, height=20)
        entry_a.place(x=65, y=130, width=80, height=20)
        label_b.place(x=15, y=155, width=50, height=20)
        entry_b.place(x=65, y=155, width=80, height=20)
        check_gravity.place(x=30, y=180, width=70, height=20)
    elif cb_model.get()=='2block':
        label_img_2block.place(x=170, y=5, width=300, height=180)
        label_a.place(x=15, y=130, width=50, height=20)
        entry_a.place(x=65, y=130, width=80, height=20)
        label_b.place(x=15, y=155, width=50, height=20)
        entry_b.place(x=65, y=155, width=80, height=20)
        label_c.place(x=15, y=180, width=50, height=20)
        entry_c.place(x=65, y=180, width=80, height=20)
        check_gravity.place(x=30, y=205, width=70, height=20)
    elif cb_model.get()=='meshed':
        label_img_meshed.place(x=170, y=5, width=300, height=180)
        entry_row.insert(0,'30')
        entry_col.insert(0,'30')
        label_row.place(x=15, y=130, width=50, height=20)
        entry_row.place(x=65, y=130, width=80, height=20)
        label_col.place(x=15, y=155, width=50, height=20)
        entry_col.place(x=65, y=155, width=80, height=20)
        label_folder.place(x=15, y=180, width=50, height=20)
        entry_folder.place(x=65, y=180, width=80, height=20)
        entry_folder.insert(0,'folder name')
    
    label_nLayer.place(x=15, y=55, width=50, height=20)
    entry_nLayer.place(x=65, y=55, width=80, height=20)
    label_x.place(x=15, y=80, width=50, height=20)
    entry_x.place(x=65, y=80, width=80, height=20)
    label_y.place(x=15, y=105, width=50, height=20)
    entry_y.place(x=65, y=105, width=80, height=20)

    label_customer.place(x=15, y=230, width=50, height=20)
    cb_customer.place(x=65, y=230, width=80, height=20)
    label_modelname.place(x=15, y=255, width=50, height=20)
    entry_modelname.place(x=65, y=255, width=80, height=20)
    label_structure.place(x=15, y=280, width=50, height=20)
    cb_structure.place(x=65, y=280, width=80, height=20)
    
    button_enter.place(x=35, y=320, width=70, height=30)

def btnMClick(x,y): # x : Layer No.,  y : Material type
    def yview(*args):
        """ scroll listboxes together """
        lbNumber.yview(*args)
        lbMaterial.yview(*args)
        lbSupplier.yview(*args)
        lbDescription.yview(*args)
        lbItemCode.yview(*args)
        lbThickness.yview(*args)
        lbModulus.yview(*args)
        lbCTE.yview(*args)
        lbPoisson.yview(*args)
        lbDensity.yview(*args)
    def OnMouseWheel(event):
        s=-0.1
        lbNumber.yview("scroll",round(s*event.delta),"units")
        lbMaterial.yview("scroll",round(s*event.delta),"units")
        lbSupplier.yview("scroll",round(s*event.delta),"units")
        lbDescription.yview("scroll",round(s*event.delta),"units")
        lbItemCode.yview("scroll",round(s*event.delta),"units")
        lbThickness.yview("scroll",round(s*event.delta),"units")
        lbModulus.yview("scroll",round(s*event.delta),"units")
        lbCTE.yview("scroll",round(s*event.delta),"units")
        lbPoisson.yview("scroll",round(s*event.delta),"units")
        lbDensity.yview("scroll",round(s*event.delta),"units")
        return "break"
    def OnSelect(event):
        widget=event.widget
        index=int(widget.curselection()[0])
        #label_no.config(text=f"{index}")
        lbNumber.select_clear(0,tk.END)
        lbMaterial.select_clear(0,tk.END)
        lbSupplier.select_clear(0,tk.END)
        lbDescription.select_clear(0,tk.END)
        lbItemCode.select_clear(0,tk.END)
        lbThickness.select_clear(0,tk.END)
        lbModulus.select_clear(0,tk.END)
        lbCTE.select_clear(0,tk.END)
        lbPoisson.select_clear(0,tk.END)
        lbDensity.select_clear(0,tk.END)
        lbNumber.selection_set(index)
        lbMaterial.selection_set(index)
        lbSupplier.selection_set(index)
        lbDescription.selection_set(index)
        lbItemCode.selection_set(index)
        lbThickness.selection_set(index)
        lbModulus.selection_set(index)
        lbCTE.selection_set(index)
        lbPoisson.selection_set(index)
        lbDensity.selection_set(index)
    def btnsearchClick():
        
        if entry_des.get()=="":
            #messagebox.showwarning(title="err",message="검색할 키워드를 입력해주세요")
            return
        
        lbNumber.delete(0,tk.END)
        lbMaterial.delete(0,tk.END)
        lbSupplier.delete(0,tk.END)
        lbDescription.delete(0,tk.END)
        lbItemCode.delete(0,tk.END)
        lbThickness.delete(0,tk.END)
        lbModulus.delete(0,tk.END)
        lbCTE.delete(0,tk.END)
        lbPoisson.delete(0,tk.END)
        lbDensity.delete(0,tk.END)
        for i in range(df.shape[0]):
            if (df.iloc[i].values[0]==y)&((entry_des.get().upper() in df.iloc[i].values[1])|(entry_des.get().upper() in df.iloc[i].values[2])|(entry_des.get().upper() in str(df.iloc[i].values[3]))):
                lbNumber.insert(i,i)
                lbMaterial.insert(i,df.iloc[i].values[0])
                lbSupplier.insert(i,df.iloc[i].values[1])
                lbDescription.insert(i,df.iloc[i].values[2])
                lbItemCode.insert(i,df.iloc[i].values[3])
                lbThickness.insert(i,df.iloc[i].values[4])
                lbModulus.insert(i,round(df.iloc[i].values[7]*1000))
                lbCTE.insert(i,df.iloc[i].values[5])
                lbPoisson.insert(i,df.iloc[i].values[11])
                lbDensity.insert(i,df.iloc[i].values[10])
                
    def btninitClick():
        entry_des.delete(0,tk.END)

        lbNumber.delete(0,tk.END)
        lbMaterial.delete(0,tk.END)
        lbSupplier.delete(0,tk.END)
        lbDescription.delete(0,tk.END)
        lbItemCode.delete(0,tk.END)
        lbThickness.delete(0,tk.END)
        lbModulus.delete(0,tk.END)
        lbCTE.delete(0,tk.END)
        lbPoisson.delete(0,tk.END)
        lbDensity.delete(0,tk.END)

        for i in range(df.shape[0]):
            if df.iloc[i].values[0]==y:
                lbNumber.insert(i,i)
                lbMaterial.insert(i,df.iloc[i].values[0])
                lbSupplier.insert(i,df.iloc[i].values[1])
                lbDescription.insert(i,df.iloc[i].values[2])
                lbItemCode.insert(i,df.iloc[i].values[3])
                lbThickness.insert(i,df.iloc[i].values[4])
                lbModulus.insert(i,round(df.iloc[i].values[7]*1000))
                lbCTE.insert(i,df.iloc[i].values[5])
                lbPoisson.insert(i,df.iloc[i].values[11])
                lbDensity.insert(i,df.iloc[i].values[10])

    def btnapplyClick(event):

        index=int(lbNumber.get(lbNumber.curselection()[0]))

        list_Modulus[x].delete(0,tk.END)
        list_CTE[x].delete(0,tk.END)
        list_Poisson[x].delete(0,tk.END)
        list_Density[x].delete(0,tk.END)

        list_No[x].config(text=str(index))
        list_Modulus[x].insert(0,round(df.iloc[index].values[7]*1000))
        list_CTE[x].insert(0,df.iloc[index].values[5])
        list_Poisson[x].insert(0,df.iloc[index].values[11])
        list_Density[x].insert(0,df.iloc[index].values[10])
        
        winDB.destroy()
    
    def Key_input(event):
        if event.keycode==13: #enter키 입력
            btnsearchClick()

    winDB=tk.Toplevel(win)
    winDB.title("Material properties ("+list_Layer[x]['text']+')')
    winDB.geometry("1000x720+250+50")
    #winDB.attributes('-topmost','true')
    winDB.bind("<Key>",Key_input)
    
    label_no=tk.Label(winDB,text="No.")
    label_no.place(x=5,y=55,width=40,height=20)
    
    label_mat=tk.Label(winDB, text="Material")
    label_mat.place(x=50,y=55,width=70,height=20)

    label_sup=tk.Label(winDB,text="Supplier")
    label_sup.place(x=125,y=55,width=80,height=20)

    label_des=tk.Label(winDB,text="Description")
    label_des.place(x=220,y=55,width=170,height=20)

    label_itc=tk.Label(winDB,text="Item Code")
    label_itc.place(x=395,y=55,width=90,height=20)

    label_thk=tk.Label(winDB,text="Thickness")
    label_thk.place(x=490,y=55,width=70,height=20)

    label_mod=tk.Label(winDB,text="Modulus")
    label_mod.place(x=562,y=55,width=70,height=20)

    label_cte=tk.Label(winDB,text="CTE")
    label_cte.place(x=634,y=55,width=70,height=20)

    label_poi=tk.Label(winDB,text="Poisson")
    label_poi.place(x=706,y=55,width=70,height=20)

    label_den=tk.Label(winDB,text="Density")
    label_den.place(x=778,y=55,width=70,height=20)

    label_keyword=tk.Label(winDB,text="검색할 키워드 (supplier, description, item code) : ")
    label_keyword.place(x=25,y=25,width=280,height=20)

    entry_des=tk.Entry(winDB)
    entry_des.place(x=310,y=25,width=170,height=20)

    buttonsearch=tk.Button(winDB,text="검색",command=btnsearchClick)
    buttonsearch.place(x=490,y=25,width=50,height=20)

    buttoninit=tk.Button(winDB,text="초기화",command=btninitClick)
    buttoninit.place(x=560,y=25,width=50,height=20)

    #buttonapply=tk.Button(winDB,text="적용",command=btnapplyClick)
    #buttonapply.place(x=905,y=20,width=60,height=30)

    frame=tk.Frame(winDB)
    frame.place(x=5,y=80,width=900,height=600)

    scrollbar=tk.Scrollbar(frame)

    lbNumber=tk.Listbox(frame,width=1,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbMaterial=tk.Listbox(frame,width=5,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbSupplier=tk.Listbox(frame,width=8,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbDescription=tk.Listbox(frame,width=20,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbItemCode=tk.Listbox(frame,width=8,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbThickness=tk.Listbox(frame,width=5,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbModulus=tk.Listbox(frame,width=5,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbCTE=tk.Listbox(frame,width=5,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbPoisson=tk.Listbox(frame,width=5,height=0, yscrollcommand=scrollbar.set, exportselection=False)
    lbDensity=tk.Listbox(frame,width=5,height=0, yscrollcommand=scrollbar.set, exportselection=False)

    lbNumber.bind("<MouseWheel>", OnMouseWheel)
    lbMaterial.bind("<MouseWheel>", OnMouseWheel)
    lbSupplier.bind("<MouseWheel>", OnMouseWheel)
    lbDescription.bind("<MouseWheel>", OnMouseWheel)
    lbItemCode.bind("<MouseWheel>", OnMouseWheel)
    lbThickness.bind("<MouseWheel>", OnMouseWheel)
    lbModulus.bind("<MouseWheel>", OnMouseWheel)
    lbCTE.bind("<MouseWheel>", OnMouseWheel)
    lbPoisson.bind("<MouseWheel>", OnMouseWheel)
    lbDensity.bind("<MouseWheel>", OnMouseWheel)

    lbNumber.bind("<<ListboxSelect>>", OnSelect)
    lbMaterial.bind("<<ListboxSelect>>", OnSelect)
    lbSupplier.bind("<<ListboxSelect>>", OnSelect)
    lbDescription.bind("<<ListboxSelect>>", OnSelect)
    lbItemCode.bind("<<ListboxSelect>>", OnSelect)
    lbThickness.bind("<<ListboxSelect>>", OnSelect)
    lbModulus.bind("<<ListboxSelect>>", OnSelect)
    lbCTE.bind("<<ListboxSelect>>", OnSelect)
    lbPoisson.bind("<<ListboxSelect>>", OnSelect)
    lbDensity.bind("<<ListboxSelect>>", OnSelect)

    lbNumber.bind("<Double-Button-1>", btnapplyClick)
    lbMaterial.bind("<Double-Button-1>", btnapplyClick)
    lbSupplier.bind("<Double-Button-1>", btnapplyClick)
    lbDescription.bind("<Double-Button-1>", btnapplyClick)
    lbItemCode.bind("<Double-Button-1>", btnapplyClick)
    lbThickness.bind("<Double-Button-1>", btnapplyClick)
    lbModulus.bind("<Double-Button-1>", btnapplyClick)
    lbCTE.bind("<Double-Button-1>", btnapplyClick)
    lbPoisson.bind("<Double-Button-1>", btnapplyClick)
    lbDensity.bind("<Double-Button-1>", btnapplyClick)

    for i in range(df.shape[0]):
        if df.iloc[i].values[0]==y:
            lbNumber.insert(i,i)
            lbMaterial.insert(i,df.iloc[i].values[0])
            lbSupplier.insert(i,df.iloc[i].values[1])
            lbDescription.insert(i,df.iloc[i].values[2])
            lbItemCode.insert(i,df.iloc[i].values[3])
            lbThickness.insert(i,df.iloc[i].values[4])
            lbModulus.insert(i,round(df.iloc[i].values[7]*1000))
            lbCTE.insert(i,df.iloc[i].values[5])
            lbPoisson.insert(i,df.iloc[i].values[11])
            lbDensity.insert(i,df.iloc[i].values[10])

        elif df.iloc[i].values[0]==y:
            lbNumber.insert(i,i)
            lbMaterial.insert(i,df.iloc[i].values[0])
            lbSupplier.insert(i,df.iloc[i].values[1])
            lbDescription.insert(i,df.iloc[i].values[2])
            lbItemCode.insert(i,df.iloc[i].values[3])
            lbThickness.insert(i,df.iloc[i].values[4])
            lbModulus.insert(i,round(df.iloc[i].values[7]*1000))
            lbCTE.insert(i,df.iloc[i].values[5])
            lbPoisson.insert(i,df.iloc[i].values[11])
            lbDensity.insert(i,df.iloc[i].values[10])

        elif df.iloc[i].values[0]==y:
            lbNumber.insert(i,i)
            lbMaterial.insert(i,df.iloc[i].values[0])
            lbSupplier.insert(i,df.iloc[i].values[1])
            lbDescription.insert(i,df.iloc[i].values[2])
            lbItemCode.insert(i,df.iloc[i].values[3])
            lbThickness.insert(i,df.iloc[i].values[4])
            lbModulus.insert(i,round(df.iloc[i].values[7]*1000))
            lbCTE.insert(i,df.iloc[i].values[5])
            lbPoisson.insert(i,df.iloc[i].values[11])
            lbDensity.insert(i,df.iloc[i].values[10])


    scrollbar.config(command=yview)

    lbNumber.pack(side="left", fill="both", expand=1)
    lbMaterial.pack(side="left", fill="both", expand=1)
    lbSupplier.pack(side="left", fill="both", expand=1)
    lbDescription.pack(side="left", fill="both", expand=1)
    lbItemCode.pack(side="left", fill="both", expand=1)
    lbThickness.pack(side="left", fill="both", expand=1)
    lbModulus.pack(side="left", fill="both", expand=1)
    lbCTE.pack(side="left", fill="both", expand=1)
    lbPoisson.pack(side="left", fill="both", expand=1)
    lbDensity.pack(side="left", fill="both", expand=1)
    scrollbar.pack(side="right", fill="y", expand=1)

    return

def btnEnterClick():
    if (entry_nLayer.get()=='')|(entry_x.get()=='')|(entry_y.get()==''):
        messagebox.showwarning(title="error",message="층 수, x, y 입력")
        return
    if (cb_customer.get()=='')|(cb_structure.get()==''):
        messagebox.showwarning(title="error",message="고객사, 구조 선택")
        return
    if entry_modelname.get()=='':
        messagebox.showwarning(title="error",message="모델명 입력")
        return
    try:
        if int(entry_nLayer.get())<2:
            messagebox.showwarning(title="error",message="층 수 : 2 이상의 자연수")
            return
    except:
        messagebox.showwarning(title="error",message="층 수")
        return
    try:
        if float(entry_x.get())<=0:
            messagebox.showwarning(title="error",message="x>0")
            return
    except:
        messagebox.showwarning(title="error",message="x")
        return
    try:
        if float(entry_y.get())<=0:
            messagebox.showwarning(title="error",message="y>0")
            return
    except:
        messagebox.showwarning(title="error",message="y")
        return
    
    if int(entry_nLayer.get())==2:
        if (cb_structure.get()=='Coreless_non')|(cb_structure.get()=='Coreless_rev'):
            messagebox.showwarning(title="error",message="structure error (2L : Cored, ETS)")
            return
    elif int(entry_nLayer.get())%2==1:
        if (cb_structure.get()=='Cored'):
            messagebox.showwarning(title="error",message="structure error (odd number of layers can't be cored)")
            return
    
    if cb_model.get()=='unit':
        model.type='unit'
        model.n=int(entry_nLayer.get())
        model.x=float(entry_x.get())
        model.y=float(entry_y.get())
        model.a=0.0
        model.b=0.0
        model.c=0.0
        model.gravity=0
        model.row=0
        model.col=0
        model.folder=''
        model.project=''

    elif cb_model.get()=="1block":
        if (entry_a.get()=='')|(entry_b.get()==''):
            messagebox.showwarning(title="error",message="a, b 입력")
            return
        try:
            if (float(entry_a.get())<=0)|(float(entry_a.get())>=(float(entry_y.get())/2)):
                messagebox.showwarning(title="error",message="0<a<(y/2)")
                return
        except:
            messagebox.showwarning(title="error",message="a")
            return
        try:
            if (float(entry_b.get())<=0)|(float(entry_b.get())>=(float(entry_x.get())/2)):
                messagebox.showwarning(title="error",message="0<b<(x/2)")
                return
        except:
            messagebox.showwarning(title="error",message="b")
            return
        model.type='1block'
        model.n=int(entry_nLayer.get())
        model.x=float(entry_x.get())
        model.y=float(entry_y.get())
        model.a=float(entry_a.get())
        model.b=float(entry_b.get())
        model.gravity=CheckG.get()

        model.c=0.0
        model.row=0
        model.col=0
        model.folder=''
        model.project=''

    elif cb_model.get()=="2block":
        if (entry_a.get()=='')|(entry_b.get()=='')|(entry_c.get()==''):
            messagebox.showwarning(title="error",message="a, b, c 입력")
            return
        try:
            if (float(entry_a.get())<=0)|(float(entry_a.get())>=(float(entry_y.get())/2)):
                messagebox.showwarning(title="error",message="0<a<(y/2)")
                return
        except:
            messagebox.showwarning(title="error",message="a")
            return
        try:
            if float(entry_b.get())<=0:
                messagebox.showwarning(title="error",message="b>0")
                return
        except:
            messagebox.showwarning(title="error",message="b")
            return
        try:
            if float(entry_c.get())<=0:
                messagebox.showwarning(title="error",message="c>0")
                return
        except:
            messagebox.showwarning(title="error",message="c")
            return
        if (2*float(entry_b.get())+float(entry_c.get()))>=float(entry_x.get()):
            messagebox.showwarning(title="error",message="(2b+c)<x")
            return
        model.type='2block'
        model.n=int(entry_nLayer.get())
        model.x=float(entry_x.get())
        model.y=float(entry_y.get())
        model.a=float(entry_a.get())
        model.b=float(entry_b.get())
        model.c=float(entry_c.get())
        model.gravity=CheckG.get()

        model.row=0
        model.col=0
        model.folder=''
        model.project=''

    elif cb_model.get()=="meshed":
        if (entry_row.get()=='')|(entry_col.get()=='')|(entry_folder.get()==''):
            messagebox.showwarning(title="error",message="row, col, folder명 입력")
            return
        try:
            if int(entry_row.get())<1:
                messagebox.showwarning(title="error",message="row는 1 이상의 자연수")
                return
        except:
            messagebox.showwarning(title="error",message="row")
            return
        try:
            if float(entry_col.get())<1:
                messagebox.showwarning(title="error",message="col은 1 이상의 자연수")
                return
        except:
            messagebox.showwarning(title="error",message="col")
            return
        model.type='meshed'
        model.n=int(entry_nLayer.get())
        model.x=float(entry_x.get())
        model.y=float(entry_y.get())
        model.row=int(entry_row.get())
        model.col=int(entry_col.get())
        model.folder=cwd+'/'+entry_folder.get()

        model.a=0.0
        model.b=0.0
        model.c=0.0
        model.gravity=0
        model.project=''
    
    label_No.place(x=170,y=200,width=30,height=40)
    label_Layer.place(x=200,y=200,width=47,height=40)
    label_Thickness.place(x=247,y=200,width=47,height=35)
    label_Modulus.place(x=294,y=200,width=47,height=35)
    label_CTE.place(x=341,y=200,width=47,height=35)
    label_Poisson.place(x=388,y=200,width=47,height=35)
    label_Density.place(x=435,y=200,width=47,height=35)
    label_Fill.place(x=482,y=200,width=47,height=35)
    label_Portion_unit.place_forget()
    label_Portion_dummy.place_forget()

    if len(list_No)>0:
        for i in range(len(list_No)):
            list_No[i].grid_forget()
    del list_No[0:]
    for i in range(2*model.n+1):
        list_No.append(tk.Label(frame.scrollable_frame, text='', width=3)) #button으로 수정
        list_No[i].grid(row=i, column=0)
    
    if len(list_Layer)>0:
        for i in range(len(list_Layer)):
            list_Layer[i].grid_forget()
    del list_Layer[0:]
    list_Layer.append(tk.Button(frame.scrollable_frame, text="SR_top", command=lambda x=0, y='SR':btnMClick(x,y), width=6))
    list_Layer[0].grid(row=0, column=1)

    for i in range(model.n-1):
        list_Layer.append(tk.Button(frame.scrollable_frame, text="L"+str(i+1), command=lambda x=(2*i+1), y='Cu':btnMClick(x,y), width=6))
        list_Layer[2*i+1].grid(row=2*i+1, column=1)
        list_Layer.append(tk.Button(frame.scrollable_frame, text="PPG"+str(i+1), command=lambda x=(2*i+2), y='PPG':btnMClick(x,y), width=6))
        list_Layer[2*i+2].grid(row=2*i+2, column=1)
    
    list_Layer.append(tk.Button(frame.scrollable_frame, text="L"+str(model.n), command=lambda x=(2*model.n-1), y='Cu':btnMClick(x,y), width=6))
    list_Layer[2*model.n-1].grid(row=2*model.n-1, column=1)
    list_Layer.append(tk.Button(frame.scrollable_frame, text="SR_btm", command=lambda x=(2*model.n), y='SR':btnMClick(x,y), width=6))
    list_Layer[2*model.n].grid(row=2*model.n, column=1)

    if len(list_Thickness)>0:
        for i in range(len(list_Thickness)):
            list_Thickness[i].grid_forget()
    del list_Thickness[0:]
    for i in range(2*model.n+1):
        list_Thickness.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Thickness[i].grid(row=i, column=2)

    if len(list_Modulus)>0:
        for i in range(len(list_Modulus)):
            list_Modulus[i].grid_forget()
    del list_Modulus[0:]
    for i in range(2*model.n+1):
        list_Modulus.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Modulus[i].grid(row=i, column=3)
    
    if len(list_CTE)>0:
        for i in range(len(list_CTE)):
            list_CTE[i].grid_forget()
    del list_CTE[0:]
    for i in range(2*model.n+1):
        list_CTE.append(tk.Entry(frame.scrollable_frame, width=6))
        list_CTE[i].grid(row=i, column=4)

    if len(list_Poisson)>0:
        for i in range(len(list_Poisson)):
            list_Poisson[i].grid_forget()
    del list_Poisson[0:]
    for i in range(2*model.n+1):
        list_Poisson.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Poisson[i].grid(row=i, column=5)
    
    if len(list_Density)>0:
        for i in range(len(list_Density)):
            list_Density[i].grid_forget()
    del list_Density[0:]
    for i in range(2*model.n+1):
        list_Density.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Density[i].grid(row=i, column=6)
    
    if len(list_Fill)>0:
        for i in range(len(list_Fill)):
            list_Fill[i].grid_forget()
    del list_Fill[0:]
    for i in range(model.n):
        list_Fill.append(tkinter.ttk.Combobox(frame.scrollable_frame, width=5, values=['up','down'], state="readonly"))
        if cb_structure.get()=='ETS':
            list_Fill[i].set("down")
        elif cb_structure.get()=='Cored':
            if i<(model.n/2): list_Fill[i].set("up")
            else: list_Fill[i].set("down")
        elif cb_structure.get()=='Coreless_non':
            if i<(model.n/2): list_Fill[i].set("up")
            else: list_Fill[i].set("down")
        elif cb_structure.get()=='Coreless_rev':
            if i<((model.n/2)-1): list_Fill[i].set("up")
            else: list_Fill[i].set("down")
        list_Fill[i].grid(row=(2*i+1), column=7)
    
    #output list 제거
    label_Modulus_unit.place_forget()       #col 10 - unit, 1block, 2block
    label_CTE_unit.place_forget()           #col 11
    label_Poisson_unit.place_forget()       #col 12
    label_Density_unit.place_forget()       #col 13
    label_Modulus_dummy.place_forget()      #col 14 - 1block, 2block
    label_CTE_dummy.place_forget()          #col 15
    label_Poisson_dummy.place_forget()      #col 16
    label_Density_dummy.place_forget()      #col 17

    if len(list_Modulus_unit)>0:
        for i in range(len(list_Modulus_unit)):
            list_Modulus_unit[i].grid_forget()
    del list_Modulus_unit[0:]

    if len(list_CTE_unit)>0:
        for i in range(len(list_CTE_unit)):
            list_CTE_unit[i].grid_forget()
    del list_CTE_unit[0:]

    if len(list_Poisson_unit)>0:
        for i in range(len(list_Poisson_unit)):
            list_Poisson_unit[i].grid_forget()
    del list_Poisson_unit[0:]

    if len(list_Density_unit)>0:
        for i in range(len(list_Density_unit)):
            list_Density_unit[i].grid_forget()
    del list_Density_unit[0:]

    if len(list_Modulus_dummy)>0:
        for i in range(len(list_Modulus_dummy)):
            list_Modulus_dummy[i].grid_forget()
    del list_Modulus_dummy[0:]

    if len(list_CTE_dummy)>0:
        for i in range(len(list_CTE_dummy)):
            list_CTE_dummy[i].grid_forget()
    del list_CTE_dummy[0:]

    if len(list_Poisson_dummy)>0:
        for i in range(len(list_Poisson_dummy)):
            list_Poisson_dummy[i].grid_forget()
    del list_Poisson_dummy[0:]

    if len(list_Density_dummy)>0:
        for i in range(len(list_Density_dummy)):
            list_Density_dummy[i].grid_forget()
    del list_Density_dummy[0:]

    if model.type=='unit':
        label_Portion_unit.place(x=537,y=200,width=47,height=35)
        if len(list_Portion_unit)>0:
            for i in range(len(list_Portion_unit)):
                list_Portion_unit[i].grid_forget()
        del list_Portion_unit[0:]
        list_Portion_unit.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Portion_unit[0].grid(row=0, column=8)
        for i in range(1,model.n+1):
            list_Portion_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            list_Portion_unit[i].grid(row=2*i-1, column=8)
        list_Portion_unit.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Portion_unit[model.n+1].grid(row=2*model.n, column=8)
        if len(list_Portion_dummy)>0:
            for i in range(len(list_Portion_dummy)):
                list_Portion_dummy[i].grid_forget()
        del list_Portion_dummy[0:]
        
    elif (model.type=='1block')|(model.type=='2block'):
        label_Portion_unit.place(x=537,y=200,width=47,height=35)
        label_Portion_dummy.place(x=584,y=200,width=47,height=35)
        if len(list_Portion_unit)>0:
            for i in range(len(list_Portion_unit)):
                list_Portion_unit[i].grid_forget()
        del list_Portion_unit[0:]
        list_Portion_unit.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Portion_unit[0].grid(row=0, column=8)
        for i in range(1,model.n+1):
            list_Portion_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            list_Portion_unit[i].grid(row=2*i-1, column=8)
        list_Portion_unit.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Portion_unit[model.n+1].grid(row=2*model.n, column=8)
        
        if len(list_Portion_dummy)>0:
            for i in range(len(list_Portion_dummy)):
                list_Portion_dummy[i].grid_forget()
        del list_Portion_dummy[0:]
        list_Portion_dummy.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Portion_dummy[0].grid(row=0, column=9)
        for i in range(1,model.n+1):
            list_Portion_dummy.append(tk.Entry(frame.scrollable_frame, width=6))
            list_Portion_dummy[i].grid(row=2*i-1, column=9)
        list_Portion_dummy.append(tk.Entry(frame.scrollable_frame, width=6))
        list_Portion_dummy[model.n+1].grid(row=2*model.n, column=9)

    elif model.type=='meshed':
        if len(list_Portion_unit)>0:
            for i in range(len(list_Portion_unit)):
                list_Portion_unit[i].grid_forget()
        del list_Portion_unit[0:]

        if len(list_Portion_dummy)>0:
            for i in range(len(list_Portion_dummy)):
                list_Portion_dummy[i].grid_forget()
        del list_Portion_dummy[0:]

    button_calc.place(x=35, y=370, width=70, height=30)
    button_save_input.place(x=35, y=450, width=70, height=30)
    button_load_input.place(x=35, y=500, width=70, height=30)

    entry_project.delete(0,tk.END)
    label_result_SQBC.config(text='')
    label_result_warpage.config(text='')
    label_result_CTE.config(text='')
    label_result_modulus.config(text='')

    check_SQBC.deselect()
    check_warpage.deselect()
    check_CTE.deselect()
    check_modulus.deselect()
    check_cpu.deselect()
    check_gui.select()
    check_job.select()

    label_project.place_forget()
    entry_project.place_forget()
    button_SQBC.place_forget()
    button_warpage.place_forget()
    button_CTE.place_forget()
    button_modulus.place_forget()
    label_modeling.place_forget()
    button_shell.place_forget()
    button_solid.place_forget()

    label_result_SQBC.place_forget()
    label_result_warpage.place_forget()
    label_result_CTE.place_forget()
    label_result_modulus.place_forget()

    button_result_SQBC.place_forget()
    button_result_warpage.place_forget()
    button_result_CTE.place_forget()
    button_result_modulus.place_forget()

    check_SQBC.place_forget()
    check_warpage.place_forget()
    check_CTE.place_forget()
    check_modulus.place_forget()
    check_cpu.place_forget()
    check_gui.place_forget()
    check_job.place_forget()
    return

def btnCalcClick():
    #input data(entry) validation
    for i in range(2*model.n+1):
        try:
            if float(list_Thickness[i].get())<=0:
                messagebox.showwarning(title="error",message="Thickness>0")
                return
            if float(list_Modulus[i].get())<=0:
                messagebox.showwarning(title="error",message="Modulus>0")
                return
            if float(list_CTE[i].get())<=0:
                messagebox.showwarning(title="error",message="CTE>0")
                return
            if (float(list_Poisson[i].get())<=-1)|(float(list_Poisson[i].get())>=0.5):
                messagebox.showwarning(title="error",message="Poisson's ratio -1~0.5")
                return
            if float(list_Density[i].get())<=0:
                messagebox.showwarning(title="error",message="Density>0")
                return
        except:
            messagebox.showwarning(title="error",message="invalid data")
            return
    if model.type!='meshed':
        for i in range(model.n+2):
            try:
                if (float(list_Portion_unit[i].get())<=0)|(float(list_Portion_unit[i].get())>100):
                    messagebox.showwarning(title="error",message="portion 0~100")
                    return  
                if (model.type=='1block')|(model.type=='2block'):
                    if (float(list_Portion_dummy[i].get())<=0)|(float(list_Portion_dummy[i].get())>100):
                        messagebox.showwarning(title="error",message="portion 0~100")
                        return  
            except:
                messagebox.showwarning(title="error",message="invalid data")
                return

    label_Modulus_unit.place_forget()       #col 10 - unit, 1block, 2block
    label_CTE_unit.place_forget()           #col 11
    label_Poisson_unit.place_forget()       #col 12
    label_Density_unit.place_forget()       #col 13
    label_Modulus_dummy.place_forget()      #col 14 - 1block, 2block
    label_CTE_dummy.place_forget()          #col 15
    label_Poisson_dummy.place_forget()      #col 16
    label_Density_dummy.place_forget()      #col 17

    if model.type=='unit':
        del L[0:]
        L.append(Layer('SR', 0.001*float(list_Thickness[0].get()), float(list_Modulus[0].get()), float(list_CTE[0].get()), float(list_Poisson[0].get()), float(list_Density[0].get())))
        
        L[0].modulus2=float(df.iloc[int(list_No[0]['text'])].values[8]) * 1000
        L[0].cte2=float(df.iloc[int(list_No[0]['text'])].values[6])
        L[0].Tg=float(df.iloc[int(list_No[0]['text'])].values[9])

        L[0].unit.portion=float(list_Portion_unit[0].get())*0.01            
        L[0].unit.modulus=L[0].modulus * L[0].unit.portion
        L[0].unit.cte=L[0].cte
        L[0].unit.poisson=L[0].poisson * L[0].unit.portion
        L[0].unit.density=L[0].density * L[0].unit.portion

        L[0].unit.cte2=L[0].cte2
        L[0].unit.modulus2=L[0].modulus2 * L[0].unit.portion

        if L[0].Tg>=255:
            L[0].unit.Elastic.append([L[0].unit.modulus, L[0].unit.poisson, 25])
            L[0].unit.Elastic.append([L[0].unit.modulus-10**(int(math.log10(L[0].unit.modulus))-1), L[0].unit.poisson, 250])
            L[0].unit.Elastic.append([L[0].unit.modulus2, L[0].unit.poisson, 260])

            L[0].unit.Expansion.append([L[0].unit.cte, L[0].Tg])
        else:
            L[0].unit.Elastic.append([L[0].unit.modulus, L[0].unit.poisson, 25])
            L[0].unit.Elastic.append([L[0].unit.modulus-10**(int(math.log10(L[0].unit.modulus))-1), L[0].unit.poisson, L[0].Tg-5])
            L[0].unit.Elastic.append([L[0].unit.modulus2+10**(int(math.log10(L[0].unit.modulus2))-1), L[0].unit.poisson, L[0].Tg+5])
            L[0].unit.Elastic.append([L[0].unit.modulus2, L[0].unit.poisson, 260])

            if L[0].Tg<200:
                L[0].unit.Expansion.append([L[0].unit.cte, L[0].Tg])
                L[0].unit.Expansion.append([(L[0].unit.cte*L[0].Tg+L[0].unit.cte2*(200-L[0].Tg))/200, 200])
                L[0].unit.Expansion.append([(L[0].unit.cte*L[0].Tg+L[0].unit.cte2*(260-L[0].Tg))/260, 260])
            else:
                L[0].unit.Expansion.append([L[0].unit.cte, L[0].Tg])
                L[0].unit.Expansion.append([(L[0].unit.cte*L[0].Tg+L[0].unit.cte2*(260-L[0].Tg))/260, 260])
        
        for i in range(model.n-1):
            L.append(Layer('Cu', 0.001*float(list_Thickness[2*i+1].get()), float(list_Modulus[2*i+1].get()), float(list_CTE[2*i+1].get()), float(list_Poisson[2*i+1].get()), float(list_Density[2*i+1].get()), list_Fill[i].get()))
            L[2*i+1].unit.portion=float(list_Portion_unit[i+1].get())*0.01

            L.append(Layer('PPG', 0.001*float(list_Thickness[2*i+2].get()), float(list_Modulus[2*i+2].get()), float(list_CTE[2*i+2].get()), float(list_Poisson[2*i+2].get()), float(list_Density[2*i+2].get())))
            L[2*i+2].modulus2=float(df.iloc[int(list_No[2*i+2]['text'])].values[8]) * 1000
            L[2*i+2].cte2=float(df.iloc[int(list_No[2*i+2]['text'])].values[6])
            L[2*i+2].Tg=float(df.iloc[int(list_No[2*i+2]['text'])].values[9])

            if L[2*i+2].Tg>=255:
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus, L[2*i+2].poisson, 25])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus-10**(int(math.log10(L[2*i+2].modulus))-1), L[2*i+2].poisson, 250])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2, L[2*i+2].poisson, 260])

                L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
            else:
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus, L[2*i+2].poisson, 25])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus-10**(int(math.log10(L[2*i+2].modulus))-1), L[2*i+2].poisson, L[2*i+2].Tg-5])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2+10**(int(math.log10(L[2*i+2].modulus2))-1), L[2*i+2].poisson, L[2*i+2].Tg+5])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2, L[2*i+2].poisson, 260])

                if L[2*i+2].Tg<200:
                    L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(200-L[2*i+2].Tg))/200, 200])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(260-L[2*i+2].Tg))/260, 260])
                else:
                    L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(260-L[2*i+2].Tg))/260, 260])

        L.append(Layer('Cu', 0.001*float(list_Thickness[2*model.n-1].get()), float(list_Modulus[2*model.n-1].get()), float(list_CTE[2*model.n-1].get()), float(list_Poisson[2*model.n-1].get()), float(list_Density[2*model.n-1].get()), list_Fill[model.n-1].get()))
        L[2*model.n-1].unit.portion=float(list_Portion_unit[model.n].get())*0.01

        L.append(Layer('SR', 0.001*float(list_Thickness[2*model.n].get()), float(list_Modulus[2*model.n].get()), float(list_CTE[2*model.n].get()), float(list_Poisson[2*model.n].get()), float(list_Density[2*model.n].get())))
        
        L[2*model.n].modulus2=float(df.iloc[int(list_No[2*model.n]['text'])].values[8]) * 1000
        L[2*model.n].cte2=float(df.iloc[int(list_No[2*model.n]['text'])].values[6])
        L[2*model.n].Tg=float(df.iloc[int(list_No[2*model.n]['text'])].values[9])
        
        L[2*model.n].unit.portion=float(list_Portion_unit[model.n+1].get())*0.01
        L[2*model.n].unit.modulus=L[2*model.n].modulus * L[2*model.n].unit.portion
        L[2*model.n].unit.cte=L[2*model.n].cte
        L[2*model.n].unit.poisson=L[2*model.n].poisson * L[2*model.n].unit.portion
        L[2*model.n].unit.density=L[2*model.n].density * L[2*model.n].unit.portion

        L[2*model.n].unit.cte2=L[2*model.n].cte2
        L[2*model.n].unit.modulus2=L[2*model.n].modulus2 * L[2*model.n].unit.portion

        if L[2*model.n].Tg>=255:
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus, L[2*model.n].unit.poisson, 25])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus-10**(int(math.log10(L[2*model.n].unit.modulus))-1), L[2*model.n].unit.poisson, 250])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus2, L[2*model.n].unit.poisson, 260])

            L[2*model.n].unit.Expansion.append([L[2*model.n].unit.cte, L[2*model.n].Tg])
        else:
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus, L[2*model.n].unit.poisson, 25])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus-10**(int(math.log10(L[2*model.n].unit.modulus))-1), L[2*model.n].unit.poisson, L[2*model.n].Tg-5])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus2+10**(int(math.log10(L[2*model.n].unit.modulus2))-1), L[2*model.n].unit.poisson, L[2*model.n].Tg+5])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus2, L[2*model.n].unit.poisson, 260])

            if L[2*model.n].Tg<200:
                L[2*model.n].unit.Expansion.append([L[2*model.n].unit.cte, L[2*model.n].Tg])
                L[2*model.n].unit.Expansion.append([(L[2*model.n].unit.cte*L[2*model.n].Tg+L[2*model.n].unit.cte2*(200-L[2*model.n].Tg))/200, 200])
                L[2*model.n].unit.Expansion.append([(L[2*model.n].unit.cte*L[2*model.n].Tg+L[2*model.n].unit.cte2*(260-L[2*model.n].Tg))/260, 260])
            else:
                L[2*model.n].unit.Expansion.append([L[2*model.n].unit.cte, L[2*model.n].Tg])
                L[2*model.n].unit.Expansion.append([(L[2*model.n].unit.cte*L[2*model.n].Tg+L[2*model.n].unit.cte2*(260-L[2*model.n].Tg))/260, 260])

        for i in range(model.n):
            if L[2*i+1].fill=='up':
                L[2*i+1].unit.modulus = L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i].modulus * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.cte = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i].cte * L[2*i].modulus * (1-L[2*i+1].unit.portion)) / L[2*i+1].unit.modulus
                L[2*i+1].unit.poisson = L[2*i+1].poisson * L[2*i+1].unit.portion + L[2*i].poisson * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.density = L[2*i+1].density * L[2*i+1].unit.portion + L[2*i].density * (1-L[2*i+1].unit.portion)

                L[2*i+1].unit.modulus2 = L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i].modulus2 * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.cte2 = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i].cte2 * L[2*i].modulus2 * (1-L[2*i+1].unit.portion)) / L[2*i+1].unit.modulus2

                if L[2*i].Tg>=255:
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus, L[2*i+1].unit.poisson, 25])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus-10**(int(math.log10(L[2*i+1].unit.modulus))-1), L[2*i+1].unit.poisson, 250])
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2, L[2*i+1].unit.poisson, 260])

                    L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i].Tg])
                else:
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus, L[2*i+1].unit.poisson, 25])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus-10**(int(math.log10(L[2*i+1].unit.modulus))-1), L[2*i+1].unit.poisson, L[2*i].Tg-5])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2+10**(int(math.log10(L[2*i+1].unit.modulus2))-1), L[2*i+1].unit.poisson, L[2*i].Tg+5])
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2, L[2*i+1].unit.poisson, 260])

                    if L[2*i].Tg<200:
                        L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i].Tg])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i].Tg+L[2*i+1].unit.cte2*(200-L[2*i].Tg))/200, 200])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i].Tg+L[2*i+1].unit.cte2*(260-L[2*i].Tg))/260, 260])
                    else:
                        L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i].Tg])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i].Tg+L[2*i+1].unit.cte2*(260-L[2*i].Tg))/260, 260])

            elif L[2*i+1].fill=='down':
                L[2*i+1].unit.modulus = L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i+2].modulus * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.cte = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i+2].cte * L[2*i+2].modulus * (1-L[2*i+1].unit.portion)) / L[2*i+1].unit.modulus
                L[2*i+1].unit.poisson = L[2*i+1].poisson * L[2*i+1].unit.portion + L[2*i+2].poisson * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.density = L[2*i+1].density * L[2*i+1].unit.portion + L[2*i+2].density * (1-L[2*i+1].unit.portion)

                L[2*i+1].unit.modulus2 = L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i+2].modulus2 * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.cte2 = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i+2].cte2 * L[2*i+2].modulus2 * (1-L[2*i+1].unit.portion)) / L[2*i+1].unit.modulus2

                if L[2*i+2].Tg>=255:
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus, L[2*i+1].unit.poisson, 25])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus-10**(int(math.log10(L[2*i+1].unit.modulus))-1), L[2*i+1].unit.poisson, 250])
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2, L[2*i+1].unit.poisson, 260])

                    L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i+2].Tg])
                else:
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus, L[2*i+1].unit.poisson, 25])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus-10**(int(math.log10(L[2*i+1].unit.modulus))-1), L[2*i+1].unit.poisson, L[2*i+2].Tg-5])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2+10**(int(math.log10(L[2*i+1].unit.modulus2))-1), L[2*i+1].unit.poisson, L[2*i+2].Tg+5])
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2, L[2*i+1].unit.poisson, 260])

                    if L[2*i+2].Tg<200:
                        L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i+2].Tg])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i+2].Tg+L[2*i+1].unit.cte2*(200-L[2*i+2].Tg))/200, 200])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i+2].Tg+L[2*i+1].unit.cte2*(260-L[2*i+2].Tg))/260, 260])
                    else:
                        L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i+2].Tg])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i+2].Tg+L[2*i+1].unit.cte2*(260-L[2*i+2].Tg))/260, 260])

            
        label_Modulus_unit.place(x=584,y=200,width=47,height=35)    #col10->9 584
        label_CTE_unit.place(x=631,y=200,width=47,height=35)        #col11->10 631
        label_Poisson_unit.place(x=678,y=200,width=47,height=35)    #col12->11 678
        label_Density_unit.place(x=725,y=200,width=47,height=35)    #col13->12 725

        if len(list_Modulus_unit)>0:
            for i in range(len(list_Modulus_unit)):
                list_Modulus_unit[i].grid_forget()
        del list_Modulus_unit[0:]
        for i in range(2*model.n+1):
            list_Modulus_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Modulus_unit[i].insert(0,str(round(L[i].modulus)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Modulus_unit[i].insert(0,str(round(L[i].unit.modulus)))
            list_Modulus_unit[i].grid(row=i, column=9)
        
        if len(list_CTE_unit)>0:
            for i in range(len(list_CTE_unit)):
                list_CTE_unit[i].grid_forget()
        del list_CTE_unit[0:]
        for i in range(2*model.n+1):
            list_CTE_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_CTE_unit[i].insert(0,str(round(L[i].cte,2)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_CTE_unit[i].insert(0,str(round(L[i].unit.cte,2)))
            list_CTE_unit[i].grid(row=i, column=10)
        
        if len(list_Poisson_unit)>0:
            for i in range(len(list_Poisson_unit)):
                list_Poisson_unit[i].grid_forget()
        del list_Poisson_unit[0:]
        for i in range(2*model.n+1):
            list_Poisson_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Poisson_unit[i].insert(0,str(round(L[i].poisson,4)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Poisson_unit[i].insert(0,str(round(L[i].unit.poisson,4)))
            list_Poisson_unit[i].grid(row=i, column=11)
        
        if len(list_Density_unit)>0:
            for i in range(len(list_Density_unit)):
                list_Density_unit[i].grid_forget()
        del list_Density_unit[0:]
        for i in range(2*model.n+1):
            list_Density_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Density_unit[i].insert(0,str(round(L[i].density,3)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Density_unit[i].insert(0,str(round(L[i].unit.density,3)))
            list_Density_unit[i].grid(row=i, column=12)

    elif (model.type=='1block')|(model.type=='2block'):
        del L[0:]
        L.append(Layer('SR', 0.001*float(list_Thickness[0].get()), float(list_Modulus[0].get()), float(list_CTE[0].get()), float(list_Poisson[0].get()), float(list_Density[0].get())))
        
        L[0].modulus2=float(df.iloc[int(list_No[0]['text'])].values[8]) * 1000
        L[0].cte2=float(df.iloc[int(list_No[0]['text'])].values[6])
        L[0].Tg=float(df.iloc[int(list_No[0]['text'])].values[9])

        L[0].unit.portion=float(list_Portion_unit[0].get())*0.01
        L[0].unit.modulus=L[0].modulus * L[0].unit.portion
        L[0].unit.cte=L[0].cte
        L[0].unit.poisson=L[0].poisson * L[0].unit.portion
        L[0].unit.density=L[0].density * L[0].unit.portion

        L[0].unit.cte2=L[0].cte2
        L[0].unit.modulus2=L[0].modulus2 * L[0].unit.portion

        L[0].dummy.portion=float(list_Portion_dummy[0].get())*0.01            
        L[0].dummy.modulus=L[0].modulus * L[0].dummy.portion
        L[0].dummy.cte=L[0].cte
        L[0].dummy.poisson=L[0].poisson * L[0].dummy.portion
        L[0].dummy.density=L[0].density * L[0].dummy.portion

        L[0].dummy.cte2=L[0].cte2
        L[0].dummy.modulus2=L[0].modulus2 * L[0].dummy.portion

        if L[0].Tg>=255:
            L[0].unit.Elastic.append([L[0].unit.modulus, L[0].unit.poisson, 25])
            L[0].unit.Elastic.append([L[0].unit.modulus-10**(int(math.log10(L[0].unit.modulus))-1), L[0].unit.poisson, 250])
            L[0].unit.Elastic.append([L[0].unit.modulus2, L[0].unit.poisson, 260])

            L[0].unit.Expansion.append([L[0].unit.cte, L[0].Tg])

            L[0].dummy.Elastic.append([L[0].dummy.modulus, L[0].dummy.poisson, 25])
            L[0].dummy.Elastic.append([L[0].dummy.modulus-10**(int(math.log10(L[0].dummy.modulus))-1), L[0].dummy.poisson, 250])
            L[0].dummy.Elastic.append([L[0].dummy.modulus2, L[0].dummy.poisson, 260])

            L[0].dummy.Expansion.append([L[0].dummy.cte, L[0].Tg])
        else:
            L[0].unit.Elastic.append([L[0].unit.modulus, L[0].unit.poisson, 25])
            L[0].unit.Elastic.append([L[0].unit.modulus-10**(int(math.log10(L[0].unit.modulus))-1), L[0].unit.poisson, L[0].Tg-5])
            L[0].unit.Elastic.append([L[0].unit.modulus2+10**(int(math.log10(L[0].unit.modulus2))-1), L[0].unit.poisson, L[0].Tg+5])
            L[0].unit.Elastic.append([L[0].unit.modulus2, L[0].unit.poisson, 260])

            L[0].dummy.Elastic.append([L[0].dummy.modulus, L[0].dummy.poisson, 25])
            L[0].dummy.Elastic.append([L[0].dummy.modulus-10**(int(math.log10(L[0].dummy.modulus))-1), L[0].dummy.poisson, L[0].Tg-5])
            L[0].dummy.Elastic.append([L[0].dummy.modulus2+10**(int(math.log10(L[0].dummy.modulus2))-1), L[0].dummy.poisson, L[0].Tg+5])
            L[0].dummy.Elastic.append([L[0].dummy.modulus2, L[0].dummy.poisson, 260])

            if L[0].Tg<200:
                L[0].unit.Expansion.append([L[0].unit.cte, L[0].Tg])
                L[0].unit.Expansion.append([(L[0].unit.cte*L[0].Tg+L[0].unit.cte2*(200-L[0].Tg))/200, 200])
                L[0].unit.Expansion.append([(L[0].unit.cte*L[0].Tg+L[0].unit.cte2*(260-L[0].Tg))/260, 260])

                L[0].dummy.Expansion.append([L[0].dummy.cte, L[0].Tg])
                L[0].dummy.Expansion.append([(L[0].dummy.cte*L[0].Tg+L[0].dummy.cte2*(200-L[0].Tg))/200, 200])
                L[0].dummy.Expansion.append([(L[0].dummy.cte*L[0].Tg+L[0].dummy.cte2*(260-L[0].Tg))/260, 260])
            else:
                L[0].unit.Expansion.append([L[0].unit.cte, L[0].Tg])
                L[0].unit.Expansion.append([(L[0].unit.cte*L[0].Tg+L[0].unit.cte2*(260-L[0].Tg))/260, 260])

                L[0].dummy.Expansion.append([L[0].dummy.cte, L[0].Tg])
                L[0].dummy.Expansion.append([(L[0].dummy.cte*L[0].Tg+L[0].dummy.cte2*(260-L[0].Tg))/260, 260])
                

        for i in range(model.n-1):
            L.append(Layer('Cu', 0.001*float(list_Thickness[2*i+1].get()), float(list_Modulus[2*i+1].get()), float(list_CTE[2*i+1].get()), float(list_Poisson[2*i+1].get()), float(list_Density[2*i+1].get()), list_Fill[i].get()))
            L[2*i+1].unit.portion=float(list_Portion_unit[i+1].get())*0.01
            L[2*i+1].dummy.portion=float(list_Portion_dummy[i+1].get())*0.01

            L.append(Layer('PPG', 0.001*float(list_Thickness[2*i+2].get()), float(list_Modulus[2*i+2].get()), float(list_CTE[2*i+2].get()), float(list_Poisson[2*i+2].get()), float(list_Density[2*i+2].get())))
            L[2*i+2].modulus2=float(df.iloc[int(list_No[2*i+2]['text'])].values[8]) * 1000
            L[2*i+2].cte2=float(df.iloc[int(list_No[2*i+2]['text'])].values[6])
            L[2*i+2].Tg=float(df.iloc[int(list_No[2*i+2]['text'])].values[9])

            if L[2*i+2].Tg>=255:
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus, L[2*i+2].poisson, 25])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus-10**(int(math.log10(L[2*i+2].modulus))-1), L[2*i+2].poisson, 250])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2, L[2*i+2].poisson, 260])

                L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
            else:
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus, L[2*i+2].poisson, 25])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus-10**(int(math.log10(L[2*i+2].modulus))-1), L[2*i+2].poisson, L[2*i+2].Tg-5])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2+10**(int(math.log10(L[2*i+2].modulus2))-1), L[2*i+2].poisson, L[2*i+2].Tg+5])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2, L[2*i+2].poisson, 260])

                if L[2*i+2].Tg<200:
                    L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(200-L[2*i+2].Tg))/200, 200])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(260-L[2*i+2].Tg))/260, 260])
                else:
                    L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(260-L[2*i+2].Tg))/260, 260])

        L.append(Layer('Cu', 0.001*float(list_Thickness[2*model.n-1].get()), float(list_Modulus[2*model.n-1].get()), float(list_CTE[2*model.n-1].get()), float(list_Poisson[2*model.n-1].get()), float(list_Density[2*model.n-1].get()), list_Fill[model.n-1].get()))
        L[2*model.n-1].unit.portion=float(list_Portion_unit[model.n].get())*0.01
        L[2*model.n-1].dummy.portion=float(list_Portion_dummy[model.n].get())*0.01   

        L.append(Layer('SR', 0.001*float(list_Thickness[2*model.n].get()), float(list_Modulus[2*model.n].get()), float(list_CTE[2*model.n].get()), float(list_Poisson[2*model.n].get()), float(list_Density[2*model.n].get())))
        L[2*model.n].unit.portion=float(list_Portion_unit[model.n+1].get())*0.01
        L[2*model.n].dummy.portion=float(list_Portion_dummy[model.n+1].get())*0.01

        L[2*model.n].unit.modulus=L[2*model.n].modulus * L[2*model.n].unit.portion
        L[2*model.n].unit.cte=L[2*model.n].cte
        L[2*model.n].unit.poisson=L[2*model.n].poisson * L[2*model.n].unit.portion
        L[2*model.n].unit.density=L[2*model.n].density * L[2*model.n].unit.portion

        L[2*model.n].dummy.modulus=L[2*model.n].modulus * L[2*model.n].dummy.portion
        L[2*model.n].dummy.cte=L[2*model.n].cte
        L[2*model.n].dummy.poisson=L[2*model.n].poisson * L[2*model.n].dummy.portion
        L[2*model.n].dummy.density=L[2*model.n].density * L[2*model.n].dummy.portion

        L[2*model.n].modulus2=float(df.iloc[int(list_No[2*model.n]['text'])].values[8]) * 1000
        L[2*model.n].cte2=float(df.iloc[int(list_No[2*model.n]['text'])].values[6])
        L[2*model.n].Tg=float(df.iloc[int(list_No[2*model.n]['text'])].values[9])

        L[2*model.n].unit.cte2=L[2*model.n].cte2
        L[2*model.n].unit.modulus2=L[2*model.n].modulus2 * L[2*model.n].unit.portion

        L[2*model.n].dummy.cte2=L[2*model.n].cte2
        L[2*model.n].dummy.modulus2=L[2*model.n].modulus2 * L[2*model.n].dummy.portion

        if L[2*model.n].Tg>=255:
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus, L[2*model.n].unit.poisson, 25])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus-10**(int(math.log10(L[2*model.n].unit.modulus))-1), L[2*model.n].unit.poisson, 250])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus2, L[2*model.n].unit.poisson, 260])

            L[2*model.n].unit.Expansion.append([L[2*model.n].unit.cte, L[2*model.n].Tg])

            L[2*model.n].dummy.Elastic.append([L[2*model.n].dummy.modulus, L[2*model.n].dummy.poisson, 25])
            L[2*model.n].dummy.Elastic.append([L[2*model.n].dummy.modulus-10**(int(math.log10(L[2*model.n].dummy.modulus))-1), L[2*model.n].dummy.poisson, 250])
            L[2*model.n].dummy.Elastic.append([L[2*model.n].dummy.modulus2, L[2*model.n].dummy.poisson, 260])

            L[2*model.n].dummy.Expansion.append([L[2*model.n].dummy.cte, L[2*model.n].Tg])
        else:
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus, L[2*model.n].unit.poisson, 25])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus-10**(int(math.log10(L[2*model.n].unit.modulus))-1), L[2*model.n].unit.poisson, L[2*model.n].Tg-5])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus2+10**(int(math.log10(L[2*model.n].unit.modulus2))-1), L[2*model.n].unit.poisson, L[2*model.n].Tg+5])
            L[2*model.n].unit.Elastic.append([L[2*model.n].unit.modulus2, L[2*model.n].unit.poisson, 260])

            L[2*model.n].dummy.Elastic.append([L[2*model.n].dummy.modulus, L[2*model.n].dummy.poisson, 25])
            L[2*model.n].dummy.Elastic.append([L[2*model.n].dummy.modulus-10**(int(math.log10(L[2*model.n].dummy.modulus))-1), L[2*model.n].dummy.poisson, L[2*model.n].Tg-5])
            L[2*model.n].dummy.Elastic.append([L[2*model.n].dummy.modulus2+10**(int(math.log10(L[2*model.n].dummy.modulus2))-1), L[2*model.n].dummy.poisson, L[2*model.n].Tg+5])
            L[2*model.n].dummy.Elastic.append([L[2*model.n].dummy.modulus2, L[2*model.n].dummy.poisson, 260])

            if L[2*model.n].Tg<200:
                L[2*model.n].unit.Expansion.append([L[2*model.n].unit.cte, L[2*model.n].Tg])
                L[2*model.n].unit.Expansion.append([(L[2*model.n].unit.cte*L[2*model.n].Tg+L[2*model.n].unit.cte2*(200-L[2*model.n].Tg))/200, 200])
                L[2*model.n].unit.Expansion.append([(L[2*model.n].unit.cte*L[2*model.n].Tg+L[2*model.n].unit.cte2*(260-L[2*model.n].Tg))/260, 260])

                L[2*model.n].dummy.Expansion.append([L[2*model.n].dummy.cte, L[2*model.n].Tg])
                L[2*model.n].dummy.Expansion.append([(L[2*model.n].dummy.cte*L[2*model.n].Tg+L[2*model.n].dummy.cte2*(200-L[2*model.n].Tg))/200, 200])
                L[2*model.n].dummy.Expansion.append([(L[2*model.n].dummy.cte*L[2*model.n].Tg+L[2*model.n].dummy.cte2*(260-L[2*model.n].Tg))/260, 260])
            else:
                L[2*model.n].unit.Expansion.append([L[2*model.n].unit.cte, L[2*model.n].Tg])
                L[2*model.n].unit.Expansion.append([(L[2*model.n].unit.cte*L[2*model.n].Tg+L[2*model.n].unit.cte2*(260-L[2*model.n].Tg))/260, 260])

                L[2*model.n].dummy.Expansion.append([L[2*model.n].dummy.cte, L[2*model.n].Tg])
                L[2*model.n].dummy.Expansion.append([(L[2*model.n].dummy.cte*L[2*model.n].Tg+L[2*model.n].dummy.cte2*(260-L[2*model.n].Tg))/260, 260])

        for i in range(model.n):
            if L[2*i+1].fill=='up':
                L[2*i+1].unit.modulus = L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i].modulus * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.cte = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i].cte * L[2*i].modulus * (1-L[2*i+1].unit.portion)) / L[2*i+1].unit.modulus
                L[2*i+1].unit.poisson = L[2*i+1].poisson * L[2*i+1].unit.portion + L[2*i].poisson * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.density = L[2*i+1].density * L[2*i+1].unit.portion + L[2*i].density * (1-L[2*i+1].unit.portion)

                L[2*i+1].dummy.modulus = L[2*i+1].modulus * L[2*i+1].dummy.portion + L[2*i].modulus * (1-L[2*i+1].dummy.portion)
                L[2*i+1].dummy.cte = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].dummy.portion + L[2*i].cte * L[2*i].modulus * (1-L[2*i+1].dummy.portion)) / L[2*i+1].dummy.modulus
                L[2*i+1].dummy.poisson = L[2*i+1].poisson * L[2*i+1].dummy.portion + L[2*i].poisson * (1-L[2*i+1].dummy.portion)
                L[2*i+1].dummy.density = L[2*i+1].density * L[2*i+1].dummy.portion + L[2*i].density * (1-L[2*i+1].dummy.portion)

                L[2*i+1].unit.modulus2 = L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i].modulus2 * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.cte2 = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i].cte2 * L[2*i].modulus2 * (1-L[2*i+1].unit.portion)) / L[2*i+1].unit.modulus2

                L[2*i+1].dummy.modulus2 = L[2*i+1].modulus * L[2*i+1].dummy.portion + L[2*i].modulus2 * (1-L[2*i+1].dummy.portion)
                L[2*i+1].dummy.cte2 = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].dummy.portion + L[2*i].cte2 * L[2*i].modulus2 * (1-L[2*i+1].dummy.portion)) / L[2*i+1].dummy.modulus2

                if L[2*i].Tg>=255:
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus, L[2*i+1].unit.poisson, 25])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus-10**(int(math.log10(L[2*i+1].unit.modulus))-1), L[2*i+1].unit.poisson, 250])
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2, L[2*i+1].unit.poisson, 260])

                    L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i].Tg])

                    L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson, 25])
                    #L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus-10**(int(math.log10(L[2*i+1].dummy.modulus))-1), L[2*i+1].dummy.poisson, 250])
                    L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus2, L[2*i+1].dummy.poisson, 260])

                    L[2*i+1].dummy.Expansion.append([L[2*i+1].dummy.cte, L[2*i].Tg])
                else:
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus, L[2*i+1].unit.poisson, 25])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus-10**(int(math.log10(L[2*i+1].unit.modulus))-1), L[2*i+1].unit.poisson, L[2*i].Tg-5])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2+10**(int(math.log10(L[2*i+1].unit.modulus2))-1), L[2*i+1].unit.poisson, L[2*i].Tg+5])
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2, L[2*i+1].unit.poisson, 260])

                    L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson, 25])
                    #L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus-10**(int(math.log10(L[2*i+1].dummy.modulus))-1), L[2*i+1].dummy.poisson, L[2*i].Tg-5])
                    #L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus2+10**(int(math.log10(L[2*i+1].dummy.modulus2))-1), L[2*i+1].dummy.poisson, L[2*i].Tg+5])
                    L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus2, L[2*i+1].dummy.poisson, 260])

                    if L[2*i].Tg<200:
                        L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i].Tg])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i].Tg+L[2*i+1].unit.cte2*(200-L[2*i].Tg))/200, 200])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i].Tg+L[2*i+1].unit.cte2*(260-L[2*i].Tg))/260, 260])

                        L[2*i+1].dummy.Expansion.append([L[2*i+1].dummy.cte, L[2*i].Tg])
                        L[2*i+1].dummy.Expansion.append([(L[2*i+1].dummy.cte*L[2*i].Tg+L[2*i+1].dummy.cte2*(200-L[2*i].Tg))/200, 200])
                        L[2*i+1].dummy.Expansion.append([(L[2*i+1].dummy.cte*L[2*i].Tg+L[2*i+1].dummy.cte2*(260-L[2*i].Tg))/260, 260])
                    else:
                        L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i].Tg])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i].Tg+L[2*i+1].unit.cte2*(260-L[2*i].Tg))/260, 260])

                        L[2*i+1].dummy.Expansion.append([L[2*i+1].dummy.cte, L[2*i].Tg])
                        L[2*i+1].dummy.Expansion.append([(L[2*i+1].dummy.cte*L[2*i].Tg+L[2*i+1].dummy.cte2*(260-L[2*i].Tg))/260, 260])

            elif L[2*i+1].fill=='down':
                L[2*i+1].unit.modulus = L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i+2].modulus * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.cte = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i+2].cte * L[2*i+2].modulus * (1-L[2*i+1].unit.portion)) / L[2*i+1].unit.modulus
                L[2*i+1].unit.poisson = L[2*i+1].poisson * L[2*i+1].unit.portion + L[2*i+2].poisson * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.density = L[2*i+1].density * L[2*i+1].unit.portion + L[2*i+2].density * (1-L[2*i+1].unit.portion)

                L[2*i+1].dummy.modulus = L[2*i+1].modulus * L[2*i+1].dummy.portion + L[2*i+2].modulus * (1-L[2*i+1].dummy.portion)
                L[2*i+1].dummy.cte = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].dummy.portion + L[2*i+2].cte * L[2*i+2].modulus * (1-L[2*i+1].dummy.portion)) / L[2*i+1].dummy.modulus
                L[2*i+1].dummy.poisson = L[2*i+1].poisson * L[2*i+1].dummy.portion + L[2*i+2].poisson * (1-L[2*i+1].dummy.portion)
                L[2*i+1].dummy.density = L[2*i+1].density * L[2*i+1].dummy.portion + L[2*i+2].density * (1-L[2*i+1].dummy.portion)

                L[2*i+1].unit.modulus2 = L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i+2].modulus2 * (1-L[2*i+1].unit.portion)
                L[2*i+1].unit.cte2 = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].unit.portion + L[2*i+2].cte2 * L[2*i+2].modulus2 * (1-L[2*i+1].unit.portion)) / L[2*i+1].unit.modulus2

                L[2*i+1].dummy.modulus2 = L[2*i+1].modulus * L[2*i+1].dummy.portion + L[2*i+2].modulus2 * (1-L[2*i+1].dummy.portion)
                L[2*i+1].dummy.cte2 = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].dummy.portion + L[2*i+2].cte2 * L[2*i+2].modulus2 * (1-L[2*i+1].dummy.portion)) / L[2*i+1].dummy.modulus2

                if L[2*i+2].Tg>=255:
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus, L[2*i+1].unit.poisson, 25])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus-10**(int(math.log10(L[2*i+1].unit.modulus))-1), L[2*i+1].unit.poisson, 250])
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2, L[2*i+1].unit.poisson, 260])

                    L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i+2].Tg])

                    L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson, 25])
                    #L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus-10**(int(math.log10(L[2*i+1].dummy.modulus))-1), L[2*i+1].dummy.poisson, 250])
                    L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus2, L[2*i+1].dummy.poisson, 260])

                    L[2*i+1].dummy.Expansion.append([L[2*i+1].dummy.cte, L[2*i+2].Tg])
                else:
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus, L[2*i+1].unit.poisson, 25])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus-10**(int(math.log10(L[2*i+1].unit.modulus))-1), L[2*i+1].unit.poisson, L[2*i+2].Tg-5])
                    #L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2+10**(int(math.log10(L[2*i+1].unit.modulus2))-1), L[2*i+1].unit.poisson, L[2*i+2].Tg+5])
                    L[2*i+1].unit.Elastic.append([L[2*i+1].unit.modulus2, L[2*i+1].unit.poisson, 260])

                    L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson, 25])
                    #L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus-10**(int(math.log10(L[2*i+1].dummy.modulus))-1), L[2*i+1].dummy.poisson, L[2*i+2].Tg-5])
                    #L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus2+10**(int(math.log10(L[2*i+1].dummy.modulus2))-1), L[2*i+1].dummy.poisson, L[2*i+2].Tg+5])
                    L[2*i+1].dummy.Elastic.append([L[2*i+1].dummy.modulus2, L[2*i+1].dummy.poisson, 260])

                    if L[2*i+2].Tg<200:
                        L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i+2].Tg])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i+2].Tg+L[2*i+1].unit.cte2*(200-L[2*i+2].Tg))/200, 200])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i+2].Tg+L[2*i+1].unit.cte2*(260-L[2*i+2].Tg))/260, 260])

                        L[2*i+1].dummy.Expansion.append([L[2*i+1].dummy.cte, L[2*i+2].Tg])
                        L[2*i+1].dummy.Expansion.append([(L[2*i+1].dummy.cte*L[2*i+2].Tg+L[2*i+1].dummy.cte2*(200-L[2*i+2].Tg))/200, 200])
                        L[2*i+1].dummy.Expansion.append([(L[2*i+1].dummy.cte*L[2*i+2].Tg+L[2*i+1].dummy.cte2*(260-L[2*i+2].Tg))/260, 260])
                    else:
                        L[2*i+1].unit.Expansion.append([L[2*i+1].unit.cte, L[2*i+2].Tg])
                        L[2*i+1].unit.Expansion.append([(L[2*i+1].unit.cte*L[2*i+2].Tg+L[2*i+1].unit.cte2*(260-L[2*i+2].Tg))/260, 260])

                        L[2*i+1].dummy.Expansion.append([L[2*i+1].dummy.cte, L[2*i+2].Tg])
                        L[2*i+1].dummy.Expansion.append([(L[2*i+1].dummy.cte*L[2*i+2].Tg+L[2*i+1].dummy.cte2*(260-L[2*i+2].Tg))/260, 260])

        label_Modulus_unit.place(x=631,y=200,width=47,height=35)    #col10
        label_CTE_unit.place(x=678,y=200,width=47,height=35)        #col11
        label_Poisson_unit.place(x=725,y=200,width=47,height=35)    #col12
        label_Density_unit.place(x=772,y=200,width=47,height=35)    #col13

        label_Modulus_dummy.place(x=819,y=200,width=47,height=35)    #col14
        label_CTE_dummy.place(x=866,y=200,width=47,height=35)        #col15
        label_Poisson_dummy.place(x=913,y=200,width=47,height=35)    #col16
        label_Density_dummy.place(x=960,y=200,width=47,height=35)    #col17

        if len(list_Modulus_unit)>0:
            for i in range(len(list_Modulus_unit)):
                list_Modulus_unit[i].grid_forget()
        del list_Modulus_unit[0:]
        for i in range(2*model.n+1):
            list_Modulus_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Modulus_unit[i].insert(0,str(round(L[i].modulus)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Modulus_unit[i].insert(0,str(round(L[i].unit.modulus)))
            list_Modulus_unit[i].grid(row=i, column=10)
        
        if len(list_CTE_unit)>0:
            for i in range(len(list_CTE_unit)):
                list_CTE_unit[i].grid_forget()
        del list_CTE_unit[0:]
        for i in range(2*model.n+1):
            list_CTE_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_CTE_unit[i].insert(0,str(round(L[i].cte,2)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_CTE_unit[i].insert(0,str(round(L[i].unit.cte,2)))
            list_CTE_unit[i].grid(row=i, column=11)
        
        if len(list_Poisson_unit)>0:
            for i in range(len(list_Poisson_unit)):
                list_Poisson_unit[i].grid_forget()
        del list_Poisson_unit[0:]
        for i in range(2*model.n+1):
            list_Poisson_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Poisson_unit[i].insert(0,str(round(L[i].poisson,4)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Poisson_unit[i].insert(0,str(round(L[i].unit.poisson,4)))
            list_Poisson_unit[i].grid(row=i, column=12)
        
        if len(list_Density_unit)>0:
            for i in range(len(list_Density_unit)):
                list_Density_unit[i].grid_forget()
        del list_Density_unit[0:]
        for i in range(2*model.n+1):
            list_Density_unit.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Density_unit[i].insert(0,str(round(L[i].density,3)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Density_unit[i].insert(0,str(round(L[i].unit.density,3)))
            list_Density_unit[i].grid(row=i, column=13)

        if len(list_Modulus_dummy)>0:
            for i in range(len(list_Modulus_dummy)):
                list_Modulus_dummy[i].grid_forget()
        del list_Modulus_dummy[0:]
        for i in range(2*model.n+1):
            list_Modulus_dummy.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Modulus_dummy[i].insert(0,str(round(L[i].modulus)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Modulus_dummy[i].insert(0,str(round(L[i].dummy.modulus)))
            list_Modulus_dummy[i].grid(row=i, column=14)
        
        if len(list_CTE_dummy)>0:
            for i in range(len(list_CTE_dummy)):
                list_CTE_dummy[i].grid_forget()
        del list_CTE_dummy[0:]
        for i in range(2*model.n+1):
            list_CTE_dummy.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_CTE_dummy[i].insert(0,str(round(L[i].cte,2)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_CTE_dummy[i].insert(0,str(round(L[i].dummy.cte,2)))
            list_CTE_dummy[i].grid(row=i, column=15)
        
        if len(list_Poisson_dummy)>0:
            for i in range(len(list_Poisson_dummy)):
                list_Poisson_dummy[i].grid_forget()
        del list_Poisson_dummy[0:]
        for i in range(2*model.n+1):
            list_Poisson_dummy.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Poisson_dummy[i].insert(0,str(round(L[i].poisson,4)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Poisson_dummy[i].insert(0,str(round(L[i].dummy.poisson,4)))
            list_Poisson_dummy[i].grid(row=i, column=16)
        
        if len(list_Density_dummy)>0:
            for i in range(len(list_Density_dummy)):
                list_Density_dummy[i].grid_forget()
        del list_Density_dummy[0:]
        for i in range(2*model.n+1):
            list_Density_dummy.append(tk.Entry(frame.scrollable_frame, width=6))
            if L[i].material=='PPG':
                list_Density_dummy[i].insert(0,str(round(L[i].density,3)))
            elif (L[i].material=='SR')|(L[i].material=='Cu'):
                list_Density_dummy[i].insert(0,str(round(L[i].dummy.density,3)))
            list_Density_dummy[i].grid(row=i, column=17) 
        
    elif model.type=='meshed':
        del L[0:]
        L.append(Layer('SR', 0.001*float(list_Thickness[0].get()), float(list_Modulus[0].get()), float(list_CTE[0].get()), float(list_Poisson[0].get()), float(list_Density[0].get()), row=model.row, col=model.col))
        
        L[0].modulus2=float(df.iloc[int(list_No[0]['text'])].values[8]) * 1000
        L[0].cte2=float(df.iloc[int(list_No[0]['text'])].values[6])
        L[0].Tg=float(df.iloc[int(list_No[0]['text'])].values[9])

        with open(model.folder+'/SR_top.txt') as f:
            for row in range(model.row):
                text=''
                text=f.readline().split()
                for col in range(model.col):
                    try:
                        if (float(text[col])<0)|(float(text[col])>100):
                            messagebox.showwarning(title="error",message="invalid data : portion(SR_top)")
                            return
                    except:
                        messagebox.showwarning(title="error",message="invalid data : portion(SR_top)")
                        return

                    L[0].section[row][col].portion=float(text[col])*0.01
                    if(L[0].section[row][col].portion)==0: #air
                        L[0].section[row][col].modulus=0.0001
                        L[0].section[row][col].cte=0.001
                        L[0].section[row][col].poisson=0.001
                        L[0].section[row][col].density=0.00118

                        L[0].section[row][col].modulus2=0.0001
                        L[0].section[row][col].cte2=0.001

                        L[0].section[row][col].Elastic.append([L[0].section[row][col].modulus, L[0].section[row][col].poisson, 300])
                        L[0].section[row][col].Expansion.append([L[0].section[row][col].cte, 300])
                    else:
                        L[0].section[row][col].modulus=L[0].modulus * L[0].section[row][col].portion
                        L[0].section[row][col].cte=L[0].cte
                        L[0].section[row][col].poisson=L[0].poisson * L[0].section[row][col].portion
                        L[0].section[row][col].density=L[0].density * L[0].section[row][col].portion

                        L[0].section[row][col].modulus2=L[0].modulus2 * L[0].section[row][col].portion
                        L[0].section[row][col].cte2=L[0].cte2

                        if L[0].Tg>=255:
                            L[0].section[row][col].Elastic.append([L[0].section[row][col].modulus, L[0].section[row][col].poisson, 25])
                            L[0].section[row][col].Elastic.append([L[0].section[row][col].modulus-10**(int(math.log10(L[0].section[row][col].modulus))-1), L[0].section[row][col].poisson, 250])
                            L[0].section[row][col].Elastic.append([L[0].section[row][col].modulus2, L[0].section[row][col].poisson, 260])

                            L[0].section[row][col].Expansion.append([L[0].section[row][col].cte, L[0].Tg])
                        else:
                            L[0].section[row][col].Elastic.append([L[0].section[row][col].modulus, L[0].section[row][col].poisson, 25])
                            L[0].section[row][col].Elastic.append([L[0].section[row][col].modulus-10**(int(math.log10(L[0].section[row][col].modulus))-1), L[0].section[row][col].poisson, L[0].Tg-5])
                            L[0].section[row][col].Elastic.append([L[0].section[row][col].modulus2+10**(int(math.log10(L[0].section[row][col].modulus2))-1), L[0].section[row][col].poisson, L[0].Tg+5])
                            L[0].section[row][col].Elastic.append([L[0].section[row][col].modulus2, L[0].section[row][col].poisson, 260])

                            if L[0].Tg<200:
                                L[0].section[row][col].Expansion.append([L[0].section[row][col].cte, L[0].Tg])
                                L[0].section[row][col].Expansion.append([(L[0].section[row][col].cte*L[0].Tg+L[0].section[row][col].cte2*(200-L[0].Tg))/200, 200])
                                L[0].section[row][col].Expansion.append([(L[0].section[row][col].cte*L[0].Tg+L[0].section[row][col].cte2*(260-L[0].Tg))/260, 260])
                            else:
                                L[0].section[row][col].Expansion.append([L[0].section[row][col].cte, L[0].Tg])
                                L[0].section[row][col].Expansion.append([(L[0].section[row][col].cte*L[0].Tg+L[0].section[row][col].cte2*(260-L[0].Tg))/260, 260])


        for i in range(model.n-1):
            L.append(Layer('Cu', 0.001*float(list_Thickness[2*i+1].get()), float(list_Modulus[2*i+1].get()), float(list_CTE[2*i+1].get()), float(list_Poisson[2*i+1].get()), float(list_Density[2*i+1].get()), list_Fill[i].get(), model.row, model.col))
            with open(model.folder+'/L'+str(i+1)+'.txt') as f:
                for row in range(model.row):
                    text=''
                    text=f.readline().split()
                    for col in range(model.col):
                        try:
                            if (float(text[col])<0)|(float(text[col])>100):
                                messagebox.showwarning(title="error",message="invalid data : portion(L"+str(i+1)+')')
                                return
                        except:
                            messagebox.showwarning(title="error",message="invalid data : portion(L"+str(i+1)+')')
                            return
                        L[2*i+1].section[row][col].portion=float(text[col])*0.01
            L.append(Layer('PPG', 0.001*float(list_Thickness[2*i+2].get()), float(list_Modulus[2*i+2].get()), float(list_CTE[2*i+2].get()), float(list_Poisson[2*i+2].get()), float(list_Density[2*i+2].get())))
            L[2*i+2].modulus2=float(df.iloc[int(list_No[2*i+2]['text'])].values[8]) * 1000
            L[2*i+2].cte2=float(df.iloc[int(list_No[2*i+2]['text'])].values[6])
            L[2*i+2].Tg=float(df.iloc[int(list_No[2*i+2]['text'])].values[9])

            if L[2*i+2].Tg>=255:
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus, L[2*i+2].poisson, 25])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus-10**(int(math.log10(L[2*i+2].modulus))-1), L[2*i+2].poisson, 250])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2, L[2*i+2].poisson, 260])

                L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
            else:
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus, L[2*i+2].poisson, 25])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus-10**(int(math.log10(L[2*i+2].modulus))-1), L[2*i+2].poisson, L[2*i+2].Tg-5])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2+10**(int(math.log10(L[2*i+2].modulus2))-1), L[2*i+2].poisson, L[2*i+2].Tg+5])
                L[2*i+2].unit.Elastic.append([L[2*i+2].modulus2, L[2*i+2].poisson, 260])

                if L[2*i+2].Tg<200:
                    L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(200-L[2*i+2].Tg))/200, 200])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(260-L[2*i+2].Tg))/260, 260])
                else:
                    L[2*i+2].unit.Expansion.append([L[2*i+2].cte, L[2*i+2].Tg])
                    L[2*i+2].unit.Expansion.append([(L[2*i+2].cte*L[2*i+2].Tg+L[2*i+2].cte2*(260-L[2*i+2].Tg))/260, 260])

        L.append(Layer('Cu', 0.001*float(list_Thickness[2*model.n-1].get()), float(list_Modulus[2*model.n-1].get()), float(list_CTE[2*model.n-1].get()), float(list_Poisson[2*model.n-1].get()), float(list_Density[2*model.n-1].get()), list_Fill[model.n-1].get(), model.row, model.col))
        with open(model.folder+'/L'+str(model.n)+'.txt') as f:
            for row in range(model.row):
                text=''
                text=f.readline().split()
                for col in range(model.col):
                    try:
                        if (float(text[col])<0)|(float(text[col])>100):
                            messagebox.showwarning(title="error",message="invalid data : portion(L"+str(model.n)+')')
                            return
                    except:
                        messagebox.showwarning(title="error",message="invalid data : portion(L"+str(model.n)+')')
                        return
                    L[2*model.n-1].section[row][col].portion=float(text[col])*0.01

        L.append(Layer('SR', 0.001*float(list_Thickness[2*model.n].get()), float(list_Modulus[2*model.n].get()), float(list_CTE[2*model.n].get()), float(list_Poisson[2*model.n].get()), float(list_Density[2*model.n].get()), row=model.row, col=model.col))
        
        L[2*model.n].modulus2=float(df.iloc[int(list_No[2*model.n]['text'])].values[8]) * 1000
        L[2*model.n].cte2=float(df.iloc[int(list_No[2*model.n]['text'])].values[6])
        L[2*model.n].Tg=float(df.iloc[int(list_No[2*model.n]['text'])].values[9])
        
        with open(model.folder+'/SR_btm.txt') as f:
            for row in range(model.row):
                text=''
                text=f.readline().split()
                for col in range(model.col):
                    try:
                        if (float(text[col])<0)|(float(text[col])>100):
                            messagebox.showwarning(title="error",message="invalid data : portion(SR_btm)")
                            return
                    except:
                        messagebox.showwarning(title="error",message="invalid data : portion(SR_btm)")
                        return
                    L[2*model.n].section[row][col].portion=float(text[col])*0.01
                    if(L[2*model.n].section[row][col].portion)==0: #air
                        L[2*model.n].section[row][col].modulus=0.0001
                        L[2*model.n].section[row][col].cte=0.001
                        L[2*model.n].section[row][col].poisson=0.001
                        L[2*model.n].section[row][col].density=0.00118

                        L[2*model.n].section[row][col].modulus2=0.0001
                        L[2*model.n].section[row][col].cte2=0.001

                        L[2*model.n].section[row][col].Elastic.append([L[2*model.n].section[row][col].modulus, L[2*model.n].section[row][col].poisson, 300])
                        L[2*model.n].section[row][col].Expansion.append([L[2*model.n].section[row][col].cte, 300])
                    else:
                        L[2*model.n].section[row][col].modulus=L[2*model.n].modulus * L[2*model.n].section[row][col].portion
                        L[2*model.n].section[row][col].cte=L[2*model.n].cte
                        L[2*model.n].section[row][col].poisson=L[2*model.n].poisson * L[2*model.n].section[row][col].portion
                        L[2*model.n].section[row][col].density=L[2*model.n].density * L[2*model.n].section[row][col].portion

                        L[2*model.n].section[row][col].modulus2=L[2*model.n].modulus2 * L[2*model.n].section[row][col].portion
                        L[2*model.n].section[row][col].cte2=L[2*model.n].cte2

                        if L[2*model.n].Tg>=255:
                            L[2*model.n].section[row][col].Elastic.append([L[2*model.n].section[row][col].modulus, L[2*model.n].section[row][col].poisson, 25])
                            L[2*model.n].section[row][col].Elastic.append([L[2*model.n].section[row][col].modulus-10**(int(math.log10(L[2*model.n].section[row][col].modulus))-1), L[2*model.n].section[row][col].poisson, 250])
                            L[2*model.n].section[row][col].Elastic.append([L[2*model.n].section[row][col].modulus2, L[2*model.n].section[row][col].poisson, 260])

                            L[2*model.n].section[row][col].Expansion.append([L[2*model.n].section[row][col].cte, L[2*model.n].Tg])
                        else:
                            L[2*model.n].section[row][col].Elastic.append([L[2*model.n].section[row][col].modulus, L[2*model.n].section[row][col].poisson, 25])
                            L[2*model.n].section[row][col].Elastic.append([L[2*model.n].section[row][col].modulus-10**(int(math.log10(L[2*model.n].section[row][col].modulus))-1), L[2*model.n].section[row][col].poisson, L[2*model.n].Tg-5])
                            L[2*model.n].section[row][col].Elastic.append([L[2*model.n].section[row][col].modulus2+10**(int(math.log10(L[2*model.n].section[row][col].modulus2))-1), L[2*model.n].section[row][col].poisson, L[2*model.n].Tg+5])
                            L[2*model.n].section[row][col].Elastic.append([L[2*model.n].section[row][col].modulus2, L[2*model.n].section[row][col].poisson, 260])

                            if L[2*model.n].Tg<200:
                                L[2*model.n].section[row][col].Expansion.append([L[2*model.n].section[row][col].cte, L[2*model.n].Tg])
                                L[2*model.n].section[row][col].Expansion.append([(L[2*model.n].section[row][col].cte*L[2*model.n].Tg+L[2*model.n].section[row][col].cte2*(200-L[2*model.n].Tg))/200, 200])
                                L[2*model.n].section[row][col].Expansion.append([(L[2*model.n].section[row][col].cte*L[2*model.n].Tg+L[2*model.n].section[row][col].cte2*(260-L[2*model.n].Tg))/260, 260])
                            else:
                                L[2*model.n].section[row][col].Expansion.append([L[2*model.n].section[row][col].cte, L[2*model.n].Tg])
                                L[2*model.n].section[row][col].Expansion.append([(L[2*model.n].section[row][col].cte*L[2*model.n].Tg+L[2*model.n].section[row][col].cte2*(260-L[2*model.n].Tg))/260, 260])
        
        for i in range(model.n):
            for row in range(model.row):
                for col in range(model.col):
                    if L[2*i+1].fill=='up':
                        L[2*i+1].section[row][col].modulus = L[2*i+1].modulus * L[2*i+1].section[row][col].portion + L[2*i].modulus * (1-L[2*i+1].section[row][col].portion)
                        L[2*i+1].section[row][col].cte = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].section[row][col].portion + L[2*i].cte * L[2*i].modulus * (1-L[2*i+1].section[row][col].portion)) / L[2*i+1].section[row][col].modulus
                        L[2*i+1].section[row][col].poisson = L[2*i+1].poisson * L[2*i+1].section[row][col].portion + L[2*i].poisson * (1-L[2*i+1].section[row][col].portion)
                        L[2*i+1].section[row][col].density = L[2*i+1].density * L[2*i+1].section[row][col].portion + L[2*i].density * (1-L[2*i+1].section[row][col].portion)

                        L[2*i+1].section[row][col].modulus2 = L[2*i+1].modulus * L[2*i+1].section[row][col].portion + L[2*i].modulus2 * (1-L[2*i+1].section[row][col].portion)
                        L[2*i+1].section[row][col].cte2 = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].section[row][col].portion + L[2*i].cte2 * L[2*i].modulus2 * (1-L[2*i+1].section[row][col].portion)) / L[2*i+1].section[row][col].modulus2

                        if L[2*i].Tg>=255:
                            L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus, L[2*i+1].section[row][col].poisson, 25])
                            #L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus-10**(int(math.log10(L[2*i+1].section[row][col].modulus))-1), L[2*i+1].section[row][col].poisson, 250])
                            L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus2, L[2*i+1].section[row][col].poisson, 260])

                            L[2*i+1].section[row][col].Expansion.append([L[2*i+1].section[row][col].cte, L[2*i].Tg])
                        else:
                            L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus, L[2*i+1].section[row][col].poisson, 25])
                            #L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus-10**(int(math.log10(L[2*i+1].section[row][col].modulus))-1), L[2*i+1].section[row][col].poisson, L[2*i].Tg-5])
                            #L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus2+10**(int(math.log10(L[2*i+1].section[row][col].modulus2))-1), L[2*i+1].section[row][col].poisson, L[2*i].Tg+5])
                            L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus2, L[2*i+1].section[row][col].poisson, 260])

                            if L[2*i].Tg<200:
                                L[2*i+1].section[row][col].Expansion.append([L[2*i+1].section[row][col].cte, L[2*i].Tg])
                                L[2*i+1].section[row][col].Expansion.append([(L[2*i+1].section[row][col].cte*L[2*i].Tg+L[2*i+1].section[row][col].cte2*(200-L[2*i].Tg))/200, 200])
                                L[2*i+1].section[row][col].Expansion.append([(L[2*i+1].section[row][col].cte*L[2*i].Tg+L[2*i+1].section[row][col].cte2*(260-L[2*i].Tg))/260, 260])
                            else:
                                L[2*i+1].section[row][col].Expansion.append([L[2*i+1].section[row][col].cte, L[2*i].Tg])
                                L[2*i+1].section[row][col].Expansion.append([(L[2*i+1].section[row][col].cte*L[2*i].Tg+L[2*i+1].section[row][col].cte2*(260-L[2*i].Tg))/260, 260])

                    elif L[2*i+1].fill=='down':
                        L[2*i+1].section[row][col].modulus = L[2*i+1].modulus * L[2*i+1].section[row][col].portion + L[2*i+2].modulus * (1-L[2*i+1].section[row][col].portion)
                        L[2*i+1].section[row][col].cte = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].section[row][col].portion + L[2*i+2].cte * L[2*i+2].modulus * (1-L[2*i+1].section[row][col].portion)) / L[2*i+1].section[row][col].modulus
                        L[2*i+1].section[row][col].poisson = L[2*i+1].poisson * L[2*i+1].section[row][col].portion + L[2*i+2].poisson * (1-L[2*i+1].section[row][col].portion)
                        L[2*i+1].section[row][col].density = L[2*i+1].density * L[2*i+1].section[row][col].portion + L[2*i+2].density * (1-L[2*i+1].section[row][col].portion)

                        L[2*i+1].section[row][col].modulus2 = L[2*i+1].modulus * L[2*i+1].section[row][col].portion + L[2*i+2].modulus2 * (1-L[2*i+1].section[row][col].portion)
                        L[2*i+1].section[row][col].cte2 = (L[2*i+1].cte * L[2*i+1].modulus * L[2*i+1].section[row][col].portion + L[2*i+2].cte2 * L[2*i+2].modulus2 * (1-L[2*i+1].section[row][col].portion)) / L[2*i+1].section[row][col].modulus2

                        if L[2*i+2].Tg>=255:
                            L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus, L[2*i+1].section[row][col].poisson, 25])
                            #L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus-10**(int(math.log10(L[2*i+1].section[row][col].modulus))-1), L[2*i+1].section[row][col].poisson, 250])
                            L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus2, L[2*i+1].section[row][col].poisson, 260])

                            L[2*i+1].section[row][col].Expansion.append([L[2*i+1].section[row][col].cte, L[2*i+2].Tg])
                        else:
                            L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus, L[2*i+1].section[row][col].poisson, 25])
                            #L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus-10**(int(math.log10(L[2*i+1].section[row][col].modulus))-1), L[2*i+1].section[row][col].poisson, L[2*i+2].Tg-5])
                            #L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus2+10**(int(math.log10(L[2*i+1].section[row][col].modulus2))-1), L[2*i+1].section[row][col].poisson, L[2*i+2].Tg+5])
                            L[2*i+1].section[row][col].Elastic.append([L[2*i+1].section[row][col].modulus2, L[2*i+1].section[row][col].poisson, 260])

                            if L[2*i+2].Tg<200:
                                L[2*i+1].section[row][col].Expansion.append([L[2*i+1].section[row][col].cte, L[2*i+2].Tg])
                                L[2*i+1].section[row][col].Expansion.append([(L[2*i+1].section[row][col].cte*L[2*i+2].Tg+L[2*i+1].section[row][col].cte2*(200-L[2*i+2].Tg))/200, 200])
                                L[2*i+1].section[row][col].Expansion.append([(L[2*i+1].section[row][col].cte*L[2*i+2].Tg+L[2*i+1].section[row][col].cte2*(260-L[2*i+2].Tg))/260, 260])
                            else:
                                L[2*i+1].section[row][col].Expansion.append([L[2*i+1].section[row][col].cte, L[2*i+2].Tg])
                                L[2*i+1].section[row][col].Expansion.append([(L[2*i+1].section[row][col].cte*L[2*i+2].Tg+L[2*i+1].section[row][col].cte2*(260-L[2*i+2].Tg))/260, 260])

        if len(list_Modulus_unit)>0:
            for i in range(len(list_Modulus_unit)):
                list_Modulus_unit[i].grid_forget()
        del list_Modulus_unit[0:]

        if len(list_CTE_unit)>0:
            for i in range(len(list_CTE_unit)):
                list_CTE_unit[i].grid_forget()
        del list_CTE_unit[0:]

        if len(list_Poisson_unit)>0:
            for i in range(len(list_Poisson_unit)):
                list_Poisson_unit[i].grid_forget()
        del list_Poisson_unit[0:]

        if len(list_Density_unit)>0:
            for i in range(len(list_Density_unit)):
                list_Density_unit[i].grid_forget()
        del list_Density_unit[0:]

        if len(list_Modulus_dummy)>0:
            for i in range(len(list_Modulus_dummy)):
                list_Modulus_dummy[i].grid_forget()
        del list_Modulus_dummy[0:]
        
        if len(list_CTE_dummy)>0:
            for i in range(len(list_CTE_dummy)):
                list_CTE_dummy[i].grid_forget()
        del list_CTE_dummy[0:]        
        
        if len(list_Poisson_dummy)>0:
            for i in range(len(list_Poisson_dummy)):
                list_Poisson_dummy[i].grid_forget()
        del list_Poisson_dummy[0:]
        
        if len(list_Density_dummy)>0:
            for i in range(len(list_Density_dummy)):
                list_Density_dummy[i].grid_forget()
        del list_Density_dummy[0:]
        
        messagebox.showwarning(title="type : meshed",message="calculation completed")
    
    label_project.place(x=800, y=10, width=80, height=25)
    entry_project.place(x=880, y=10, width=300, height=25)
    entry_project.delete(0,tk.END)
    now=datetime.now()
    time=now.strftime("%Y%m%d_%H%M")
    if CheckG.get()==0: entry_project.insert(0,time+'_'+cb_customer.get()+'_'+entry_modelname.get()+'_'+str(model.n)+'L_'+cb_structure.get()+'_'+model.type)
    else:  entry_project.insert(0,time+'_'+cb_customer.get()+'_'+entry_modelname.get()+'_'+str(model.n)+'L_'+cb_structure.get()+'_'+model.type+'_Gr')
    
    button_SQBC.place(x=800, y=45, width=70, height=25)
    label_result_SQBC.config(text='')
    label_result_SQBC.place(x=880, y=45, width=240, height=25)
    button_result_SQBC.place_forget()
    check_SQBC.deselect()
    check_SQBC.place_forget()

    button_warpage.place(x=800, y=80, width=70, height=25)
    label_result_warpage.config(text='')
    label_result_warpage.place(x=880, y=80, width=240, height=25)
    button_result_warpage.place_forget()
    check_warpage.deselect()
    check_warpage.place_forget()
    
    button_CTE.place(x=800, y=115, width=70, height=25)
    label_result_CTE.config(text='')
    label_result_CTE.place(x=880, y=115, width=240, height=25)
    button_result_CTE.place_forget()
    check_CTE.deselect()
    check_CTE.place_forget()
    
    button_modulus.place(x=800, y=150, width=70, height=25)
    label_result_modulus.config(text='')
    label_result_modulus.place(x=880, y=150, width=240, height=25)
    button_result_modulus.place_forget()
    check_modulus.deselect()
    check_modulus.place_forget()
    
    label_modeling.place(x=1200, y=10, width=70, height=25)
    button_shell.place(x=1200, y=45, width=70, height=25)
    button_solid.place(x=1200, y=80, width=70, height=25)

    check_gui.select()
    check_job.select()

    check_cpu.place(x=1200, y=120, width=70, height=25)
    check_gui.place(x=1200, y=155, width=70, height=25)
    check_job.place(x=1200, y=190, width=70, height=25)

    button_highT.place(x=1200, y=230, width=70, height=25)

    return

def updatedata():
    for i in range(2*model.n+1):
        try:
            if float(list_Thickness[i].get())<=0:
                messagebox.showwarning(title="error",message="Thickness>0")
                return False
            else: L[i].thickness=float(list_Thickness[i].get())*0.001
        except:
            messagebox.showwarning(title="error",message="invalid data (Thickness)")
            return False
    if model.type!='meshed':
        for i in range(2*model.n+1):
            try:
                if float(list_Modulus_unit[i].get())<=0:
                    messagebox.showwarning(title="error",message="Modulus>0")
                    return False
                else: L[i].unit.modulus=float(list_Modulus_unit[i].get())
                if float(list_CTE_unit[i].get())<=0:
                    messagebox.showwarning(title="error",message="CTE>0")
                    return False
                else: L[i].unit.cte=float(list_CTE_unit[i].get())
                
                if (float(list_Poisson_unit[i].get())<=-1)|(float(list_Poisson_unit[i].get())>=0.5):
                    messagebox.showwarning(title="error",message="Poisson's ratio -1~0.5")
                    return False
                else: L[i].unit.poisson=float(list_Poisson_unit[i].get())
                
                if float(list_Density_unit[i].get())<=0:
                    messagebox.showwarning(title="error",message="Density>0")
                    return False
                else: L[i].unit.density=float(list_Density_unit[i].get())

                if (model.type=='1block')|(model.type=='2block'):
                    if float(list_Modulus_dummy[i].get())<=0:
                        messagebox.showwarning(title="error",message="Modulus>0")
                        return False
                    else: L[i].dummy.modulus=float(list_Modulus_dummy[i].get())

                    if float(list_CTE_dummy[i].get())<=0:
                        messagebox.showwarning(title="error",message="CTE>0")
                        return False
                    else: L[i].dummy.cte=float(list_CTE_dummy[i].get())
                    
                    if (float(list_Poisson_dummy[i].get())<=-1)|(float(list_Poisson_dummy[i].get())>=0.5):
                        messagebox.showwarning(title="error",message="Poisson's ratio -1~0.5")
                        return False
                    else: L[i].dummy.poisson=float(list_Poisson_dummy[i].get())
                    
                    if float(list_Density_dummy[i].get())<=0:
                        messagebox.showwarning(title="error",message="Density>0")
                        return False
                    else: L[i].dummy.density=float(list_Density_dummy[i].get())
            except:
                messagebox.showwarning(title="error",message="invalid data")
                return False
    return True

def btnSQBCClick():

    def capture():
        x1=winSQBC.winfo_rootx()*1.25
        y1=winSQBC.winfo_rooty()*1.25 + 31*1.25
        x2=winSQBC.winfo_width()*1.25 + x1
        y2=winSQBC.winfo_rooty()*1.25 + winSQBC.winfo_height()*1.25
        box=(x1+1,y1+1,x2-1,y2-1)

        img_SQBC=ImageGrab.grab(box)
        img_SQBC.save('D:/AbaqusSim/%s/SQBC/%s_SQBC.png' % (model.project, model.project))
        #img_SQBC.save('D:/AbaqusSim/%s/SQBC/%s_SQBC.png' % (model.project, model.project),"PDF",resolution=100.0,save_all=True)

    if entry_project.get()=='':
        messagebox.showwarning(title="error",message="Enter project name.")
        return
    model.project=entry_project.get()

    if updatedata()==False:
        messagebox.showwarning(title="error",message="Failed to update input data")
        return
    
    if model.type=='unit':    
        del Ls[0:]
        for i in range(2*model.n+1):
            if (i==0): #SR_top
                Ls.append(LayerSQBC(L[i].thickness, L[i].unit.portion, L[i].unit.modulus, L[i].unit.cte, 0.0, '#1ddb16'))
            elif i==2*model.n: #SR_btm
                Ls.append(LayerSQBC(L[i].thickness, L[i].unit.portion, L[i].unit.modulus, L[i].unit.cte, 0.0, '#1ddb16'))
            elif i%2==1: #Cu
                Ls.append(LayerSQBC(L[i].thickness, L[i].unit.portion, L[i].unit.modulus, L[i].unit.cte, 0.0, '#ffbb00', L[i].fill))
            elif i%2==0: #PPG
                if i%4==0: Ls.append(LayerSQBC(L[i].thickness, 0.0, L[i].modulus, L[i].cte, 0.0, '#8c8c8c'))
                else: Ls.append(LayerSQBC(L[i].thickness, 0.0, L[i].modulus, L[i].cte, 0.0, '#c8c8c8'))

    elif (model.type=='1block')|(model.type=='2block'):
        Stotal=model.x*model.y
        Sunit=(model.x-2*model.b-model.c)*(model.y-2*model.a)
        Sdummy=Stotal-Sunit
        Pu=Sunit/Stotal
        Pd=Sdummy/Stotal

        del Ls[0:]
        for i in range(2*model.n+1):
            if (i==0): #SR_top
                portion=L[i].unit.portion*Pu + L[i].dummy.portion*Pd
                modulus=L[i].unit.modulus*Pu + L[i].dummy.modulus*Pd
                cte=(L[i].unit.cte * L[i].unit.modulus * Pu + L[i].dummy.cte * L[i].dummy.modulus * Pd) / modulus
                Ls.append(LayerSQBC(L[i].thickness, portion, modulus, cte, 0.0, '#1ddb16'))
            elif i==2*model.n: #SR_btm
                portion=L[i].unit.portion*Pu + L[i].dummy.portion*Pd
                modulus=L[i].unit.modulus*Pu + L[i].dummy.modulus*Pd
                cte=(L[i].unit.cte * L[i].unit.modulus * Pu + L[i].dummy.cte * L[i].dummy.modulus * Pd) / modulus
                Ls.append(LayerSQBC(L[i].thickness, portion, modulus, cte, 0.0, '#1ddb16'))
            elif i%2==1: #Cu
                portion=L[i].unit.portion*Pu + L[i].dummy.portion*Pd
                modulus=L[i].unit.modulus*Pu + L[i].dummy.modulus*Pd
                cte=(L[i].unit.cte * L[i].unit.modulus * Pu + L[i].dummy.cte * L[i].dummy.modulus * Pd) / modulus
                Ls.append(LayerSQBC(L[i].thickness, portion, modulus, cte, 0.0, '#ffbb00', L[i].fill))
            elif i%2==0: #PPG
                if i%4==0: Ls.append(LayerSQBC(L[i].thickness, 0.0, L[i].modulus, L[i].cte, 0.0, '#8c8c8c'))
                else: Ls.append(LayerSQBC(L[i].thickness, 0.0, L[i].modulus, L[i].cte, 0.0, '#c8c8c8'))

    elif model.type=='meshed':    
        del Ls[0:]
        for i in range(2*model.n+1):
            if (i==0)|(i==2*model.n)|(i%2==1):
                portion=0.0
                modulus=0.0
                cte=0.0
                for row in range(model.row):
                    for col in range(model.col):
                        portion=portion+L[i].section[row][col].portion
                        modulus=modulus+L[i].section[row][col].modulus
                        cte=cte + L[i].section[row][col].cte * L[i].section[row][col].modulus
                portion=portion/(model.row*model.col)
                cte=cte/modulus
                modulus=modulus/(model.row*model.col)
                
            if (i==0): #SR_top
                Ls.append(LayerSQBC(L[i].thickness, portion, modulus, cte, 0.0, '#1ddb16'))
            elif i==2*model.n: #SR_btm
                Ls.append(LayerSQBC(L[i].thickness, portion, modulus, cte, 0.0, '#1ddb16'))
            elif i%2==1: #Cu
                Ls.append(LayerSQBC(L[i].thickness, portion, modulus, cte, 0.0, '#ffbb00', L[i].fill))
            elif i%2==0: #PPG
                if i%4==0: Ls.append(LayerSQBC(L[i].thickness, 0.0, L[i].modulus, L[i].cte, 0.0, '#8c8c8c'))
                else: Ls.append(LayerSQBC(L[i].thickness, 0.0, L[i].modulus, L[i].cte, 0.0, '#c8c8c8'))
    
    if os.path.exists('D:/AbaqusSim')==False:
        os.mkdir('D:/AbaqusSim')
    
    if os.path.exists('D:/AbaqusSim/%s' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s' % model.project)
    
    if os.path.exists('D:/AbaqusSim/%s/SQBC' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s/SQBC' % model.project)
    
    SaveInput('D:/AbaqusSim/%s/SQBC' % model.project)

    winSQBC=tk.Toplevel(win, bg='white')
    winSQBC.title('SQBC')
    winSQBC.geometry("700x470+150+70")

    button_capture_SQBC=tk.Button(winSQBC,text="capture",command=capture)
    button_capture_SQBC.place(x=325,y=5,width=50,height=25)

    label_title_SQBC=tk.Label(winSQBC,text="%s SQBC result" % (model.project), bg='white')
    label_title_SQBC.place(x=50,y=50,width=600,height=25)

    label_NA=tk.Label(winSQBC, text="NA from top : ", anchor='w', bg='white')
    label_ttot=tk.Label(winSQBC, text="total thickness : ", anchor='w', bg='white')
    label_NAttot=tk.Label(winSQBC, text="NA/total thickness : ", anchor='w', bg='white')
    label_Modulus_upper=tk.Label(winSQBC, text="Modulus upper : ", anchor='w', bg='white')
    label_Modulus_lower=tk.Label(winSQBC, text="Modulus lower : ", anchor='w', bg='white')
    label_CTE_upper=tk.Label(winSQBC, text="CTE upper : ", anchor='w', bg='white')
    label_CTE_lower=tk.Label(winSQBC, text="CTE lower : ", anchor='w', bg='white')
    label_delta_CTE=tk.Label(winSQBC, text="ΔCTE : ", anchor='w', bg='white')
    label_warpage=tk.Label(winSQBC, text="warpage : ", anchor='w', bg='white')
    label_description=tk.Label(winSQBC, text="(ΔCTE>0 : smile, ΔCTE<0 : crying)", anchor='w', bg='white')
    
    label_vNA=tk.Label(winSQBC, anchor='w', bg='white')
    label_vttot=tk.Label(winSQBC, anchor='w', bg='white')
    label_vNAttot=tk.Label(winSQBC, anchor='w', bg='white')
    label_vModulus_upper=tk.Label(winSQBC, anchor='w', bg='white')
    label_vModulus_lower=tk.Label(winSQBC, anchor='w', bg='white')
    label_vCTE_upper=tk.Label(winSQBC, anchor='w', bg='white')
    label_vCTE_lower=tk.Label(winSQBC, anchor='w', bg='white')
    label_vdelta_CTE=tk.Label(winSQBC, anchor='w', bg='white')
    label_vwarpage=tk.Label(winSQBC, anchor='w', bg='white')

    label_NA.place(x=470, y=100, width=120, height=20)
    label_ttot.place(x=470, y=125, width=120, height=20)
    label_NAttot.place(x=470, y=150, width=120, height=20)
    label_Modulus_upper.place(x=470, y=180, width=120, height=20)
    label_Modulus_lower.place(x=470, y=205, width=120, height=20)
    label_CTE_upper.place(x=470, y=235, width=120, height=20)
    label_CTE_lower.place(x=470, y=260, width=120, height=20)
    label_delta_CTE.place(x=470, y=285, width=120, height=20)
    label_warpage.place(x=470, y=320, width=120, height=20)
    
    label_vNA.place(x=590, y=100, width=80, height=20)
    label_vttot.place(x=590, y=125, width=80, height=20)
    label_vNAttot.place(x=590, y=150, width=80, height=20)
    label_vModulus_upper.place(x=590, y=180, width=80, height=20)
    label_vModulus_lower.place(x=590, y=205, width=80, height=20)
    label_vCTE_upper.place(x=590, y=235, width=80, height=20)
    label_vCTE_lower.place(x=590, y=260, width=80, height=20)
    label_vdelta_CTE.place(x=590, y=285, width=80, height=20)
    label_vwarpage.place(x=590, y=320, width=80, height=20)

    label_description.place(x=470, y=345, width=200, height=20)

    canvas=tk.Canvas(winSQBC, relief="solid", bg="white", bd=1)
    w=400
    h=300

    ttot = 0
    for i in range(2*model.n+1):
        ttot = ttot + Ls[i].thickness
    cent = ttot/2
    Ls[0].distance = cent - Ls[0].thickness/2
    for i in range(1,2*model.n+1):
        Ls[i].distance = Ls[i-1].distance - (Ls[i-1].thickness + Ls[i].thickness)/2
    num=0
    den=0
    for i in range(2*model.n+1):
        num = num + Ls[i].Etd()
        den = den + Ls[i].Et()
    offset=num/den
    NA=cent-offset

    num = 0
    den = 0
    layer_bot_bound = 0
    layer_top_bound = 0
    for i in range(2*model.n+1):
        layer_bot_bound = layer_bot_bound + Ls[i].thickness
        layer_top_bound = layer_bot_bound - Ls[i].thickness
        if (layer_bot_bound <= NA) & (Ls[i].thickness > 0) :
            num = num + Ls[i].Et()
            den = den + Ls[i].thickness
        elif (layer_bot_bound > NA) & (layer_top_bound < NA) & (Ls[i].thickness > 0) :
            num = num + Ls[i].modulus * (NA - layer_top_bound)
            den = den + (NA - layer_top_bound)
    modulus_upper = num / den

    num = 0
    den = 0
    layer_bot_bound = 0
    layer_top_bound = 0
    for i in range(2*model.n+1):
        layer_bot_bound = layer_bot_bound + Ls[i].thickness
        layer_top_bound = layer_bot_bound - Ls[i].thickness
        if (layer_top_bound < NA) & (layer_bot_bound > NA) & (Ls[i].thickness > 0) :
            num = num + Ls[i].modulus * (layer_bot_bound - NA)
            den = den + (layer_bot_bound - NA)
        elif (layer_top_bound >= NA) & (Ls[i].thickness > 0) :
            num = num + Ls[i].Et()
            den = den + Ls[i].thickness
    modulus_lower = num / den

    num = 0
    den = 0
    layer_bot_bound = 0
    layer_top_bound = 0
    for i in range(2*model.n+1):
        layer_bot_bound = layer_bot_bound + Ls[i].thickness
        layer_top_bound = layer_bot_bound - Ls[i].thickness
        if (layer_bot_bound <= NA) & (Ls[i].thickness > 0) :
            num = num + Ls[i].AEt()
            den = den + Ls[i].Et()
        elif (layer_bot_bound > NA) & (layer_top_bound < NA) & (Ls[i].thickness > 0) :
            num = num + Ls[i].cte * Ls[i].modulus * (NA - layer_top_bound)
            den = den + Ls[i].modulus * (NA - layer_top_bound)
    CTE_upper = num / den

    num = 0
    den = 0
    layer_bot_bound = 0
    layer_top_bound = 0
    for i in range(2*model.n+1):
        layer_bot_bound = layer_bot_bound + Ls[i].thickness
        layer_top_bound = layer_bot_bound - Ls[i].thickness
        if (layer_top_bound < NA) & (layer_bot_bound > NA) & (Ls[i].thickness > 0) :
            num = num + Ls[i].cte * Ls[i].modulus * (layer_bot_bound - NA)
            den = den + Ls[i].modulus * (layer_bot_bound - NA)
        elif (layer_top_bound >= NA) & (Ls[i].thickness > 0) :
            num = num + Ls[i].AEt()
            den = den + Ls[i].Et()
    CTE_lower = num / den

    scale = 200/ttot
    t=list()
    for i in range(2*model.n+1):
        t.append(Ls[i].thickness * scale)

    """
    # 2L : Cored | ETS
    # 3L : Coreless_non | Coreless_rev | "ETS
    # 4L : Cored | Coreless_non | Coreless_rev | ETS
    # 5L : Coreless_non | Coreless_rev | ETS
    if n==2:
        if ss=='Cored':
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2], 350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(50,50+t[0]+t[1],350,50+t[0]+t[1]+t[2],fill=PPG1.color,outline=PPG1.color)
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        elif ss=='ETS':
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0],350,50+t[0]+t[1]+t[2],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2], 350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        else:
            return
    
    elif n==3:
        if ss=="Coreless_non":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0]+t[1],350,50+t[0]+t[1]+t[2]+t[3],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3],350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        elif ss=="Coreless_rev":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0]+t[1],350,50+t[0]+t[1]+t[2],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2],350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        elif ss=="ETS":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0],350,50+t[0]+t[1]+t[2],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2],350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        else:
            return
    
    elif n==4:
        if ss=="Cored":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0]+t[1],350,50+t[0]+t[1]+t[2]+t[3],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3],350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=PPG3.color,outline=PPG3.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            canvas.create_rectangle(200-150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 200+150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7],fill=L4.color,outline=L4.color)
            
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="PPG3")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]/2,text="L4 ("+str(round(L4.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        elif ss=="Coreless_non":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0]+t[1],350,50+t[0]+t[1]+t[2]+t[3],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=PPG3.color,outline=PPG3.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            canvas.create_rectangle(200-150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 200+150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7],fill=L4.color,outline=L4.color)
            
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="PPG3")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]/2,text="L4 ("+str(round(L4.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        elif ss=="Coreless_rev":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0]+t[1],350,50+t[0]+t[1]+t[2],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2],350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=PPG3.color,outline=PPG3.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            canvas.create_rectangle(200-150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 200+150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7],fill=L4.color,outline=L4.color)
            
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="PPG3")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]/2,text="L4 ("+str(round(L4.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        elif ss=="ETS":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0],350,50+t[0]+t[1]+t[2],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2],350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=PPG3.color,outline=PPG3.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            canvas.create_rectangle(200-150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 200+150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7],fill=L4.color,outline=L4.color)
            
            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="PPG3")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]/2,text="L4 ("+str(round(L4.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        else:
            return
    elif n==5:
        if ss=="Coreless_non":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0]+t[1],350,50+t[0]+t[1]+t[2]+t[3],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=PPG3.color,outline=PPG3.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=PPG4.color,outline=PPG4.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            canvas.create_rectangle(200-150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 200+150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7],fill=L4.color,outline=L4.color)
            canvas.create_rectangle(200-150*L5.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 200+150*L5.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9],fill=L5.color,outline=L5.color)

            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="PPG3")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]/2,text="L4 ("+str(round(L4.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]/2,text="PPG4")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]/2,text="L5 ("+str(round(L5.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        elif ss=="Coreless_rev":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0]+t[1],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0]+t[1],350,50+t[0]+t[1]+t[2]+t[3],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3],350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=PPG3.color,outline=PPG3.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=PPG4.color,outline=PPG4.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            canvas.create_rectangle(200-150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 200+150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7],fill=L4.color,outline=L4.color)
            canvas.create_rectangle(200-150*L5.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 200+150*L5.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9],fill=L5.color,outline=L5.color)

            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="PPG3")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]/2,text="L4 ("+str(round(L4.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]/2,text="PPG4")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]/2,text="L5 ("+str(round(L5.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        elif ss=="ETS":
            canvas.create_rectangle(50,50, 50+150*SR_top.portion,50+t[0],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(350-150*SR_top.portion,50, 350,50+t[0],fill=SR_top.color,outline=SR_top.color)
            canvas.create_rectangle(50,50+t[0],350,50+t[0]+t[1]+t[2],fill=PPG1.color,outline=PPG1.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2],350,50+t[0]+t[1]+t[2]+t[3]+t[4],fill=PPG2.color,outline=PPG2.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],fill=PPG3.color,outline=PPG3.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6],350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8],fill=PPG4.color,outline=PPG4.color)
            canvas.create_rectangle(50,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 50+150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(350-150*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 350,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10],fill=SR_btm.color,outline=SR_btm.color)
            canvas.create_rectangle(200-150*L1.portion,50+t[0], 200+150*L1.portion,50+t[0]+t[1],fill=L1.color,outline=L1.color)
            canvas.create_rectangle(200-150*L2.portion,50+t[0]+t[1]+t[2], 200+150*L2.portion,50+t[0]+t[1]+t[2]+t[3],fill=L2.color,outline=L2.color)
            canvas.create_rectangle(200-150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4], 200+150*L3.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5],fill=L3.color,outline=L3.color)
            canvas.create_rectangle(200-150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6], 200+150*L4.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7],fill=L4.color,outline=L4.color)
            canvas.create_rectangle(200-150*L5.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8], 200+150*L5.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9],fill=L5.color,outline=L5.color)

            canvas.create_text(50+75*SR_top.portion,50+t[0]/2,text="SR top ("+str(round(SR_top.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]/2,text="L1 ("+str(round(L1.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]/2,text="PPG1")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]/2,text="L2 ("+str(round(L2.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]/2,text="PPG2")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]/2,text="L3 ("+str(round(L3.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]/2,text="PPG3")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]/2,text="L4 ("+str(round(L4.portion*100,0))+'%)')
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]/2,text="PPG4")
            canvas.create_text(200,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]/2,text="L5 ("+str(round(L5.portion*100,0))+'%)')
            canvas.create_text(50+75*SR_btm.portion,50+t[0]+t[1]+t[2]+t[3]+t[4]+t[5]+t[6]+t[7]+t[8]+t[9]+t[10]/2,text="SR btm ("+str(round(SR_btm.portion*100,0))+'%)')
        else:
            return
    """
    
    canvas.create_line(50,50,350,50,350,250,50,250,50,50,fill="black") #structure
        
    dy=0
    for i in range(2*model.n):
        dy=dy+t[i]
        canvas.create_line(50,50+dy,350,50+dy,fill="black")
    

    label_dNA=tk.Label(winSQBC, text="NA (Neutral Axis, 중립축) : "+str(round(NA,3)), bg='white', anchor='w', fg='red')
    label_dCA=tk.Label(winSQBC, text="CA (Central Axis, 중심축) : "+str(round(ttot/2,3)), bg='white', anchor='w', fg='blue')

    canvas.create_line(0,50+NA*scale,w,50+NA*scale,fill="red") #NA
    canvas.create_line(0,h/2,w,h/2,fill="blue",dash=(2,1)) #CA

    if NA<=(ttot/2):
        canvas.create_text(w-15,50+NA*scale-10,text="NA",fill='red')
        canvas.create_text(0+15,h/2+10,text="CA",fill='blue')
        label_dNA.place(x=130, y=100+h+5, width=280, height=20)
        label_dCA.place(x=130, y=100+h+5+20+3, width=280, height=20)
    else:
        canvas.create_text(w-15,50+NA*scale+10,text="NA",fill='red')
        canvas.create_text(0+15,h/2-10,text="CA",fill='blue')
        label_dCA.place(x=130, y=100+h+5, width=280, height=20)
        label_dNA.place(x=130, y=100+h+5+20+3, width=280, height=20)

    canvas.place(x=25, y=100, width=w, height=h)

    if CTE_upper>CTE_lower: sc="smile"
    elif CTE_upper<CTE_lower: sc="crying"
    else : sc="flat"

    label_vNA.config(text=str(round(NA,3)))
    label_vttot.config(text=str(round(ttot,3)))
    label_vNAttot.config(text=str(round(NA/ttot,4)))
    label_vModulus_upper.config(text=str(round(modulus_upper*0.001,2))+' GPa')
    label_vModulus_lower.config(text=str(round(modulus_lower*0.001,2))+' GPa')
    label_vCTE_upper.config(text=str(round(CTE_upper,3)))
    label_vCTE_lower.config(text=str(round(CTE_lower,3)))
    label_vdelta_CTE.config(text=str(round(CTE_upper-CTE_lower,3)))
    label_vwarpage.config(text=sc)

    label_result_SQBC.config(text='E('+str(round(modulus_upper*0.001,2))+'/'+str(round(modulus_lower*0.001,2))+'), α('+str(round(CTE_upper,2))+'/'+str(round(CTE_lower,2))+'), '+sc)
    button_result_SQBC.place(x=1130, y=45, width=40, height=25)
    check_SQBC.place(x=1180, y=45, width=15, height=25)

    try:
        f=open('D:/AbaqusSim/%s/SQBC/%s_SQBC_result.txt' % (model.project, model.project),'w')
    except:
        messagebox.showwarning(title="error",message="Failed to open result file")
        return
    f.write('NA from top : %s\n' % str(round(NA,3)))
    f.write('total thickness : %s\n' % str(round(ttot,3)))
    f.write('NA/total : %s\n' % str(round(NA/ttot,4)))
    f.write('Modulus upper[GPa] : %s\n' % str(round(modulus_upper*0.001,2)))
    f.write('Modulus lower[GPa] : %s\n' % str(round(modulus_lower*0.001,2)))
    f.write('CTE upper : %s\n' % str(round(CTE_upper,3)))
    f.write('CTE lower : %s\n' % str(round(CTE_lower,3)))
    f.write('ΔCTE : %s\n' % str(round(CTE_upper-CTE_lower,3)))
    f.write('warpage : %s\n' % (sc))
    f.close()

def btnResultSQBCClick():
    try:
        f=open('D:/AbaqusSim/%s/SQBC/%s_SQBC_result.txt' % (model.project, model.project),'r')
    except:
        messagebox.showwarning(title="error",message="Failed to open result file")
        return

    winSQBC=tk.Toplevel(win, bg='white')
    winSQBC.title('SQBC result')
    winSQBC.geometry("700x470+150+70")

    label_title_SQBC=tk.Label(winSQBC,text="%s SQBC result" % (model.project), bg='white')
    label_title_SQBC.place(x=50,y=50,width=600,height=25)

    label_NA=tk.Label(winSQBC, text="NA from top : ", anchor='w', bg='white')
    label_ttot=tk.Label(winSQBC, text="total thickness : ", anchor='w', bg='white')
    label_NAttot=tk.Label(winSQBC, text="NA/total thickness : ", anchor='w', bg='white')
    label_Modulus_upper=tk.Label(winSQBC, text="Modulus upper : ", anchor='w', bg='white')
    label_Modulus_lower=tk.Label(winSQBC, text="Modulus lower : ", anchor='w', bg='white')
    label_CTE_upper=tk.Label(winSQBC, text="CTE upper : ", anchor='w', bg='white')
    label_CTE_lower=tk.Label(winSQBC, text="CTE lower : ", anchor='w', bg='white')
    label_delta_CTE=tk.Label(winSQBC, text="ΔCTE : ", anchor='w', bg='white')
    label_warpage=tk.Label(winSQBC, text="warpage : ", anchor='w', bg='white')
    label_description=tk.Label(winSQBC, text="(ΔCTE>0 : smile, ΔCTE<0 : crying)", anchor='w', bg='white')
    
    label_vNA=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip(), anchor='w', bg='white')
    label_vttot=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip(), anchor='w', bg='white')
    label_vNAttot=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip(), anchor='w', bg='white')
    label_vModulus_upper=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip()+' GPa', anchor='w', bg='white')
    label_vModulus_lower=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip()+' GPa', anchor='w', bg='white')
    label_vCTE_upper=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip(), anchor='w', bg='white')
    label_vCTE_lower=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip(), anchor='w', bg='white')
    label_vdelta_CTE=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip(), anchor='w', bg='white')
    label_vwarpage=tk.Label(winSQBC, text=f.readline().split(sep=':')[1].strip(), anchor='w', bg='white')

    label_NA.place(x=470, y=100, width=120, height=20)
    label_ttot.place(x=470, y=125, width=120, height=20)
    label_NAttot.place(x=470, y=150, width=120, height=20)
    label_Modulus_upper.place(x=470, y=180, width=120, height=20)
    label_Modulus_lower.place(x=470, y=205, width=120, height=20)
    label_CTE_upper.place(x=470, y=235, width=120, height=20)
    label_CTE_lower.place(x=470, y=260, width=120, height=20)
    label_delta_CTE.place(x=470, y=285, width=120, height=20)
    label_warpage.place(x=470, y=320, width=120, height=20)
    
    label_vNA.place(x=590, y=100, width=80, height=20)
    label_vttot.place(x=590, y=125, width=80, height=20)
    label_vNAttot.place(x=590, y=150, width=80, height=20)
    label_vModulus_upper.place(x=590, y=180, width=80, height=20)
    label_vModulus_lower.place(x=590, y=205, width=80, height=20)
    label_vCTE_upper.place(x=590, y=235, width=80, height=20)
    label_vCTE_lower.place(x=590, y=260, width=80, height=20)
    label_vdelta_CTE.place(x=590, y=285, width=80, height=20)
    label_vwarpage.place(x=590, y=320, width=80, height=20)

    label_description.place(x=470, y=345, width=200, height=20)

    canvas=tk.Canvas(winSQBC, relief="solid", bg="white", bd=1)
    w=400
    h=300
    canvas.create_line(50,50,350,50,350,250,50,250,50,50,fill="black") #structure

    ttot=float(label_vttot['text'])
    NA=float(label_vNA['text'])

    scale = 200/ttot

    dy=0
    for i in range(2*model.n):
        dy=dy+Ls[i].thickness*scale
        canvas.create_line(50,50+dy,350,50+dy,fill="black")
    

    label_dNA=tk.Label(winSQBC, text="NA (Neutral Axis, 중립축) : "+str(round(NA,3)), bg='white', anchor='w', fg='red')
    label_dCA=tk.Label(winSQBC, text="CA (Central Axis, 중심축) : "+str(round(ttot/2,3)), bg='white', anchor='w', fg='blue')

    canvas.create_line(0,50+NA*scale,w,50+NA*scale,fill="red") #NA
    canvas.create_line(0,h/2,w,h/2,fill="blue",dash=(2,1)) #CA

    if NA<=(ttot/2):
        canvas.create_text(w-15,50+NA*scale-10,text="NA",fill='red')
        canvas.create_text(0+15,h/2+10,text="CA",fill='blue')
        label_dNA.place(x=130, y=100+h+5, width=280, height=20)
        label_dCA.place(x=130, y=100+h+5+20+3, width=280, height=20)
    else:
        canvas.create_text(w-15,50+NA*scale+10,text="NA",fill='red')
        canvas.create_text(0+15,h/2-10,text="CA",fill='blue')
        label_dCA.place(x=130, y=100+h+5, width=280, height=20)
        label_dNA.place(x=130, y=100+h+5+20+3, width=280, height=20)

    canvas.place(x=25, y=100, width=w, height=h)
    return

def writescript(): #unit, 1block, 2block, meshed
    try:
        f=open(model.project+'.py','w')
    except:
        return False
    f.write("from abaqus import *\n")
    f.write("from abaqusConstants import *\n")
    f.write("import visualization\n")
    f.write("import interaction\n")
    f.write("backwardCompatibility.setValues(includeDeprecated=True, reportDeprecated=False)\n")
    f.write("import regionToolset\n")
    f.write("import sketch\n")
    f.write("import part\n")

    f.write("myModel = mdb.Model(name='Model-1')\n")

    if model.type=='unit':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #unit
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((0,0,0),)), name='unit')\n")

        f.write("myModel.Material(name='SR_top')\n")
        f.write("myModel.materials['SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='SR_btm')\n")
        f.write("myModel.materials['SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='L%d')\n" % (i+1))
            f.write("myModel.materials['L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))
        
        f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
    
    elif model.type=='1block':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))
        f.write("a=%f\n" % model.a)
        f.write("b=%f\n" % model.b)

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("xyCoordsInner = ((b-x,y-a),(x-b,y-a),(x-b,a-y),(b-x,a-y),(b-x,y-a))\n") #unit
        f.write("xyCoordsOuter = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #dummy
        f.write("for i in range(len(xyCoordsInner)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner[i],point2=xyCoordsInner[i+1])\n")
        f.write("for i in range(len(xyCoordsOuter)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoordsOuter[i],point2=xyCoordsOuter[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((x,y,0),)), name='dummy')\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((0,0,0),)), name='unit')\n")
        
        f.write("mySketch3 = myModel.ConstrainedSketch(name='Sketch C',sheetSize=500.0)\n")
        f.write("mySketch3.Line(point1=(-x,0),point2=(x,0))\n")
        f.write("mySketch3.Line(point1=(0,-y),point2=(0,y))\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch3)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x,y,0),)),sketch=mySketch3)\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x),0.5*(y-a),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x),0.5*(a-y),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(x-b),0.5*(a-y),0),)))\n")

        if CheckG.get()==1:
            f.write("mySketchG = myModel.ConstrainedSketch(name='Sketch G',sheetSize=500.0)\n")
            f.write("xg=%f/2\n" % (model.x*1.5))
            f.write("yg=%f/2\n" % (model.y*1.5))
            f.write("xyCoordsG = ((-xg,yg),(xg,yg),(xg,-yg),(-xg,-yg),(-xg,yg))\n")
            f.write("for i in range(len(xyCoordsG)-1):\n")
            f.write("    mySketchG.Line(point1=xyCoordsG[i],point2=xyCoordsG[i+1])\n")
            f.write("myPartG = myModel.Part(name='Part-2', dimensionality=THREE_D, type=DISCRETE_RIGID_SURFACE)\n")
            f.write("myPartG.BaseShell(sketch=mySketchG)\n")
            f.write("RP=myPartG.ReferencePoint(point=(0,0,0))\n")
        
        f.write("myModel.Material(name='U_SR_top')\n")
        f.write("myModel.materials['U_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['U_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['U_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='U_SR_btm')\n")
        f.write("myModel.materials['U_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['U_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['U_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        f.write("myModel.Material(name='D_SR_top')\n")
        f.write("myModel.materials['D_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].dummy.density))
        f.write("myModel.materials['D_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].dummy.modulus, L[0].dummy.poisson))
        f.write("myModel.materials['D_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].dummy.cte))
        f.write("myModel.Material(name='D_SR_btm')\n")
        f.write("myModel.materials['D_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].dummy.density))
        f.write("myModel.materials['D_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].dummy.modulus, L[2*model.n].dummy.poisson))
        f.write("myModel.materials['D_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].dummy.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='U_L%d')\n" % (i+1))
            f.write("myModel.materials['U_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['U_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['U_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))

            f.write("myModel.Material(name='D_L%d')\n" % (i+1))
            f.write("myModel.materials['D_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].dummy.density))
            f.write("myModel.materials['D_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson))
            f.write("myModel.materials['D_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].dummy.cte))
        
        if CheckG.get()==1:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        else:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        f.write("myPart.compositeLayups['dummy'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['dummy'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
    
    elif model.type=='2block':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))
        f.write("a=%f\n" % model.a)
        f.write("b=%f\n" % model.b)
        f.write("c=%f\n" % (model.c/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("xyCoordsInner1 = ((-c,y-a),(b-x,y-a),(b-x,a-y),(-c,a-y),(-c,y-a))\n") #unit_left
        f.write("xyCoordsInner2 = ((c,y-a),(x-b,y-a),(x-b,a-y),(c,a-y),(c,y-a))\n") #unit_right
        f.write("xyCoordsOuter = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #dummy
        f.write("for i in range(len(xyCoordsInner1)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner1[i],point2=xyCoordsInner1[i+1])\n")
        f.write("for i in range(len(xyCoordsInner2)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner2[i],point2=xyCoordsInner2[i+1])\n")
        f.write("for i in range(len(xyCoordsOuter)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoordsOuter[i],point2=xyCoordsOuter[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((x,y,0),)), name='dummy')\n")
        f.write("myPart.Set(faces=myPart.faces.findAt((((b-x-c)/2,0,0),),(((c+x-b)/2,0,0),)), name='unit')\n")
        
        f.write("mySketch3 = myModel.ConstrainedSketch(name='Sketch C',sheetSize=500.0)\n")
        f.write("mySketch3.Line(point1=(-x,0),point2=(x,0))\n")
        f.write("mySketch3.Line(point1=(0,-y),point2=(0,y))\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt((((b-x-c)/2,0,0),),(((c+x-b)/2,0,0),)),sketch=mySketch3)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x,y,0),)),sketch=mySketch3)\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x-c),0.5*(y-a),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x-c),0.5*(a-y),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(x-b+c),0.5*(a-y),0),)))\n")

        if CheckG.get()==1:
            f.write("mySketchG = myModel.ConstrainedSketch(name='Sketch G',sheetSize=500.0)\n")
            f.write("xg=%f/2\n" % (model.x*1.5))
            f.write("yg=%f/2\n" % (model.y*1.5))
            f.write("xyCoordsG = ((-xg,yg),(xg,yg),(xg,-yg),(-xg,-yg),(-xg,yg))\n")
            f.write("for i in range(len(xyCoordsG)-1):\n")
            f.write("    mySketchG.Line(point1=xyCoordsG[i],point2=xyCoordsG[i+1])\n")
            f.write("myPartG = myModel.Part(name='Part-2', dimensionality=THREE_D, type=DISCRETE_RIGID_SURFACE)\n")
            f.write("myPartG.BaseShell(sketch=mySketchG)\n")
            f.write("RP=myPartG.ReferencePoint(point=(0,0,0))\n")
        
        f.write("myModel.Material(name='U_SR_top')\n")
        f.write("myModel.materials['U_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['U_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['U_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='U_SR_btm')\n")
        f.write("myModel.materials['U_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['U_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['U_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        f.write("myModel.Material(name='D_SR_top')\n")
        f.write("myModel.materials['D_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].dummy.density))
        f.write("myModel.materials['D_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].dummy.modulus, L[0].dummy.poisson))
        f.write("myModel.materials['D_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].dummy.cte))
        f.write("myModel.Material(name='D_SR_btm')\n")
        f.write("myModel.materials['D_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].dummy.density))
        f.write("myModel.materials['D_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].dummy.modulus, L[2*model.n].dummy.poisson))
        f.write("myModel.materials['D_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].dummy.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='U_L%d')\n" % (i+1))
            f.write("myModel.materials['U_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['U_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['U_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))

            f.write("myModel.Material(name='D_L%d')\n" % (i+1))
            f.write("myModel.materials['D_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].dummy.density))
            f.write("myModel.materials['D_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson))
            f.write("myModel.materials['D_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].dummy.cte))
        
        if CheckG.get()==1:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        else:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        f.write("myPart.compositeLayups['dummy'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['dummy'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))

    elif model.type=='meshed':
        f.write("x=%f\n" % model.x)
        f.write("y=%f\n" % model.y)
        f.write("nrow=%d\n" % model.row)
        f.write("ncol=%d\n" % model.col)
        
        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((0,0),(x,0),(x,y),(0,y),(0,0))\n")
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("    mySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")

        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("for i in range(1,ncol):\n")
        f.write("    mySketch2.Line(point1=(i*(x/ncol),0),point2=(i*(x/ncol),y))\n")
        f.write("for i in range(1,nrow):\n")
        f.write("    mySketch2.Line(point1=(0,i*(y/nrow)),point2=(x,i*(y/nrow)))\n")

        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        for i in range(model.row):
            for j in range(model.col):
                f.write("myPart.Set(faces=myPart.faces.findAt(((%f,%f,0),)), name='Set_%d_%d')\n" % (((j+0.5)*(model.x/model.col)),(model.y-(i+0.5)*(model.y/model.row)),i,j))
                f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='Set_%d_%d', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n" % (i,j))
                f.write("myPart.compositeLayups['Set_%d_%d'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n" % (i,j))
                f.write("myPart.compositeLayups['Set_%d_%d'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n" % (i,j))
        
        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
            
        for i in range(model.row):
            for j in range(model.col):
                f.write("myModel.Material(name='SR_top_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_top_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[0].section[i][j].density))
                f.write("myModel.materials['SR_top_%d_%d'].Elastic(table=((%f,%f),))\n" % (i, j, L[0].section[i][j].modulus, L[0].section[i][j].poisson))
                f.write("myModel.materials['SR_top_%d_%d'].Expansion(table=((%fe-06,),))\n" % (i, j, L[0].section[i][j].cte))
                
                f.write("myModel.Material(name='SR_btm_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_btm_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[2*model.n].section[i][j].density))
                f.write("myModel.materials['SR_btm_%d_%d'].Elastic(table=((%f,%f),))\n" % (i, j, L[2*model.n].section[i][j].modulus, L[2*model.n].section[i][j].poisson))
                f.write("myModel.materials['SR_btm_%d_%d'].Expansion(table=((%fe-06,),))\n" % (i, j, L[2*model.n].section[i][j].cte))
                
        for i in range(model.n):    
            for row in range(model.row):
                for col in range(model.col):
                    f.write("myModel.Material(name='L%d_%d_%d')\n" % ((i+1),row,col))
                    f.write("myModel.materials['L%d_%d_%d'].Density(table=((%fe-09,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].density))
                    f.write("myModel.materials['L%d_%d_%d'].Elastic(table=((%f,%f),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].modulus, L[2*i+1].section[row][col].poisson))
                    f.write("myModel.materials['L%d_%d_%d'].Expansion(table=((%fe-06,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].cte))
                    
        for i in range(model.row):
            for j in range(model.col):
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_btm_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,i,j,i,j,L[2*model.n].thickness))
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,model.n,i,j,i,j,L[2*model.n-1].thickness))
                for k in range(model.n-1,0,-1):
                    f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,k,(2*(model.n-k)+1),i,j,L[2*k].thickness))
                    f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,k,i,j,(2*(model.n-k)+2),i,j,L[2*k-1].thickness))
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_top_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,i,j,(2*model.n+1),i,j,L[0].thickness))   

    f.write("myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)\n")
    f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-1-1', part=myPart)\n")
    
    if (CheckG.get()==1): #1block, 2block
        f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-2-1', part=myPartG)\n")
        f.write("myModel.rootAssembly.Set(name='RP', referencePoints=(myModel.rootAssembly.instances['Part-2-1'].referencePoints[RP.id], ))\n")
        
        f.write("myModel.rootAssembly.Surface(name='Ground', side1Faces=myModel.rootAssembly.instances['Part-2-1'].faces.findAt(((0,0,0),)))\n")
        if model.type=='1block': f.write("myModel.rootAssembly.Surface(name='strip', side2Faces=myModel.rootAssembly.instances['Part-1-1'].faces.findAt(((0,0,0),),((x-b/2,0,0),)))\n")
        elif model.type=='2block': f.write("myModel.rootAssembly.Surface(name='strip', side2Faces=myModel.rootAssembly.instances['Part-1-1'].faces.findAt(((0,0,0),),((0.5*(x-b+c),0,0),)))\n")

    if CheckG.get()==1: f.write("myModel.StaticStep(initialInc=0.1, name='Step-1', nlgeom=ON, previous='Initial', maxNumInc=1000000, minInc=1e-12)\n")
    else: f.write("myModel.StaticStep(initialInc=0.1, name='Step-1', nlgeom=ON, previous='Initial', maxNumInc=10000, minInc=1e-08)\n")

    if model.type=='unit':
        f.write("myModel.rootAssembly.Set(name='xyz', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((-x,-y,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='yz', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((x,-y,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='z', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((-x,y,0),)))\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xyz', region=myModel.rootAssembly.sets['xyz'], u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='yz', region=myModel.rootAssembly.sets['yz'], u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='z', region=myModel.rootAssembly.sets['z'], u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    elif model.type=='1block':
        f.write("myModel.rootAssembly.Set(name='xsymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((0,(y-a)/2,0),),((0,y-a/2,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='ysymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt((((x-b)/2,0,0),),((x-b/2,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='center', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")

        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xsymm', region=myModel.rootAssembly.sets['xsymm'], u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=SET, ur3=SET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='ysymm', region=myModel.rootAssembly.sets['ysymm'], u1=UNSET, u2=SET, u3=UNSET, ur1=SET, ur2=UNSET, ur3=SET)\n")
        if (CheckG.get()==1): f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=UNSET, ur1=SET, ur2=SET, ur3=UNSET)\n")
        else: f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)\n")
    elif model.type=='2block':
        f.write("myModel.rootAssembly.Set(name='xsymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((0,(y-a)/2,0),),((0,y-a/2,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='ysymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((c/2,0,0),),(((c+x-b)/2,0,0),),((x-b/2,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='center', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")

        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xsymm', region=myModel.rootAssembly.sets['xsymm'], u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=SET, ur3=SET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='ysymm', region=myModel.rootAssembly.sets['ysymm'], u1=UNSET, u2=SET, u3=UNSET, ur1=SET, ur2=UNSET, ur3=SET)\n")
        if (CheckG.get()==1): f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=UNSET, ur1=SET, ur2=SET, ur3=UNSET)\n")
        else: f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)\n")

    elif model.type=='meshed':
        f.write("myModel.rootAssembly.Set(name='xyz', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='yz', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((x,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='z', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,y,0),)))\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xyz', region=myModel.rootAssembly.sets['xyz'], u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='yz', region=myModel.rootAssembly.sets['yz'], u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='z', region=myModel.rootAssembly.sets['z'], u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    
    f.write("myModel.rootAssembly.Set(name='Set-4', edges=myModel.rootAssembly.instances['Part-1-1'].edges, faces=myModel.rootAssembly.instances['Part-1-1'].faces, vertices=myModel.rootAssembly.instances['Part-1-1'].vertices)\n")
    
    if CheckG.get()==1:
        f.write("myModel.StaticStep(initialInc=0.1, name='Step-2', previous='Step-1')\n")
        f.write("myModel.ContactProperty('IntProp-1')\n")
        f.write("myModel.interactionProperties['IntProp-1'].TangentialBehavior(dependencies=0, directionality=ISOTROPIC, elasticSlipStiffness=None, formulation=PENALTY, fraction=0.005, maximumElasticSlip=FRACTION, pressureDependency=OFF, shearStressLimit=None, slipRateDependency=OFF, table=((0.1, ), ), temperatureDependency=OFF)\n")
        f.write("myModel.SurfaceToSurfaceContactStd(adjustMethod=NONE, clearanceRegion=None, createStepName='Initial', datumAxis=None, initialClearance=OMIT, interactionProperty='IntProp-1', main=myModel.rootAssembly.surfaces['Ground'], name='Int-1', secondary=myModel.rootAssembly.surfaces['strip'], sliding=FINITE, thickness=ON)\n")
        f.write("myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['Part-2-1'].faces.findAt(((0,0,0),)), name='b_Set-6')\n")
        f.write("myModel.RigidBody(bodyRegion=myModel.rootAssembly.sets['b_Set-6'], name='Constraint-1', refPointRegion=myModel.rootAssembly.sets['RP'])\n")
        f.write("myModel.Gravity(comp3=-2000.0, createStepName='Step-1', distributionType=UNIFORM, field='', name='Load-1', region=myModel.rootAssembly.sets['Set-4'])\n")
    
    f.write("myModel.Temperature(createStepName='Initial', crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=UNIFORM, magnitudes=(150.0, ), name='Predefined Field-1', region=myModel.rootAssembly.sets['Set-4'])\n")
    
    if CheckG.get()==1:
        f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(150.0, ), stepName='Step-1')\n")
    else:
        f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(25.0, ), stepName='Step-1')\n")
    
    f.write("myPart.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=%f)\n" %(round(max(model.x,model.y)/100,1)))
    f.write("myPart.generateMesh()\n")

    if CheckG.get()==1:
        f.write("myPartG.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=%f)\n" % (max(model.x,model.y)*1.5))
        f.write("myPartG.generateMesh()\n")
        #f.write("myModel.EncastreBC(createStepName='Initial', localCsys=None, name='RP', region=myModel.rootAssembly.sets['RP'])\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='RP', region=myModel.rootAssembly.sets['RP'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)\n")
        f.write("myModel.StaticStep(name='Step-3', previous='Step-2')\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='center-DISP', region=myModel.rootAssembly.sets['center'], u1=UNSET, u2=UNSET, u3=-0.0001, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='Xsymm-DISP', region=myModel.rootAssembly.sets['xsymm'], u1=UNSET, u2=UNSET, u3=-0.0001, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='Ysymm-DISP', region=myModel.rootAssembly.sets['ysymm'], u1=UNSET, u2=UNSET, u3=-0.0001, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.boundaryConditions['Xsymm-DISP'].deactivate('Step-2')\n")
        f.write("myModel.boundaryConditions['Ysymm-DISP'].deactivate('Step-2')\n")
        f.write("myModel.boundaryConditions['center-DISP'].deactivate('Step-2')\n")
        f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(150.0, ), stepName='Step-2')\n")
        f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(25.0, ), stepName='Step-3')\n")
    
    f.write("myModel.rootAssembly.regenerate()\n")
    f.write("mdb.models.changeKey(fromName='Model-1', toName='POR')\n")
    if CheckCPU.get()==1: cpu=32
    else: cpu=4
    f.write("mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE, model='POR', modelPrint=OFF, multiprocessingMode=DEFAULT, name='POR', nodalOutputPrecision=SINGLE, numCpus=%d, numDomains=%d, numGPUs=0, numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)\n" % (cpu,cpu))
    
    f.write("mdb.saveAs(pathName='%s')\n" % model.project)
    if CheckJob.get()==0: return True
    f.write("mdb.jobs['POR'].submit(consistencyChecking=OFF)\n")
    f.write("mdb.jobs['POR'].waitForCompletion()\n")

    f.write("myViewport=session.Viewport(name='Warpage (%s)',origin=(0,0),width=200,height=130)\n" % (model.project))

    f.write("myOdb=visualization.openOdb(path='POR.odb')\n")
    f.write("myViewport.setValues(displayedObject=myOdb)\n")
    f.write("myViewport.odbDisplay.setPrimaryVariable(variableLabel='U',outputPosition=NODAL,refinement=(COMPONENT,'U3'))\n")
    f.write("myViewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))\n")
    #f.write("myViewport.maximize()\n")
    f.write("myViewport.view.fitView()\n")
    #f.write("session.printOptions.setValues(vpBackground=ON)\n")
    if (model.type=='1block')|(model.type=='2block'):
        f.write("myViewport.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=ON, mirrorAboutYzPlane=ON)\n")
    else:
        f.write("myViewport.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=OFF, mirrorAboutYzPlane=OFF)\n")
    f.write("session.printToFile(fileName='%s_img', format=PNG, canvasObjects=(myViewport,))\n" % model.project)
    
    #
    f.write("f=open('%s_result.txt','w')\n" % model.project)
    f.write("strMinMax=myViewport.getPrimVarMinMaxLoc()\n")
    f.write("f.write(str(strMinMax)+'\\n\\n')\n")
    #f.write("if (strMinMax['minNodeLabel']==1)|(strMinMax['maxNodeLabel']==7): warpage=strMinMax['minValue']-strMinMax['maxValue']\n") #smile -
    #f.write("elif (strMinMax['maxNodeLabel']==1)|(strMinMax['minNodeLabel']==7): warpage=strMinMax['maxValue']-strMinMax['minValue']\n") #crying +
    #f.write("else: warpage=0\n")
    if CheckG.get()==1:
        f.write("fieldValues=myOdb.steps['Step-3'].frames[-1].fieldOutputs['U'].values\n")
    else:
        f.write("fieldValues=myOdb.steps['Step-1'].frames[-1].fieldOutputs['U'].values\n")
    
    if model.type=='unit':
        f.write("for v in fieldValues:\n")
        f.write("    if v.nodeLabel==1: z1=v.data[2]\n")
        f.write("if (z1>((strMinMax['maxValue']+strMinMax['minValue'])/2)): warpage=strMinMax['minValue']-strMinMax['maxValue']; sc='smile'\n")
        f.write("elif (z1<((strMinMax['maxValue']+strMinMax['minValue'])/2)): warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='crying'\n")
        f.write("else: warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='none'\n")
    elif (model.type=='1block')|(model.type=='2block'):
        f.write("for v in fieldValues:\n")
        f.write("    if v.nodeLabel==1: z1=v.data[2]\n")
        f.write("    elif v.nodeLabel==5: z5=v.data[2]\n")
        f.write("    elif v.nodeLabel==6: z6=v.data[2]\n")
        f.write("    elif v.nodeLabel==7: z7=v.data[2]; break\n")
        f.write("if z1<((z5+z6+z7)/3): warpage=strMinMax['minValue']-strMinMax['maxValue']; sc='smile'\n")
        f.write("elif z1>((z5+z6+z7)/3): warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='crying'\n")
        f.write("else: warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='none'\n")
    elif model.type=='meshed':
        f.write("for v in fieldValues:\n")
        f.write("    if v.nodeLabel==3: z3=v.data[2]\n")
        f.write("if (z3>((strMinMax['maxValue']+strMinMax['minValue'])/2)): warpage=strMinMax['minValue']-strMinMax['maxValue']; sc='smile'\n")
        f.write("elif (z3<((strMinMax['maxValue']+strMinMax['minValue'])/2)): warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='crying'\n")
        f.write("else: warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='none'\n")
    f.write("f.write('warpage : '+str(round(warpage,3))+'\\n'+sc)\n")
    f.write("f.close()\n")
    return True

def btnWarpageClick():
    if entry_project.get()=='':
        messagebox.showwarning(title="error",message="Enter project name.")
        return
    model.project=entry_project.get()

    if updatedata()==False:
        messagebox.showwarning(title="error",message="Failed to update input data")
        return

    if os.path.exists('D:/AbaqusSim')==False:
        os.mkdir('D:/AbaqusSim')
    
    if os.path.exists('D:/AbaqusSim/%s' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s' % model.project)
    
    if os.path.exists('D:/AbaqusSim/%s/Warpage' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s/Warpage' % model.project)

    os.chdir('D:/AbaqusSim/%s/Warpage' % model.project)

    SaveInput('D:/AbaqusSim/%s/Warpage' % model.project)

    if writescript()==False:
        messagebox.showwarning(title="error",message="failed to write script (Warpage)")
        return

    if CheckGUI.get()==1: os.system("abaqus cae script=%s.py" % model.project)
    else: os.system("abaqus cae nogui=%s.py" % model.project)

    if CheckJob.get()==1:
        try:
            f=open("D:/AbaqusSim/%s/Warpage/%s_result.txt" % (model.project,model.project),'r')
        except:
            messagebox.showwarning(title="error",message="failed to open result file (Warpage)")
            return
        f.readline()
        f.readline()
        result=f.readline().strip()
        sc=f.readline().strip()
        f.close()
        
        label_result_warpage.config(text=result+' ('+sc+')')
        button_result_warpage.place(x=1130, y=80, width=40, height=25)
        check_warpage.place(x=1180, y=80, width=15, height=25)
    else:
        if CheckGUI.get()==0:
            messagebox.showwarning(title="Warpage", message="modeling completed (Warpage)")

    return

def btnResultWarpageClick():
    try:
        f=open("D:/AbaqusSim/%s/Warpage/%s_result.txt" % (model.project,model.project),'r')
    except:
        messagebox.showwarning(title="error",message="failed to open result file (Warpage)")
        return
    f.readline()
    f.readline()
    result=f.readline().strip()
    sc=f.readline().strip()
    f.close()

    rw=tk.Toplevel(win)
    rw.title(model.project+' warpage')
    rw.geometry("1000x720+50+50")

    if (result=="")|(sc==""):
        label_result=tk.Label(rw, text='failed')
    else:
        label_result=tk.Label(rw, text=result+' ('+sc+')')
    
    global img_result

    img_result=tk.PhotoImage(file="D:/AbaqusSim/%s/Warpage/%s_img.png" % (model.project,model.project))
    label_img=tk.Label(rw, image=img_result)
    label_title=tk.Label(rw, text=model.project+' result')
    label_title.place(x=5, y=5, width=500, height=30)
    
    label_img.place(x=5, y=55, width=900, height=600)
    label_result.place(x=5, y=665, width=500, height=50)

    return


def writescriptCTE(): #unit, 1block, 2block, meshed
    try:
        f=open(model.project+'_CTE.py','w')
    except:
        return False
    
    f.write("from abaqus import *\n")
    f.write("from abaqusConstants import *\n")
    f.write("import visualization\n")
    f.write("import interaction\n")
    f.write("backwardCompatibility.setValues(includeDeprecated=True, reportDeprecated=False)\n")
    f.write("import regionToolset\n")
    f.write("import sketch\n")
    f.write("import part\n")

    f.write("myModel = mdb.Model(name='Model-1')\n")

    if model.type=='unit':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #unit
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((0,0,0),)), name='unit')\n")

        f.write("myModel.Material(name='SR_top')\n")
        f.write("myModel.materials['SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='SR_btm')\n")
        f.write("myModel.materials['SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='L%d')\n" % (i+1))
            f.write("myModel.materials['L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))
        
        f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
    
    elif model.type=='1block':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))
        f.write("a=%f\n" % model.a)
        f.write("b=%f\n" % model.b)

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("xyCoordsInner = ((b-x,y-a),(x-b,y-a),(x-b,a-y),(b-x,a-y),(b-x,y-a))\n") #unit
        f.write("xyCoordsOuter = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #dummy
        f.write("for i in range(len(xyCoordsInner)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner[i],point2=xyCoordsInner[i+1])\n")
        f.write("for i in range(len(xyCoordsOuter)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoordsOuter[i],point2=xyCoordsOuter[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((x,y,0),)), name='dummy')\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((0,0,0),)), name='unit')\n")
        
        f.write("mySketch3 = myModel.ConstrainedSketch(name='Sketch C',sheetSize=500.0)\n")
        f.write("mySketch3.Line(point1=(-x,0),point2=(x,0))\n")
        f.write("mySketch3.Line(point1=(0,-y),point2=(0,y))\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch3)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x,y,0),)),sketch=mySketch3)\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x),0.5*(y-a),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x),0.5*(a-y),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(x-b),0.5*(a-y),0),)))\n")
        
        f.write("myModel.Material(name='U_SR_top')\n")
        f.write("myModel.materials['U_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['U_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['U_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='U_SR_btm')\n")
        f.write("myModel.materials['U_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['U_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['U_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        f.write("myModel.Material(name='D_SR_top')\n")
        f.write("myModel.materials['D_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].dummy.density))
        f.write("myModel.materials['D_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].dummy.modulus, L[0].dummy.poisson))
        f.write("myModel.materials['D_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].dummy.cte))
        f.write("myModel.Material(name='D_SR_btm')\n")
        f.write("myModel.materials['D_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].dummy.density))
        f.write("myModel.materials['D_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].dummy.modulus, L[2*model.n].dummy.poisson))
        f.write("myModel.materials['D_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].dummy.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='U_L%d')\n" % (i+1))
            f.write("myModel.materials['U_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['U_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['U_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))

            f.write("myModel.Material(name='D_L%d')\n" % (i+1))
            f.write("myModel.materials['D_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].dummy.density))
            f.write("myModel.materials['D_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson))
            f.write("myModel.materials['D_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].dummy.cte))
        
        
        f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        f.write("myPart.compositeLayups['dummy'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['dummy'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
    
    elif model.type=='2block':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))
        f.write("a=%f\n" % model.a)
        f.write("b=%f\n" % model.b)
        f.write("c=%f\n" % (model.c/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("xyCoordsInner1 = ((-c,y-a),(b-x,y-a),(b-x,a-y),(-c,a-y),(-c,y-a))\n") #unit_left
        f.write("xyCoordsInner2 = ((c,y-a),(x-b,y-a),(x-b,a-y),(c,a-y),(c,y-a))\n") #unit_right
        f.write("xyCoordsOuter = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #dummy
        f.write("for i in range(len(xyCoordsInner1)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner1[i],point2=xyCoordsInner1[i+1])\n")
        f.write("for i in range(len(xyCoordsInner2)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner2[i],point2=xyCoordsInner2[i+1])\n")
        f.write("for i in range(len(xyCoordsOuter)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoordsOuter[i],point2=xyCoordsOuter[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((x,y,0),)), name='dummy')\n")
        f.write("myPart.Set(faces=myPart.faces.findAt((((b-x-c)/2,0,0),),(((c+x-b)/2,0,0),)), name='unit')\n")
        
        f.write("mySketch3 = myModel.ConstrainedSketch(name='Sketch C',sheetSize=500.0)\n")
        f.write("mySketch3.Line(point1=(-x,0),point2=(x,0))\n")
        f.write("mySketch3.Line(point1=(0,-y),point2=(0,y))\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt((((b-x-c)/2,0,0),),(((c+x-b)/2,0,0),)),sketch=mySketch3)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x,y,0),)),sketch=mySketch3)\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x-c),0.5*(y-a),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x-c),0.5*(a-y),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(x-b+c),0.5*(a-y),0),)))\n")
        
        f.write("myModel.Material(name='U_SR_top')\n")
        f.write("myModel.materials['U_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['U_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['U_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='U_SR_btm')\n")
        f.write("myModel.materials['U_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['U_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['U_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        f.write("myModel.Material(name='D_SR_top')\n")
        f.write("myModel.materials['D_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].dummy.density))
        f.write("myModel.materials['D_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].dummy.modulus, L[0].dummy.poisson))
        f.write("myModel.materials['D_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].dummy.cte))
        f.write("myModel.Material(name='D_SR_btm')\n")
        f.write("myModel.materials['D_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].dummy.density))
        f.write("myModel.materials['D_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].dummy.modulus, L[2*model.n].dummy.poisson))
        f.write("myModel.materials['D_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].dummy.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='U_L%d')\n" % (i+1))
            f.write("myModel.materials['U_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['U_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['U_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))

            f.write("myModel.Material(name='D_L%d')\n" % (i+1))
            f.write("myModel.materials['D_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].dummy.density))
            f.write("myModel.materials['D_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson))
            f.write("myModel.materials['D_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].dummy.cte))
        
        f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        f.write("myPart.compositeLayups['dummy'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['dummy'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))

    elif model.type=='meshed':
        f.write("x=%f\n" % model.x)
        f.write("y=%f\n" % model.y)
        f.write("nrow=%d\n" % model.row)
        f.write("ncol=%d\n" % model.col)
        
        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((0,0),(x,0),(x,y),(0,y),(0,0))\n")
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("    mySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")

        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("for i in range(1,ncol):\n")
        f.write("    mySketch2.Line(point1=(i*(x/ncol),0),point2=(i*(x/ncol),y))\n")
        f.write("for i in range(1,nrow):\n")
        f.write("    mySketch2.Line(point1=(0,i*(y/nrow)),point2=(x,i*(y/nrow)))\n")

        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        for i in range(model.row):
            for j in range(model.col):
                f.write("myPart.Set(faces=myPart.faces.findAt(((%f,%f,0),)), name='Set_%d_%d')\n" % (((j+0.5)*(model.x/model.col)),(model.y-(i+0.5)*(model.y/model.row)),i,j))
                f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='Set_%d_%d', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n" % (i,j))
                f.write("myPart.compositeLayups['Set_%d_%d'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n" % (i,j))
                f.write("myPart.compositeLayups['Set_%d_%d'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n" % (i,j))
        
        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
            
        for i in range(model.row):
            for j in range(model.col):
                f.write("myModel.Material(name='SR_top_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_top_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[0].section[i][j].density))
                f.write("myModel.materials['SR_top_%d_%d'].Elastic(table=((%f,%f),))\n" % (i, j, L[0].section[i][j].modulus, L[0].section[i][j].poisson))
                f.write("myModel.materials['SR_top_%d_%d'].Expansion(table=((%fe-06,),))\n" % (i, j, L[0].section[i][j].cte))
                
                f.write("myModel.Material(name='SR_btm_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_btm_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[2*model.n].section[i][j].density))
                f.write("myModel.materials['SR_btm_%d_%d'].Elastic(table=((%f,%f),))\n" % (i, j, L[2*model.n].section[i][j].modulus, L[2*model.n].section[i][j].poisson))
                f.write("myModel.materials['SR_btm_%d_%d'].Expansion(table=((%fe-06,),))\n" % (i, j, L[2*model.n].section[i][j].cte))
                
        for i in range(model.n):    
            for row in range(model.row):
                for col in range(model.col):
                    f.write("myModel.Material(name='L%d_%d_%d')\n" % ((i+1),row,col))
                    f.write("myModel.materials['L%d_%d_%d'].Density(table=((%fe-09,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].density))
                    f.write("myModel.materials['L%d_%d_%d'].Elastic(table=((%f,%f),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].modulus, L[2*i+1].section[row][col].poisson))
                    f.write("myModel.materials['L%d_%d_%d'].Expansion(table=((%fe-06,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].cte))
                    
        for i in range(model.row):
            for j in range(model.col):
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_btm_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,i,j,i,j,L[2*model.n].thickness))
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,model.n,i,j,i,j,L[2*model.n-1].thickness))
                for k in range(model.n-1,0,-1):
                    f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,k,(2*(model.n-k)+1),i,j,L[2*k].thickness))
                    f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,k,i,j,(2*(model.n-k)+2),i,j,L[2*k-1].thickness))
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_top_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,i,j,(2*model.n+1),i,j,L[0].thickness))   


    f.write("myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)\n")
    f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-1-1', part=myPart)\n")
    f.write("myModel.StaticStep(initialInc=0.1, name='Step-1', nlgeom=ON, previous='Initial', maxNumInc=10000, minInc=1e-08)\n")
    if model.type=='unit':
        f.write("myModel.rootAssembly.Set(name='xy', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((-x,-y,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='y', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((x,-y,0),)))\n")
        #f.write("myModel.rootAssembly.Set(name='z', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((-x,y,0),)))\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xy', region=myModel.rootAssembly.sets['xy'], u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='y', region=myModel.rootAssembly.sets['y'], u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        #f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='z', region=myModel.rootAssembly.sets['z'], u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    elif model.type=='1block':
        f.write("myModel.rootAssembly.Set(name='xsymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((0,(y-a)/2,0),),((0,y-a/2,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='ysymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt((((x-b)/2,0,0),),((x-b/2,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='center', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")

        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xsymm', region=myModel.rootAssembly.sets['xsymm'], u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=SET, ur3=SET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='ysymm', region=myModel.rootAssembly.sets['ysymm'], u1=UNSET, u2=SET, u3=UNSET, ur1=SET, ur2=UNSET, ur3=SET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)\n")
    elif model.type=='2block':
        f.write("myModel.rootAssembly.Set(name='xsymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((0,(y-a)/2,0),),((0,y-a/2,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='ysymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((c/2,0,0),),(((c+x-b)/2,0,0),),((x-b/2,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='center', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")

        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xsymm', region=myModel.rootAssembly.sets['xsymm'], u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=SET, ur3=SET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='ysymm', region=myModel.rootAssembly.sets['ysymm'], u1=UNSET, u2=SET, u3=UNSET, ur1=SET, ur2=UNSET, ur3=SET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)\n")
    elif model.type=='meshed':
        f.write("myModel.rootAssembly.Set(name='xy', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='y', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((x,0,0),)))\n")
        #f.write("myModel.rootAssembly.Set(name='z', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,y,0),)))\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xy', region=myModel.rootAssembly.sets['xy'], u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='y', region=myModel.rootAssembly.sets['y'], u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        #f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='z', region=myModel.rootAssembly.sets['z'], u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    

    f.write("myModel.rootAssembly.Set(name='Set-4', edges=myModel.rootAssembly.instances['Part-1-1'].edges, faces=myModel.rootAssembly.instances['Part-1-1'].faces, vertices=myModel.rootAssembly.instances['Part-1-1'].vertices)\n")

    f.write("myModel.rootAssembly.Set(name='fix', edges=myModel.rootAssembly.instances['Part-1-1'].edges, faces=myModel.rootAssembly.instances['Part-1-1'].faces)\n")
    f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='fix', region=myModel.rootAssembly.sets['fix'], u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    
    f.write("myModel.Temperature(createStepName='Initial', crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=UNIFORM, magnitudes=(25.0, ), name='Predefined Field-1', region=myModel.rootAssembly.sets['Set-4'])\n")
    f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(260.0, ), stepName='Step-1')\n")
    
    f.write("myPart.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=%f)\n" % round(max(model.x,model.y)/100,1))
    f.write("myPart.generateMesh()\n")

    f.write("myModel.rootAssembly.regenerate()\n")
    f.write("mdb.models.changeKey(fromName='Model-1', toName='CTE')\n")

    if CheckCPU.get()==1: cpu=32
    else: cpu=4
    f.write("mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE, model='CTE', modelPrint=OFF, multiprocessingMode=DEFAULT, name='CTE', nodalOutputPrecision=SINGLE, numCpus=%d, numDomains=%d, numGPUs=0, numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)\n" % (cpu,cpu))
    
    f.write("mdb.saveAs(pathName='%s_CTE')\n" % model.project)
    if CheckJob.get()==0: return True
    f.write("mdb.jobs['CTE'].submit(consistencyChecking=OFF)\n")
    f.write("mdb.jobs['CTE'].waitForCompletion()\n")

    f.write("myViewport1=session.Viewport(name='Strain X (%s)',origin=(0,0),width=200,height=130)\n" % model.project)
    f.write("myViewport2=session.Viewport(name='Strain Y (%s)',origin=(0,0),width=200,height=130)\n" % model.project)

    f.write("myOdb=visualization.openOdb(path='CTE.odb')\n")
    f.write("myViewport1.setValues(displayedObject=myOdb)\n")
    f.write("myViewport1.odbDisplay.setPrimaryVariable(variableLabel='U',outputPosition=NODAL,refinement=(COMPONENT,'U1'))\n")
    f.write("myViewport1.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))\n")
    #f.write("myViewport.maximize()\n")
    f.write("myViewport1.view.fitView()\n")
    #f.write("session.printOptions.setValues(vpBackground=ON)\n")
    if (model.type=='1block')|(model.type=='2block'): f.write("myViewport1.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=ON, mirrorAboutYzPlane=ON)\n")
    else: f.write("myViewport1.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=OFF, mirrorAboutYzPlane=OFF)\n")
    f.write("session.printToFile(fileName='%s_CTE_X_img', format=PNG, canvasObjects=(myViewport1,))\n" % model.project)

    f.write("myViewport2.setValues(displayedObject=myOdb)\n")
    f.write("myViewport2.odbDisplay.setPrimaryVariable(variableLabel='U',outputPosition=NODAL,refinement=(COMPONENT,'U2'))\n")
    f.write("myViewport2.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))\n")
    f.write("myViewport2.view.fitView()\n")
    if (model.type=='1block')|(model.type=='2block'): f.write("myViewport2.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=ON, mirrorAboutYzPlane=ON)\n")
    else: f.write("myViewport2.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=OFF, mirrorAboutYzPlane=OFF)\n")
    f.write("session.printToFile(fileName='%s_CTE_Y_img', format=PNG, canvasObjects=(myViewport2,))\n" % model.project)

    f.write("f=open('%s_CTE_result.txt','w')\n" % model.project)

    f.write("strMinMax1=myViewport1.getPrimVarMinMaxLoc()\n")
    f.write("strMinMax2=myViewport2.getPrimVarMinMaxLoc()\n")
    if model.type=='unit':
        f.write("CTE_X=round((strMinMax1['maxValue']/(2*x*235))*1000000,3)\n")
        f.write("CTE_Y=round((strMinMax2['maxValue']/(2*y*235))*1000000,3)\n")
    else:
        f.write("CTE_X=round((strMinMax1['maxValue']/(x*235))*1000000,3)\n")
        f.write("CTE_Y=round((strMinMax2['maxValue']/(y*235))*1000000,3)\n")

    f.write("f.write(str(CTE_X)+'\\n')\n")
    f.write("f.write(str(CTE_Y)+'\\n')\n")
    f.write("f.write('\\n')\n")
    f.write("f.write(str(strMinMax1)+'\\n')\n")
    f.write("f.write(str(strMinMax2)+'\\n')\n")
    f.write("f.close()\n")
    return True


def btnCTEClick():

    if entry_project.get()=='':
        messagebox.showwarning(title="error",message="Enter project name.")
        return
    model.project=entry_project.get()

    if updatedata()==False:
        messagebox.showwarning(title="error",message="Failed to update input data")
        return

    if os.path.exists('D:/AbaqusSim')==False:
        os.mkdir('D:/AbaqusSim')
    
    if os.path.exists('D:/AbaqusSim/%s' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s' % model.project)
    
    if os.path.exists('D:/AbaqusSim/%s/CTE' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s/CTE' % model.project)

    os.chdir('D:/AbaqusSim/%s/CTE' % model.project)

    SaveInput('D:/AbaqusSim/%s/CTE' % model.project)

    if writescriptCTE()==False:
        messagebox.showwarning(title="error",message="failed to write script (CTE)")
        return

    if CheckGUI.get()==1: os.system("abaqus cae script=%s_CTE.py" % model.project)
    else: os.system("abaqus cae nogui=%s_CTE.py" % model.project)

    if CheckJob.get()==1:
        try:
            f=open("D:/AbaqusSim/%s/CTE/%s_CTE_result.txt" % (model.project,model.project),'r')
        except:
            messagebox.showwarning(title="error",message="failed to open result file (CTE)")
            return
        
        CTE_X=f.readline().strip()
        CTE_Y=f.readline().strip()
        
        f.close()
        
        label_result_CTE.config(text='CTE_X='+CTE_X+', CTE_Y='+CTE_Y)
        button_result_CTE.place(x=1130, y=115, width=40, height=25)
        check_CTE.place(x=1180, y=115, width=15, height=25)
    else:
        if CheckGUI.get()==0:
            messagebox.showwarning(title="CTE", message="modeling completed (CTE)")
    
    return

def btnResultCTEClick():
    try:
        f=open("D:/AbaqusSim/%s/CTE/%s_CTE_result.txt" % (model.project,model.project),'r')
    except:
        messagebox.showwarning(title="error",message="failed to open result file (CTE)")
        return
    result1=f.readline()
    result2=f.readline()
    f.close()

    rw=tk.Toplevel(win)
    rw.title(model.project+' CTE')
    rw.geometry("1230x550+50+60")

    label_title=tk.Label(rw, text=model.project+' CTE result')
    label_result1=tk.Label(rw, text='CTE_X='+result1)
    label_result2=tk.Label(rw, text='CTE_Y='+result2)
    
    global img_result1, img_result2, img_result1r, img_result2r

    img_result1=Image.open("D:/AbaqusSim/%s/CTE/%s_CTE_X_img.png" % (model.project, model.project))
    img_result1=img_result1.resize((600,388), PIL.Image.LANCZOS)
    img_result1r=ImageTk.PhotoImage(img_result1)
    label_img1=tk.Label(rw, image=img_result1r)
    img_result2=Image.open("D:/AbaqusSim/%s/CTE/%s_CTE_Y_img.png" % (model.project, model.project))
    img_result2=img_result2.resize((600,388), PIL.Image.LANCZOS)
    img_result2r=ImageTk.PhotoImage(img_result2)
    label_img2=tk.Label(rw, image=img_result2r)

    label_title.place(x=50, y=5, width=500, height=30)
    label_img1.place(x=10, y=50, width=600, height=388)
    label_img2.place(x=620, y=50, width=600, height=388)
    label_result1.place(x=10, y=450, width=600, height=50)
    label_result2.place(x=620, y=450, width=600, height=50)

    return

def writescriptModulus(): #unit
    try:
        f=open(model.project+'_Modulus.py','w')
    except:
        return False
    f.write("from abaqus import *\n")
    f.write("from abaqusConstants import *\n")
    f.write("import visualization\n")
    f.write("import interaction\n")
    f.write("backwardCompatibility.setValues(includeDeprecated=True, reportDeprecated=False)\n")
    f.write("import regionToolset\n")
    f.write("import sketch\n")
    f.write("import part\n")
    f.write("import mesh\n") #mesh.ElemType

    f.write("myModel = mdb.Model(name='Model-1')\n")

    f.write("x=%f\n" % (model.x/2))
    f.write("y=%f\n" % (model.y/2))

    f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
    f.write("xyCoords = ((0,0),(x,0),(x,y),(0,y),(0,0))\n")
    f.write("for i in range(len(xyCoords)-1):\n")
    f.write("    mySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")
    f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
    f.write("mySketch2.Line(point1=(x/2,0),point2=(x/2,y))\n")
    f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")

    ttot=0
    for i in range(2*model.n+1):
        ttot=ttot+L[i].thickness

    f.write("myPart.BaseSolidExtrude(depth=%f, sketch=mySketch)\n" % ttot)
    f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x/2,y/2,0),)),sketch=mySketch2)\n") #fix

    temp=0
    for i in range(2*model.n):
        temp=temp+L[i].thickness
        f.write("myPart.PartitionCellByPlaneNormalToEdge(point=(0,0,%f), edge=myPart.edges.findAt((0,0,%f),), cells=myPart.cells)\n" % (ttot-temp, L[2*model.n].thickness/2))

    f.write("myModel.Material(name='SR_top')\n")
    f.write("myModel.materials['SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
    f.write("myModel.materials['SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
    f.write("myModel.materials['SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
    f.write("myModel.HomogeneousSolidSection(name='Section_SR_top',material='SR_top', thickness=None)\n")
    f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=0,xMax=x,yMin=0,yMax=y,zMin=%f,zMax=%f)), sectionName='Section_SR_top', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((ttot-L[0].thickness),ttot))

    f.write("myModel.Material(name='SR_btm')\n")
    f.write("myModel.materials['SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
    f.write("myModel.materials['SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
    f.write("myModel.materials['SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))
    f.write("myModel.HomogeneousSolidSection(name='Section_SR_btm',material='SR_btm', thickness=None)\n")
    f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=0,xMax=x,yMin=0,yMax=y,zMin=0,zMax=%f)), sectionName='Section_SR_btm', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % (L[2*model.n].thickness))
    

    temp = L[0].thickness
    for i in range(model.n-1):
        temp=temp+L[2*i+1].thickness+L[2*i+2].thickness
        f.write("myModel.Material(name='PPG%d')\n" % (i+1))
        f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
        f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
        f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        f.write("myModel.HomogeneousSolidSection(name='Section_PPG%d',material='PPG%d', thickness=None)\n" % ((i+1),(i+1)))
        f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=0,xMax=x,yMin=0,yMax=y,zMin=%f,zMax=%f)), sectionName='Section_PPG%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((ttot-temp),(ttot-temp+L[2*i+2].thickness),(i+1)))

        f.write("myModel.Material(name='L%d')\n" % (i+1))
        f.write("myModel.materials['L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
        f.write("myModel.materials['L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
        f.write("myModel.materials['L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))
        f.write("myModel.HomogeneousSolidSection(name='Section_L%d',material='L%d', thickness=None)\n" % ((i+1),(i+1)))
        f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=0,xMax=x,yMin=0,yMax=y,zMin=%f,zMax=%f)), sectionName='Section_L%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((ttot-temp+L[2*i+2].thickness),(ttot-temp+L[2*i+2].thickness+L[2*i+1].thickness),(i+1)))

    f.write("myModel.Material(name='L%d')\n" % (model.n))
    f.write("myModel.materials['L%d'].Density(table=((%fe-09,),))\n" % (model.n, L[2*model.n-1].unit.density))
    f.write("myModel.materials['L%d'].Elastic(table=((%f,%f),))\n" % (model.n, L[2*model.n-1].unit.modulus, L[2*model.n-1].unit.poisson))
    f.write("myModel.materials['L%d'].Expansion(table=((%fe-06,),))\n" % (model.n, L[2*model.n-1].unit.cte))
    f.write("myModel.HomogeneousSolidSection(name='Section_L%d',material='L%d', thickness=None)\n" % (model.n, model.n))
    f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=0,xMax=x,yMin=0,yMax=y,zMin=%f,zMax=%f)), sectionName='Section_L%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % (L[2*model.n].thickness,(L[2*model.n].thickness+L[2*model.n-1].thickness),model.n))

    f.write("myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)\n")
    f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-1-1', part=myPart)\n")

    f.write("myModel.rootAssembly.Set(edges=myModel.rootAssembly.instances['Part-1-1'].edges.getByBoundingBox(xMin=x/2,xMax=x/2,yMin=0,yMax=y,zMin=0,zMax=0), name='fix')\n")
    f.write("myModel.rootAssembly.Set(edges=myModel.rootAssembly.instances['Part-1-1'].edges.getByBoundingBox(xMin=0,xMax=0,yMin=0,yMax=y,zMin=%f,zMax=%f), name='load')\n" % (ttot, ttot))

    f.write("RP=myModel.rootAssembly.ReferencePoint(point=(0.0, 0.0, 1.0))\n")
    f.write("myModel.rootAssembly.Set(name='RP', referencePoints=(myModel.rootAssembly.referencePoints[RP.id], ))\n")

    f.write("myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['Part-1-1'].faces.getByBoundingBox(xMin=0,xMax=0,yMin=0,yMax=y,zMin=0,zMax=%f), name='Xsymm')\n" % ttot)
    f.write("myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['Part-1-1'].faces.getByBoundingBox(xMin=0,xMax=x,yMin=0,yMax=0,zMin=0,zMax=%f), name='Ysymm')\n" % ttot)
    
    f.write("myModel.StaticStep(initialInc=0.1, name='Step-1', previous='Initial')\n")
    f.write("myModel.MultipointConstraint(controlPoint=myModel.rootAssembly.sets['RP'], csys=None, mpcType=TIE_MPC, name='Constraint-1', surface=myModel.rootAssembly.sets['load'], userMode=DOF_MODE_MPC, userType=0)\n")
    f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='Load', region=myModel.rootAssembly.sets['RP'], u1=UNSET, u2=UNSET, u3=-0.01, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    f.write("myModel.XsymmBC(createStepName='Initial', localCsys=None, name='Xsymm', region=myModel.rootAssembly.sets['Xsymm'])\n")
    f.write("myModel.YsymmBC(createStepName='Initial', localCsys=None, name='Ysymm', region=myModel.rootAssembly.sets['Ysymm'])\n")
    f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='fix', region=myModel.rootAssembly.sets['fix'], u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    f.write("myPart.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=%f)\n" % round(max(model.x,model.y)/100,1))
    f.write("myPart.generateMesh()\n")
    f.write("myPart.setElementType(elemTypes=(mesh.ElemType(elemCode=C3D8I, elemLibrary=STANDARD, secondOrderAccuracy=OFF, distortionControl=DEFAULT), mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD), mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)), regions=(myPart.cells.getByBoundingBox(xMin=0,xMax=x,yMin=0,yMax=y,zMin=0,zMax=%f), ))\n" % ttot)
    f.write("myModel.rootAssembly.regenerate()\n")
    f.write("mdb.models.changeKey(fromName='Model-1', toName='Global_Modulus')\n")
    if CheckCPU.get()==1: cpu=32
    else: cpu=4
    f.write("mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE, model='Global_Modulus', modelPrint=OFF, multiprocessingMode=DEFAULT, name='Modulus', nodalOutputPrecision=SINGLE, numCpus=%d, numDomains=%d, numGPUs=0, numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)\n" % (cpu,cpu))
    
    f.write("mdb.saveAs(pathName='%s_Modulus')\n" % model.project)
    if CheckJob.get()==0: return True
    f.write("mdb.jobs['Modulus'].submit(consistencyChecking=OFF)\n")
    f.write("mdb.jobs['Modulus'].waitForCompletion()\n")

    f.write("myOdb=visualization.openOdb(path='Modulus.odb')\n")
    f.write("myViewport=session.Viewport(name='z displacement (%s)',origin=(0,0),width=200,height=130)\n" % (model.project))
    f.write("myViewport.setValues(displayedObject=myOdb)\n")
    f.write("myViewport.odbDisplay.setPrimaryVariable(variableLabel='U',outputPosition=NODAL,refinement=(COMPONENT,'U3'))\n")
    f.write("myViewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))\n")
    #f.write("myViewport.maximize()\n")
    f.write("myViewport.view.fitView()\n")
    #f.write("session.printOptions.setValues(vpBackground=ON)\n")
    f.write("myViewport.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=ON, mirrorAboutYzPlane=ON)\n")
    f.write("session.printToFile(fileName='%s_Z_img', format=PNG, canvasObjects=(myViewport,))\n" % model.project)
    f.write("myViewport.minimize()\n")

    f.write("myViewport2=session.Viewport(name='Force (%s)',origin=(0,0),width=200,height=130)\n" % (model.project))
    f.write("myViewport2.setValues(displayedObject=myOdb)\n")
    f.write("myViewport2.odbDisplay.setPrimaryVariable(variableLabel='RF',outputPosition=NODAL,refinement=(COMPONENT,'RF3'))\n")
    f.write("myViewport2.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))\n")
    #f.write("myViewport.maximize()\n")
    f.write("myViewport2.view.fitView()\n")
    #f.write("session.printOptions.setValues(vpBackground=ON)\n")
    f.write("myViewport2.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=ON, mirrorAboutYzPlane=ON)\n")
    f.write("session.printToFile(fileName='%s_F_img', format=PNG, canvasObjects=(myViewport2,))\n" % model.project)
    f.write("myViewport2.minimize()\n")
    
    f.write("f=open('%s_Modulus_result.txt','w')\n" % model.project)
    f.write("strMinMax=myViewport.getPrimVarMinMaxLoc()\n")
    f.write("f.write('z:'+str(strMinMax)+'\\n')\n") #Z
    f.write("strMinMax2=myViewport2.getPrimVarMinMaxLoc()\n")
    f.write("f.write('F:'+str(strMinMax2)+'\\n')\n") #F
    f.write("f.write(str(strMinMax['minValue'])+'\\n')\n") #Z = -0.01
    f.write("f.write(str(strMinMax2['minValue'])+'\\n')\n") #F
    f.write("f.write('%s\\n')\n" % str(ttot)) #t
    f.write("f.close()\n")

    return True

def btnModulusClick():
    if model.type!='unit':
        messagebox.showwarning(title="error",message="unit만 가능")
        return
    if entry_project.get()=='':
        messagebox.showwarning(title="error",message="Enter project name.")
        return
    model.project=entry_project.get()

    if updatedata()==False:
        messagebox.showwarning(title="error",message="Failed to update input data")
        return

    if os.path.exists('D:/AbaqusSim')==False:
        os.mkdir('D:/AbaqusSim')
    
    if os.path.exists('D:/AbaqusSim/%s' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s' % model.project)
    
    if os.path.exists('D:/AbaqusSim/%s/Modulus' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s/Modulus' % model.project)

    os.chdir('D:/AbaqusSim/%s/Modulus' % model.project)

    SaveInput('D:/AbaqusSim/%s/Modulus' % model.project)

    if writescriptModulus()==False:
        messagebox.showwarning(title="error",message="failed to write script (Modulus)")
        return

    if CheckGUI.get()==1: os.system("abaqus cae script=%s_Modulus.py" % model.project)
    else: os.system("abaqus cae nogui=%s_Modulus.py" % model.project)

    if CheckJob.get()==1:
        try:
            f=open("D:/AbaqusSim/%s/Modulus/%s_Modulus_result.txt" % (model.project,model.project),'r')
        except:
            messagebox.showwarning(title="error",message="failed to open result file (Modulus)")
            return
        f.readline()
        f.readline()
        f.readline()
        F=abs(float(f.readline().strip()))
        t=float(f.readline().strip())
        f.close()
        E=(((model.x/2)**3) * F)/(model.y*(t**3)*0.01)
        
        label_result_modulus.config(text='E='+str(round(E))+'MPa')
        button_result_modulus.place(x=1130, y=150, width=40, height=25)
        check_modulus.place(x=1180, y=150, width=15, height=25)
    else:
        if CheckGUI.get()==0:
            messagebox.showwarning(title="Modulus", message="modeling completed (Modulus)")

    return

def btnResultModulusClick():
    try:
        f=open("D:/AbaqusSim/%s/Modulus/%s_Modulus_result.txt" % (model.project,model.project),'r')
    except:
        messagebox.showwarning(title="error",message="failed to open result file (Modulus)")
        return
    f.readline()
    f.readline()
    f.readline()
    F=abs(float(f.readline().strip()))
    t=float(f.readline().strip())
    f.close()
    E=(((model.x/2)**3) * F)/(model.y*(t**3)*0.01)

    rw=tk.Toplevel(win)
    rw.title(model.project+' Modulus')
    rw.geometry("1230x550+50+60")

    label_title=tk.Label(rw, text=model.project+' Modulus result')
    label_result1=tk.Label(rw, text='F='+str(round(F,6))+'N, Δz=0.01mm, t='+str(round(t,4))+'mm')
    label_result2=tk.Label(rw, text='E='+str(round(E))+'MPa')
    
    global img_result1, img_result2, img_result1r, img_result2r

    img_result1=Image.open("D:/AbaqusSim/%s/Modulus/%s_Z_img.png" % (model.project, model.project))
    img_result1=img_result1.resize((600,388), PIL.Image.LANCZOS)
    img_result1r=ImageTk.PhotoImage(img_result1)
    label_img1=tk.Label(rw, image=img_result1r)
    img_result2=Image.open("D:/AbaqusSim/%s/Modulus/%s_F_img.png" % (model.project, model.project))
    img_result2=img_result2.resize((600,388), PIL.Image.LANCZOS)
    img_result2r=ImageTk.PhotoImage(img_result2)
    label_img2=tk.Label(rw, image=img_result2r)

    label_title.place(x=50, y=5, width=500, height=30)
    label_img1.place(x=10, y=50, width=600, height=388)
    label_img2.place(x=620, y=50, width=600, height=388)
    label_result1.place(x=10, y=450, width=600, height=50)
    label_result2.place(x=620, y=450, width=600, height=50)
    return


def writescriptShell(): #unit, 1block, 2block, meshed
    try:
        f=open(model.project+'_Shell.py','w')
    except:
        return False
    
    f.write("from abaqus import *\n")
    f.write("from abaqusConstants import *\n")
    f.write("import visualization\n")
    f.write("import interaction\n")
    f.write("backwardCompatibility.setValues(includeDeprecated=True, reportDeprecated=False)\n")
    f.write("import regionToolset\n")
    f.write("import sketch\n")
    f.write("import part\n")

    f.write("myModel = mdb.Model(name='Model-1')\n")

    if model.type=='unit':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #unit
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((0,0,0),)), name='unit')\n")

        f.write("myModel.Material(name='SR_top')\n")
        f.write("myModel.materials['SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='SR_btm')\n")
        f.write("myModel.materials['SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='L%d')\n" % (i+1))
            f.write("myModel.materials['L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))
        
        f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
    
    elif model.type=='1block':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))
        f.write("a=%f\n" % model.a)
        f.write("b=%f\n" % model.b)

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("xyCoordsInner = ((b-x,y-a),(x-b,y-a),(x-b,a-y),(b-x,a-y),(b-x,y-a))\n") #unit
        f.write("xyCoordsOuter = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #dummy
        f.write("for i in range(len(xyCoordsInner)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner[i],point2=xyCoordsInner[i+1])\n")
        f.write("for i in range(len(xyCoordsOuter)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoordsOuter[i],point2=xyCoordsOuter[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((x,y,0),)), name='dummy')\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((0,0,0),)), name='unit')\n")
        
        f.write("mySketch3 = myModel.ConstrainedSketch(name='Sketch C',sheetSize=500.0)\n")
        f.write("mySketch3.Line(point1=(-x,0),point2=(x,0))\n")
        f.write("mySketch3.Line(point1=(0,-y),point2=(0,y))\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch3)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x,y,0),)),sketch=mySketch3)\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x),0.5*(y-a),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x),0.5*(a-y),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(x-b),0.5*(a-y),0),)))\n")

        if CheckG.get()==1:
            f.write("mySketchG = myModel.ConstrainedSketch(name='Sketch G',sheetSize=500.0)\n")
            f.write("xg=%f/2\n" % (model.x*1.5))
            f.write("yg=%f/2\n" % (model.y*1.5))
            f.write("xyCoordsG = ((-xg,yg),(xg,yg),(xg,-yg),(-xg,-yg),(-xg,yg))\n")
            f.write("for i in range(len(xyCoordsG)-1):\n")
            f.write("    mySketchG.Line(point1=xyCoordsG[i],point2=xyCoordsG[i+1])\n")
            f.write("myPartG = myModel.Part(name='Part-2', dimensionality=THREE_D, type=DISCRETE_RIGID_SURFACE)\n")
            f.write("myPartG.BaseShell(sketch=mySketchG)\n")
            f.write("RP=myPartG.ReferencePoint(point=(0,0,0))\n")
        
        f.write("myModel.Material(name='U_SR_top')\n")
        f.write("myModel.materials['U_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['U_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['U_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='U_SR_btm')\n")
        f.write("myModel.materials['U_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['U_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['U_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        f.write("myModel.Material(name='D_SR_top')\n")
        f.write("myModel.materials['D_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].dummy.density))
        f.write("myModel.materials['D_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].dummy.modulus, L[0].dummy.poisson))
        f.write("myModel.materials['D_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].dummy.cte))
        f.write("myModel.Material(name='D_SR_btm')\n")
        f.write("myModel.materials['D_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].dummy.density))
        f.write("myModel.materials['D_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].dummy.modulus, L[2*model.n].dummy.poisson))
        f.write("myModel.materials['D_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].dummy.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='U_L%d')\n" % (i+1))
            f.write("myModel.materials['U_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['U_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['U_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))

            f.write("myModel.Material(name='D_L%d')\n" % (i+1))
            f.write("myModel.materials['D_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].dummy.density))
            f.write("myModel.materials['D_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson))
            f.write("myModel.materials['D_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].dummy.cte))
        
        if CheckG.get()==1:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        else:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        f.write("myPart.compositeLayups['dummy'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['dummy'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
    
    elif model.type=='2block':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))
        f.write("a=%f\n" % model.a)
        f.write("b=%f\n" % model.b)
        f.write("c=%f\n" % (model.c/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("xyCoordsInner1 = ((-c,y-a),(b-x,y-a),(b-x,a-y),(-c,a-y),(-c,y-a))\n") #unit_left
        f.write("xyCoordsInner2 = ((c,y-a),(x-b,y-a),(x-b,a-y),(c,a-y),(c,y-a))\n") #unit_right
        f.write("xyCoordsOuter = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #dummy
        f.write("for i in range(len(xyCoordsInner1)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner1[i],point2=xyCoordsInner1[i+1])\n")
        f.write("for i in range(len(xyCoordsInner2)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner2[i],point2=xyCoordsInner2[i+1])\n")
        f.write("for i in range(len(xyCoordsOuter)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoordsOuter[i],point2=xyCoordsOuter[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((x,y,0),)), name='dummy')\n")
        f.write("myPart.Set(faces=myPart.faces.findAt((((b-x-c)/2,0,0),),(((c+x-b)/2,0,0),)), name='unit')\n")
        
        f.write("mySketch3 = myModel.ConstrainedSketch(name='Sketch C',sheetSize=500.0)\n")
        f.write("mySketch3.Line(point1=(-x,0),point2=(x,0))\n")
        f.write("mySketch3.Line(point1=(0,-y),point2=(0,y))\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt((((b-x-c)/2,0,0),),(((c+x-b)/2,0,0),)),sketch=mySketch3)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x,y,0),)),sketch=mySketch3)\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x-c),0.5*(y-a),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x-c),0.5*(a-y),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(x-b+c),0.5*(a-y),0),)))\n")

        if CheckG.get()==1:
            f.write("mySketchG = myModel.ConstrainedSketch(name='Sketch G',sheetSize=500.0)\n")
            f.write("xg=%f/2\n" % (model.x*1.5))
            f.write("yg=%f/2\n" % (model.y*1.5))
            f.write("xyCoordsG = ((-xg,yg),(xg,yg),(xg,-yg),(-xg,-yg),(-xg,yg))\n")
            f.write("for i in range(len(xyCoordsG)-1):\n")
            f.write("    mySketchG.Line(point1=xyCoordsG[i],point2=xyCoordsG[i+1])\n")
            f.write("myPartG = myModel.Part(name='Part-2', dimensionality=THREE_D, type=DISCRETE_RIGID_SURFACE)\n")
            f.write("myPartG.BaseShell(sketch=mySketchG)\n")
            f.write("RP=myPartG.ReferencePoint(point=(0,0,0))\n")
        
        f.write("myModel.Material(name='U_SR_top')\n")
        f.write("myModel.materials['U_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['U_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['U_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.Material(name='U_SR_btm')\n")
        f.write("myModel.materials['U_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['U_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['U_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))

        f.write("myModel.Material(name='D_SR_top')\n")
        f.write("myModel.materials['D_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].dummy.density))
        f.write("myModel.materials['D_SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].dummy.modulus, L[0].dummy.poisson))
        f.write("myModel.materials['D_SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].dummy.cte))
        f.write("myModel.Material(name='D_SR_btm')\n")
        f.write("myModel.materials['D_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].dummy.density))
        f.write("myModel.materials['D_SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].dummy.modulus, L[2*model.n].dummy.poisson))
        f.write("myModel.materials['D_SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].dummy.cte))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
        
        for i in range(model.n):
            f.write("myModel.Material(name='U_L%d')\n" % (i+1))
            f.write("myModel.materials['U_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['U_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['U_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))

            f.write("myModel.Material(name='D_L%d')\n" % (i+1))
            f.write("myModel.materials['D_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].dummy.density))
            f.write("myModel.materials['D_L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].dummy.modulus, L[2*i+1].dummy.poisson))
            f.write("myModel.materials['D_L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].dummy.cte))
        
        if CheckG.get()==1:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        else:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        f.write("myPart.compositeLayups['dummy'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['dummy'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))

    elif model.type=='meshed':
        f.write("x=%f\n" % model.x)
        f.write("y=%f\n" % model.y)
        f.write("nrow=%d\n" % model.row)
        f.write("ncol=%d\n" % model.col)
        
        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((0,0),(x,0),(x,y),(0,y),(0,0))\n")
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("    mySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")

        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("for i in range(1,ncol):\n")
        f.write("    mySketch2.Line(point1=(i*(x/ncol),0),point2=(i*(x/ncol),y))\n")
        f.write("for i in range(1,nrow):\n")
        f.write("    mySketch2.Line(point1=(0,i*(y/nrow)),point2=(x,i*(y/nrow)))\n")

        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        for i in range(model.row):
            for j in range(model.col):
                f.write("myPart.Set(faces=myPart.faces.findAt(((%f,%f,0),)), name='Set_%d_%d')\n" % (((j+0.5)*(model.x/model.col)),(model.y-(i+0.5)*(model.y/model.row)),i,j))
                f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='Set_%d_%d', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n" % (i,j))
                f.write("myPart.compositeLayups['Set_%d_%d'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n" % (i,j))
                f.write("myPart.compositeLayups['Set_%d_%d'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n" % (i,j))
        
        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
            
        for i in range(model.row):
            for j in range(model.col):
                f.write("myModel.Material(name='SR_top_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_top_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[0].section[i][j].density))
                f.write("myModel.materials['SR_top_%d_%d'].Elastic(table=((%f,%f),))\n" % (i, j, L[0].section[i][j].modulus, L[0].section[i][j].poisson))
                f.write("myModel.materials['SR_top_%d_%d'].Expansion(table=((%fe-06,),))\n" % (i, j, L[0].section[i][j].cte))
                
                f.write("myModel.Material(name='SR_btm_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_btm_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[2*model.n].section[i][j].density))
                f.write("myModel.materials['SR_btm_%d_%d'].Elastic(table=((%f,%f),))\n" % (i, j, L[2*model.n].section[i][j].modulus, L[2*model.n].section[i][j].poisson))
                f.write("myModel.materials['SR_btm_%d_%d'].Expansion(table=((%fe-06,),))\n" % (i, j, L[2*model.n].section[i][j].cte))
                
        for i in range(model.n):    
            for row in range(model.row):
                for col in range(model.col):
                    f.write("myModel.Material(name='L%d_%d_%d')\n" % ((i+1),row,col))
                    f.write("myModel.materials['L%d_%d_%d'].Density(table=((%fe-09,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].density))
                    f.write("myModel.materials['L%d_%d_%d'].Elastic(table=((%f,%f),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].modulus, L[2*i+1].section[row][col].poisson))
                    f.write("myModel.materials['L%d_%d_%d'].Expansion(table=((%fe-06,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].cte))
                    
        for i in range(model.row):
            for j in range(model.col):
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_btm_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,i,j,i,j,L[2*model.n].thickness))
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,model.n,i,j,i,j,L[2*model.n-1].thickness))
                for k in range(model.n-1,0,-1):
                    f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,k,(2*(model.n-k)+1),i,j,L[2*k].thickness))
                    f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,k,i,j,(2*(model.n-k)+2),i,j,L[2*k-1].thickness))
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_top_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,i,j,(2*model.n+1),i,j,L[0].thickness))   


    f.write("myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)\n")
    f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-1-1', part=myPart)\n")

    if (CheckG.get()==1): #1block, 2block
        f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-2-1', part=myPartG)\n")
        f.write("myModel.rootAssembly.Set(name='RP', referencePoints=(myModel.rootAssembly.instances['Part-2-1'].referencePoints[RP.id], ))\n")
        
        f.write("myModel.rootAssembly.Surface(name='Ground', side1Faces=myModel.rootAssembly.instances['Part-2-1'].faces.findAt(((0,0,0),)))\n")
        if model.type=='1block': f.write("myModel.rootAssembly.Surface(name='strip', side2Faces=myModel.rootAssembly.instances['Part-1-1'].faces.findAt(((0,0,0),),((x-b/2,0,0),)))\n")
        elif model.type=='2block': f.write("myModel.rootAssembly.Surface(name='strip', side2Faces=myModel.rootAssembly.instances['Part-1-1'].faces.findAt(((0,0,0),),((0.5*(x-b+c),0,0),)))\n")

    f.write("mdb.saveAs(pathName='%s_Shell')\n" % model.project)
    return True


def btnShellClick():
    if entry_project.get()=='':
        messagebox.showwarning(title="error",message="Enter project name.")
        return
    model.project=entry_project.get()

    if updatedata()==False:
        messagebox.showwarning(title="error",message="Failed to update input data")
        return

    if os.path.exists('D:/AbaqusSim')==False:
        os.mkdir('D:/AbaqusSim')
    
    if os.path.exists('D:/AbaqusSim/%s' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s' % model.project)
    
    if os.path.exists('D:/AbaqusSim/%s/Shell' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s/Shell' % model.project)

    os.chdir('D:/AbaqusSim/%s/Shell' % model.project)

    SaveInput('D:/AbaqusSim/%s/Shell' % model.project)

    if writescriptShell()==False:
        messagebox.showwarning(title="error",message="failed to write script (Shell)")
        return

    if CheckGUI.get()==1:
        os.system("abaqus cae script=%s_Shell.py" % model.project)
    else:
        os.system("abaqus cae nogui=%s_Shell.py" % model.project)
        messagebox.showwarning(title="Shell", message="modeling completed (Shell)")
    return

def writescriptSolid(): #unit, meshed
    try:
        f=open(model.project+'_Solid.py','w')
    except:
        return False
    
    f.write("from abaqus import *\n")
    f.write("from abaqusConstants import *\n")
    f.write("import visualization\n")
    f.write("import interaction\n")
    f.write("backwardCompatibility.setValues(includeDeprecated=True, reportDeprecated=False)\n")
    f.write("import regionToolset\n")
    f.write("import sketch\n")
    f.write("import part\n")

    f.write("myModel = mdb.Model(name='Model-1')\n")

    if model.type=='unit':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #unit
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")

        ttot=0
        for i in range(2*model.n+1):
            ttot=ttot+L[i].thickness

        f.write("myPart.BaseSolidExtrude(depth=%f, sketch=mySketch)\n" % ttot)
        
        temp=0
        for i in range(2*model.n):
            temp=temp+L[i].thickness
            f.write("myPart.PartitionCellByPlaneNormalToEdge(point=(-x,-y,%f), edge=myPart.edges.findAt((-x,-y,%f),), cells=myPart.cells)\n" % (ttot-temp, L[2*model.n].thickness/2))
        
        temp = L[0].thickness
        for i in range(model.n-1):
            temp=temp+L[2*i+1].thickness+L[2*i+2].thickness
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
            f.write("myModel.HomogeneousSolidSection(name='Section_PPG%d',material='PPG%d', thickness=None)\n" % ((i+1),(i+1)))
            f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=-x,xMax=x,yMin=-y,yMax=y,zMin=%f,zMax=%f)), sectionName='Section_PPG%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((ttot-temp),(ttot-temp+L[2*i+2].thickness),(i+1)))

        f.write("myModel.Material(name='SR_top')\n")
        f.write("myModel.materials['SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        f.write("myModel.materials['SR_top'].Elastic(table=((%f,%f),))\n" % (L[0].unit.modulus, L[0].unit.poisson))
        f.write("myModel.materials['SR_top'].Expansion(table=((%fe-06,),))\n" % (L[0].unit.cte))
        f.write("myModel.HomogeneousSolidSection(name='Section_SR_top',material='SR_top', thickness=None)\n")
        f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=-x,xMax=x,yMin=-y,yMax=y,zMin=%f,zMax=%f)), sectionName='Section_SR_top', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((ttot-L[0].thickness),ttot))

        f.write("myModel.Material(name='SR_btm')\n" )
        f.write("myModel.materials['SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        f.write("myModel.materials['SR_btm'].Elastic(table=((%f,%f),))\n" % (L[2*model.n].unit.modulus, L[2*model.n].unit.poisson))
        f.write("myModel.materials['SR_btm'].Expansion(table=((%fe-06,),))\n" % (L[2*model.n].unit.cte))
        f.write("myModel.HomogeneousSolidSection(name='Section_SR_btm',material='SR_btm', thickness=None)\n")
        f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=-x,xMax=x,yMin=-y,yMax=y,zMin=0,zMax=%f)), sectionName='Section_SR_btm', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % (L[2*model.n].thickness))
        
        temp = L[0].thickness
        for i in range(model.n):
            temp = temp+L[2*i+1].thickness+L[2*i+2].thickness
            f.write("myModel.Material(name='L%d')\n" % (i+1))
            f.write("myModel.materials['L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            f.write("myModel.materials['L%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+1].unit.modulus, L[2*i+1].unit.poisson))
            f.write("myModel.materials['L%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+1].unit.cte))
            f.write("myModel.HomogeneousSolidSection(name='Section_L%d',material='L%d', thickness=None)\n" % ((i+1),(i+1)))
            f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=-x,xMax=x,yMin=-y,yMax=y,zMin=%f,zMax=%f)), sectionName='Section_L%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((ttot-temp+L[2*i+2].thickness),(ttot-temp+L[2*i+2].thickness+L[2*i+1].thickness),(i+1)))

    elif model.type=='meshed':
        f.write("x=%f\n" % model.x)
        f.write("y=%f\n" % model.y)
            
        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((0,0),(x,0),(x,y),(0,y),(0,0))\n")
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("    mySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")

        ttot=0
        for i in range(2*model.n+1):
            ttot=ttot+L[i].thickness

        f.write("myPart.BaseSolidExtrude(depth=%f, sketch=mySketch)\n" % ttot)
        
        temp=0
        for i in range(2*model.n):
            temp=temp+L[i].thickness
            f.write("myPart.PartitionCellByPlaneNormalToEdge(point=(0,0,%f), edge=myPart.edges.findAt((0,0,%f),), cells=myPart.cells)\n" % (ttot-temp, L[2*model.n].thickness/2))
        
        for i in range(1,model.col):
            f.write("myPart.PartitionCellByPlaneNormalToEdge(point=(%f,0,0), edge=myPart.edges.findAt((%f,0,0),), cells=myPart.cells)\n" % (((model.x/model.col)*i), (model.x-(model.x/model.col)/2)))
        for i in range(1,model.row):
            f.write("myPart.PartitionCellByPlaneNormalToEdge(point=(0,%f,0), edge=myPart.edges.findAt((0,%f,0),), cells=myPart.cells)\n" % (((model.y/model.row)*i), (model.y-(model.y/model.row)/2)))
        
        temp = L[0].thickness
        for i in range(model.n-1):
            temp=temp+L[2*i+1].thickness+L[2*i+2].thickness
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            f.write("myModel.materials['PPG%d'].Elastic(table=((%f,%f),))\n" % ((i+1), L[2*i+2].modulus, L[2*i+2].poisson))
            f.write("myModel.materials['PPG%d'].Expansion(table=((%fe-06,),))\n" % ((i+1), L[2*i+2].cte))
            f.write("myModel.HomogeneousSolidSection(name='Section_PPG%d',material='PPG%d', thickness=None)\n" % ((i+1),(i+1)))
            f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=0,xMax=x,yMin=0,yMax=y,zMin=%f,zMax=%f)), sectionName='Section_PPG%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((ttot-temp),(ttot-temp+L[2*i+2].thickness),(i+1)))
            
        for i in range(model.row):
            for j in range(model.col):
                f.write("myModel.Material(name='SR_top_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_top_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[0].section[i][j].density))
                f.write("myModel.materials['SR_top_%d_%d'].Elastic(table=((%f,%f),))\n" % (i, j, L[0].section[i][j].modulus, L[0].section[i][j].poisson))
                f.write("myModel.materials['SR_top_%d_%d'].Expansion(table=((%fe-06,),))\n" % (i, j, L[0].section[i][j].cte))
                f.write("myModel.HomogeneousSolidSection(name='Section_SR_top_%d_%d',material='SR_top_%d_%d', thickness=None)\n" % (i,j,i,j))
                f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=%f,xMax=%f,yMin=%f,yMax=%f,zMin=%f,zMax=%f)), sectionName='Section_SR_top_%d_%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((j*(model.x/model.col)),((j+1)*(model.x/model.col)),(model.y-(i+1)*(model.y/model.row)),(model.y-i*(model.y/model.row)),(ttot-L[0].thickness),ttot,i,j))

                f.write("myModel.Material(name='SR_btm_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_btm_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[2*model.n].section[i][j].density))
                f.write("myModel.materials['SR_btm_%d_%d'].Elastic(table=((%f,%f),))\n" % (i, j, L[2*model.n].section[i][j].modulus, L[2*model.n].section[i][j].poisson))
                f.write("myModel.materials['SR_btm_%d_%d'].Expansion(table=((%fe-06,),))\n" % (i, j, L[2*model.n].section[i][j].cte))
                f.write("myModel.HomogeneousSolidSection(name='Section_SR_btm_%d_%d',material='SR_btm_%d_%d', thickness=None)\n" % (i,j,i,j))
                f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=%f,xMax=%f,yMin=%f,yMax=%f,zMin=0,zMax=%f)), sectionName='Section_SR_btm_%d_%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((j*(model.x/model.col)),((j+1)*(model.x/model.col)),(model.y-(i+1)*(model.y/model.row)),(model.y-i*(model.y/model.row)),L[2*model.n].thickness,i,j))
        
        temp = L[0].thickness
        for i in range(model.n):
            temp = temp+L[2*i+1].thickness+L[2*i+2].thickness
            for row in range(model.row):
                for col in range(model.col):
                    f.write("myModel.Material(name='L%d_%d_%d')\n" % ((i+1),row,col))
                    f.write("myModel.materials['L%d_%d_%d'].Density(table=((%fe-09,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].density))
                    f.write("myModel.materials['L%d_%d_%d'].Elastic(table=((%f,%f),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].modulus, L[2*i+1].section[row][col].poisson))
                    f.write("myModel.materials['L%d_%d_%d'].Expansion(table=((%fe-06,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].cte))
                    f.write("myModel.HomogeneousSolidSection(name='Section_L%d_%d_%d',material='L%d_%d_%d', thickness=None)\n" % ((i+1),row,col,(i+1),row,col))
                    f.write("myPart.SectionAssignment(region=regionToolset.Region(cells=myPart.cells.getByBoundingBox(xMin=%f,xMax=%f,yMin=%f,yMax=%f,zMin=%f,zMax=%f)), sectionName='Section_L%d_%d_%d', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)\n" % ((col*(model.x/model.col)),((col+1)*(model.x/model.col)),(model.y-(row+1)*(model.y/model.row)),(model.y-row*(model.y/model.row)),(ttot-temp+L[2*i+2].thickness),(ttot-temp+L[2*i+2].thickness+L[2*i+1].thickness),(i+1),row,col))

    f.write("myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)\n")
    f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-1-1', part=myPart)\n")
    f.write("mdb.saveAs(pathName='%s_Solid')\n" % model.project)
    return True

def btnSolidClick():
    if (model.type=='1block')|(model.type=='2block'):
        messagebox.showwarning(title="error",message="unit, meshed만 가능")
        return
    if entry_project.get()=='':
        messagebox.showwarning(title="error",message="Enter project name.")
        return
    model.project=entry_project.get()

    if updatedata()==False:
        messagebox.showwarning(title="error",message="Failed to update input data")
        return
    
    if os.path.exists('D:/AbaqusSim')==False:
        os.mkdir('D:/AbaqusSim')
    
    if os.path.exists('D:/AbaqusSim/%s' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s' % model.project)
    
    if os.path.exists('D:/AbaqusSim/%s/Solid' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s/Solid' % model.project)

    os.chdir('D:/AbaqusSim/%s/Solid' % model.project)

    SaveInput('D:/AbaqusSim/%s/Solid' % model.project)

    if writescriptSolid()==False:
        messagebox.showwarning(title="error",message="failed to write script (Solid)")
        return

    if CheckGUI.get()==1:
        os.system("abaqus cae script=%s_Solid.py" % model.project)
    else:
        os.system("abaqus cae nogui=%s_Solid.py" % model.project)
        messagebox.showwarning(title="Solid", message="modeling completed (Solid)")
    return

def writescriptHighT(): #수정필요
    try:
        f=open(model.project+'_HighT.py','w')
    except:
        return False
    f.write("from abaqus import *\n")
    f.write("from abaqusConstants import *\n")
    f.write("import visualization\n")
    f.write("import interaction\n")
    f.write("backwardCompatibility.setValues(includeDeprecated=True, reportDeprecated=False)\n")
    f.write("import regionToolset\n")
    f.write("import sketch\n")
    f.write("import part\n")

    f.write("myModel = mdb.Model(name='Model-1')\n")

    if model.type=='unit':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #unit
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((0,0,0),)), name='unit')\n")

        f.write("myModel.Material(name='SR_top')\n")
        f.write("myModel.materials['SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        strtemp="("
        for i in range(len(L[0].unit.Elastic)):
            strtemp=strtemp+'('+str(L[0].unit.Elastic[i][0])+','+str(L[0].unit.Elastic[i][1])+','+str(L[0].unit.Elastic[i][2])+')'
            if len(L[0].unit.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].unit.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['SR_top'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[0].unit.Expansion)):
            strtemp=strtemp+'('+str(L[0].unit.Expansion[i][0])+'e-06,'+str(L[0].unit.Expansion[i][1])+')'
            if len(L[0].unit.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].unit.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['SR_top'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))
        f.write("myModel.Material(name='SR_btm')\n")
        f.write("myModel.materials['SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        strtemp="("
        for i in range(len(L[2*model.n].unit.Elastic)):
            strtemp=strtemp+'('+str(L[2*model.n].unit.Elastic[i][0])+','+str(L[2*model.n].unit.Elastic[i][1])+','+str(L[2*model.n].unit.Elastic[i][2])+')'
            if len(L[2*model.n].unit.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].unit.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['SR_btm'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[2*model.n].unit.Expansion)):
            strtemp=strtemp+'('+str(L[2*model.n].unit.Expansion[i][0])+'e-06,'+str(L[2*model.n].unit.Expansion[i][1])+')'
            if len(L[2*model.n].unit.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].unit.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['SR_btm'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))
        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            strtemp="("
            for j in range(len(L[2*i+2].unit.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+2].unit.Elastic[j][0])+','+str(L[2*i+2].unit.Elastic[j][1])+','+str(L[2*i+2].unit.Elastic[j][2])+')'
                if len(L[2*i+2].unit.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+2].unit.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['PPG%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+2].unit.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+2].unit.Expansion[j][0])+'e-06,'+str(L[2*i+2].unit.Expansion[j][1])+')'
                if len(L[2*i+2].unit.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+2].unit.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['PPG%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
        
        for i in range(model.n):
            f.write("myModel.Material(name='L%d')\n" % (i+1))
            f.write("myModel.materials['L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            strtemp="("
            for j in range(len(L[2*i+1].unit.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+1].unit.Elastic[j][0])+','+str(L[2*i+1].unit.Elastic[j][1])+','+str(L[2*i+1].unit.Elastic[j][2])+')'
                if len(L[2*i+1].unit.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].unit.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['L%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+1].unit.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+1].unit.Expansion[j][0])+'e-06,'+str(L[2*i+1].unit.Expansion[j][1])+')'
                if len(L[2*i+1].unit.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].unit.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['L%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
        
        f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
    
    elif model.type=='1block':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))
        f.write("a=%f\n" % model.a)
        f.write("b=%f\n" % model.b)

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("xyCoordsInner = ((b-x,y-a),(x-b,y-a),(x-b,a-y),(b-x,a-y),(b-x,y-a))\n") #unit
        f.write("xyCoordsOuter = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #dummy
        f.write("for i in range(len(xyCoordsInner)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner[i],point2=xyCoordsInner[i+1])\n")
        f.write("for i in range(len(xyCoordsOuter)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoordsOuter[i],point2=xyCoordsOuter[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((x,y,0),)), name='dummy')\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((0,0,0),)), name='unit')\n")
        
        f.write("mySketch3 = myModel.ConstrainedSketch(name='Sketch C',sheetSize=500.0)\n")
        f.write("mySketch3.Line(point1=(-x,0),point2=(x,0))\n")
        f.write("mySketch3.Line(point1=(0,-y),point2=(0,y))\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch3)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x,y,0),)),sketch=mySketch3)\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x),0.5*(y-a),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x),0.5*(a-y),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(x-b),0.5*(a-y),0),)))\n")

        if CheckG.get()==1:
            f.write("mySketchG = myModel.ConstrainedSketch(name='Sketch G',sheetSize=500.0)\n")
            f.write("xg=%f/2\n" % (model.x*1.5))
            f.write("yg=%f/2\n" % (model.y*1.5))
            f.write("xyCoordsG = ((-xg,yg),(xg,yg),(xg,-yg),(-xg,-yg),(-xg,yg))\n")
            f.write("for i in range(len(xyCoordsG)-1):\n")
            f.write("    mySketchG.Line(point1=xyCoordsG[i],point2=xyCoordsG[i+1])\n")
            f.write("myPartG = myModel.Part(name='Part-2', dimensionality=THREE_D, type=DISCRETE_RIGID_SURFACE)\n")
            f.write("myPartG.BaseShell(sketch=mySketchG)\n")
            f.write("RP=myPartG.ReferencePoint(point=(0,0,0))\n")
        
        f.write("myModel.Material(name='U_SR_top')\n")
        f.write("myModel.materials['U_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        strtemp="("
        for i in range(len(L[0].unit.Elastic)):
            strtemp=strtemp+'('+str(L[0].unit.Elastic[i][0])+','+str(L[0].unit.Elastic[i][1])+','+str(L[0].unit.Elastic[i][2])+')'
            if len(L[0].unit.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].unit.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['U_SR_top'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[0].unit.Expansion)):
            strtemp=strtemp+'('+str(L[0].unit.Expansion[i][0])+'e-06,'+str(L[0].unit.Expansion[i][1])+')'
            if len(L[0].unit.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].unit.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['U_SR_top'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))
        f.write("myModel.Material(name='U_SR_btm')\n")
        f.write("myModel.materials['U_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        strtemp="("
        for i in range(len(L[2*model.n].unit.Elastic)):
            strtemp=strtemp+'('+str(L[2*model.n].unit.Elastic[i][0])+','+str(L[2*model.n].unit.Elastic[i][1])+','+str(L[2*model.n].unit.Elastic[i][2])+')'
            if len(L[2*model.n].unit.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].unit.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['U_SR_btm'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[2*model.n].unit.Expansion)):
            strtemp=strtemp+'('+str(L[2*model.n].unit.Expansion[i][0])+'e-06,'+str(L[2*model.n].unit.Expansion[i][1])+')'
            if len(L[2*model.n].unit.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].unit.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['U_SR_btm'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))

        f.write("myModel.Material(name='D_SR_top')\n")
        f.write("myModel.materials['D_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].dummy.density))
        strtemp="("
        for i in range(len(L[0].dummy.Elastic)):
            strtemp=strtemp+'('+str(L[0].dummy.Elastic[i][0])+','+str(L[0].dummy.Elastic[i][1])+','+str(L[0].dummy.Elastic[i][2])+')'
            if len(L[0].dummy.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].dummy.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['D_SR_top'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[0].dummy.Expansion)):
            strtemp=strtemp+'('+str(L[0].dummy.Expansion[i][0])+'e-06,'+str(L[0].dummy.Expansion[i][1])+')'
            if len(L[0].dummy.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].dummy.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['D_SR_top'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))
        f.write("myModel.Material(name='D_SR_btm')\n")
        f.write("myModel.materials['D_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].dummy.density))
        strtemp="("
        for i in range(len(L[2*model.n].dummy.Elastic)):
            strtemp=strtemp+'('+str(L[2*model.n].dummy.Elastic[i][0])+','+str(L[2*model.n].dummy.Elastic[i][1])+','+str(L[2*model.n].dummy.Elastic[i][2])+')'
            if len(L[2*model.n].dummy.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].dummy.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['D_SR_btm'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[2*model.n].dummy.Expansion)):
            strtemp=strtemp+'('+str(L[2*model.n].dummy.Expansion[i][0])+'e-06,'+str(L[2*model.n].dummy.Expansion[i][1])+')'
            if len(L[2*model.n].dummy.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].dummy.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['D_SR_btm'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            strtemp="("
            for j in range(len(L[2*i+2].unit.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+2].unit.Elastic[j][0])+','+str(L[2*i+2].unit.Elastic[j][1])+','+str(L[2*i+2].unit.Elastic[j][2])+')'
                if len(L[2*i+2].unit.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+2].unit.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['PPG%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+2].unit.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+2].unit.Expansion[j][0])+'e-06,'+str(L[2*i+2].unit.Expansion[j][1])+')'
                if len(L[2*i+2].unit.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+2].unit.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['PPG%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
        
        for i in range(model.n):
            f.write("myModel.Material(name='U_L%d')\n" % (i+1))
            f.write("myModel.materials['U_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            strtemp="("
            for j in range(len(L[2*i+1].unit.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+1].unit.Elastic[j][0])+','+str(L[2*i+1].unit.Elastic[j][1])+','+str(L[2*i+1].unit.Elastic[j][2])+')'
                if len(L[2*i+1].unit.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].unit.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['U_L%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+1].unit.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+1].unit.Expansion[j][0])+'e-06,'+str(L[2*i+1].unit.Expansion[j][1])+')'
                if len(L[2*i+1].unit.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].unit.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['U_L%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))

            f.write("myModel.Material(name='D_L%d')\n" % (i+1))
            f.write("myModel.materials['D_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].dummy.density))
            strtemp="("
            for j in range(len(L[2*i+1].dummy.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+1].dummy.Elastic[j][0])+','+str(L[2*i+1].dummy.Elastic[j][1])+','+str(L[2*i+1].dummy.Elastic[j][2])+')'
                if len(L[2*i+1].dummy.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].dummy.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['D_L%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+1].dummy.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+1].dummy.Expansion[j][0])+'e-06,'+str(L[2*i+1].dummy.Expansion[j][1])+')'
                if len(L[2*i+1].dummy.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].dummy.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['D_L%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
        
        if CheckG.get()==1:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        else:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        f.write("myPart.compositeLayups['dummy'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['dummy'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
    
    elif model.type=='2block':
        f.write("x=%f\n" % (model.x/2))
        f.write("y=%f\n" % (model.y/2))
        f.write("a=%f\n" % model.a)
        f.write("b=%f\n" % model.b)
        f.write("c=%f\n" % (model.c/2))

        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("xyCoordsInner1 = ((-c,y-a),(b-x,y-a),(b-x,a-y),(-c,a-y),(-c,y-a))\n") #unit_left
        f.write("xyCoordsInner2 = ((c,y-a),(x-b,y-a),(x-b,a-y),(c,a-y),(c,y-a))\n") #unit_right
        f.write("xyCoordsOuter = ((-x,y),(x,y),(x,-y),(-x,-y),(-x,y))\n") #dummy
        f.write("for i in range(len(xyCoordsInner1)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner1[i],point2=xyCoordsInner1[i+1])\n")
        f.write("for i in range(len(xyCoordsInner2)-1):\n")
        f.write("\tmySketch2.Line(point1=xyCoordsInner2[i],point2=xyCoordsInner2[i+1])\n")
        f.write("for i in range(len(xyCoordsOuter)-1):\n")
        f.write("\tmySketch.Line(point1=xyCoordsOuter[i],point2=xyCoordsOuter[i+1])\n")
        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        f.write("myPart.Set(faces=myPart.faces.findAt(((x,y,0),)), name='dummy')\n")
        f.write("myPart.Set(faces=myPart.faces.findAt((((b-x-c)/2,0,0),),(((c+x-b)/2,0,0),)), name='unit')\n")
        
        f.write("mySketch3 = myModel.ConstrainedSketch(name='Sketch C',sheetSize=500.0)\n")
        f.write("mySketch3.Line(point1=(-x,0),point2=(x,0))\n")
        f.write("mySketch3.Line(point1=(0,-y),point2=(0,y))\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt((((b-x-c)/2,0,0),),(((c+x-b)/2,0,0),)),sketch=mySketch3)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((x,y,0),)),sketch=mySketch3)\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((-x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((x,-y,0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x-c),0.5*(y-a),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(b-x-c),0.5*(a-y),0),)))\n")
        f.write("myPart.RemoveFaces(deleteCells=False, faceList=myPart.faces.findAt(((0.5*(x-b+c),0.5*(a-y),0),)))\n")

        if CheckG.get()==1:
            f.write("mySketchG = myModel.ConstrainedSketch(name='Sketch G',sheetSize=500.0)\n")
            f.write("xg=%f/2\n" % (model.x*1.5))
            f.write("yg=%f/2\n" % (model.y*1.5))
            f.write("xyCoordsG = ((-xg,yg),(xg,yg),(xg,-yg),(-xg,-yg),(-xg,yg))\n")
            f.write("for i in range(len(xyCoordsG)-1):\n")
            f.write("    mySketchG.Line(point1=xyCoordsG[i],point2=xyCoordsG[i+1])\n")
            f.write("myPartG = myModel.Part(name='Part-2', dimensionality=THREE_D, type=DISCRETE_RIGID_SURFACE)\n")
            f.write("myPartG.BaseShell(sketch=mySketchG)\n")
            f.write("RP=myPartG.ReferencePoint(point=(0,0,0))\n")
        
        f.write("myModel.Material(name='U_SR_top')\n")
        f.write("myModel.materials['U_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].unit.density))
        strtemp="("
        for i in range(len(L[0].unit.Elastic)):
            strtemp=strtemp+'('+str(L[0].unit.Elastic[i][0])+','+str(L[0].unit.Elastic[i][1])+','+str(L[0].unit.Elastic[i][2])+')'
            if len(L[0].unit.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].unit.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['U_SR_top'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[0].unit.Expansion)):
            strtemp=strtemp+'('+str(L[0].unit.Expansion[i][0])+'e-06,'+str(L[0].unit.Expansion[i][1])+')'
            if len(L[0].unit.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].unit.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['U_SR_top'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))

        f.write("myModel.Material(name='U_SR_btm')\n")
        f.write("myModel.materials['U_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].unit.density))
        strtemp="("
        for i in range(len(L[2*model.n].unit.Elastic)):
            strtemp=strtemp+'('+str(L[2*model.n].unit.Elastic[i][0])+','+str(L[2*model.n].unit.Elastic[i][1])+','+str(L[2*model.n].unit.Elastic[i][2])+')'
            if len(L[2*model.n].unit.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].unit.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['U_SR_btm'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[2*model.n].unit.Expansion)):
            strtemp=strtemp+'('+str(L[2*model.n].unit.Expansion[i][0])+'e-06,'+str(L[2*model.n].unit.Expansion[i][1])+')'
            if len(L[2*model.n].unit.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].unit.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['U_SR_btm'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))

        f.write("myModel.Material(name='D_SR_top')\n")
        f.write("myModel.materials['D_SR_top'].Density(table=((%fe-09,),))\n" % (L[0].dummy.density))
        strtemp="("
        for i in range(len(L[0].dummy.Elastic)):
            strtemp=strtemp+'('+str(L[0].dummy.Elastic[i][0])+','+str(L[0].dummy.Elastic[i][1])+','+str(L[0].dummy.Elastic[i][2])+')'
            if len(L[0].dummy.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].dummy.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['D_SR_top'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[0].dummy.Expansion)):
            strtemp=strtemp+'('+str(L[0].dummy.Expansion[i][0])+'e-06,'+str(L[0].dummy.Expansion[i][1])+')'
            if len(L[0].dummy.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[0].dummy.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['D_SR_top'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))
        f.write("myModel.Material(name='D_SR_btm')\n")
        f.write("myModel.materials['D_SR_btm'].Density(table=((%fe-09,),))\n" % (L[2*model.n].dummy.density))
        strtemp="("
        for i in range(len(L[2*model.n].dummy.Elastic)):
            strtemp=strtemp+'('+str(L[2*model.n].dummy.Elastic[i][0])+','+str(L[2*model.n].dummy.Elastic[i][1])+','+str(L[2*model.n].dummy.Elastic[i][2])+')'
            if len(L[2*model.n].dummy.Elastic)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].dummy.Elastic)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['D_SR_btm'].Elastic(table=%s, temperatureDependency=ON)\n" % (strtemp))
        strtemp='('
        for i in range(len(L[2*model.n].dummy.Expansion)):
            strtemp=strtemp+'('+str(L[2*model.n].dummy.Expansion[i][0])+'e-06,'+str(L[2*model.n].dummy.Expansion[i][1])+')'
            if len(L[2*model.n].dummy.Expansion)==1:
                strtemp=strtemp+',)'
                break
            if i==(len(L[2*model.n].dummy.Expansion)-1):
                strtemp=strtemp+')'
            else:
                strtemp=strtemp+','
        f.write("myModel.materials['D_SR_btm'].Expansion(table=%s, temperatureDependency=ON)\n" % (strtemp))

        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            strtemp="("
            for j in range(len(L[2*i+2].unit.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+2].unit.Elastic[j][0])+','+str(L[2*i+2].unit.Elastic[j][1])+','+str(L[2*i+2].unit.Elastic[j][2])+')'
                if len(L[2*i+2].unit.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+2].unit.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['PPG%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+2].unit.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+2].unit.Expansion[j][0])+'e-06,'+str(L[2*i+2].unit.Expansion[j][1])+')'
                if len(L[2*i+2].unit.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+2].unit.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['PPG%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
        
        for i in range(model.n):
            f.write("myModel.Material(name='U_L%d')\n" % (i+1))
            f.write("myModel.materials['U_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].unit.density))
            strtemp="("
            for j in range(len(L[2*i+1].unit.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+1].unit.Elastic[j][0])+','+str(L[2*i+1].unit.Elastic[j][1])+','+str(L[2*i+1].unit.Elastic[j][2])+')'
                if len(L[2*i+1].unit.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].unit.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['U_L%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+1].unit.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+1].unit.Expansion[j][0])+'e-06,'+str(L[2*i+1].unit.Expansion[j][1])+')'
                if len(L[2*i+1].unit.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].unit.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['U_L%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))

            f.write("myModel.Material(name='D_L%d')\n" % (i+1))
            f.write("myModel.materials['D_L%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+1].dummy.density))
            strtemp="("
            for j in range(len(L[2*i+1].dummy.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+1].dummy.Elastic[j][0])+','+str(L[2*i+1].dummy.Elastic[j][1])+','+str(L[2*i+1].dummy.Elastic[j][2])+')'
                if len(L[2*i+1].dummy.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].dummy.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['D_L%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+1].dummy.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+1].dummy.Expansion[j][0])+'e-06,'+str(L[2*i+1].dummy.Expansion[j][1])+')'
                if len(L[2*i+1].dummy.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+1].dummy.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['D_L%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
        
        if CheckG.get()==1:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=BOTTOM_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        else:
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='unit', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
            f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='dummy', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n")
        f.write("myPart.compositeLayups['unit'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['unit'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        f.write("myPart.compositeLayups['dummy'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n")
        f.write("myPart.compositeLayups['dummy'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n")
        
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_btm', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (L[2*model.n].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (model.n,L[2*model.n-1].thickness))
        for i in range(model.n-1,0,-1):
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+1),L[2*i].thickness))
            f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_L%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,(2*(model.n-i)+2),L[2*i-1].thickness))
        f.write("myPart.compositeLayups['unit'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='U_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['unit'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))
        f.write("myPart.compositeLayups['dummy'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='D_SR_top', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['dummy'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % ((2*model.n+1),L[0].thickness))

    elif model.type=='meshed':
        f.write("x=%f\n" % model.x)
        f.write("y=%f\n" % model.y)
        f.write("nrow=%d\n" % model.row)
        f.write("ncol=%d\n" % model.col)
        
        f.write("mySketch = myModel.ConstrainedSketch(name='Sketch A',sheetSize=500.0)\n")
        f.write("xyCoords = ((0,0),(x,0),(x,y),(0,y),(0,0))\n")
        f.write("for i in range(len(xyCoords)-1):\n")
        f.write("    mySketch.Line(point1=xyCoords[i],point2=xyCoords[i+1])\n")

        f.write("mySketch2 = myModel.ConstrainedSketch(name='Sketch B',sheetSize=500.0)\n")
        f.write("for i in range(1,ncol):\n")
        f.write("    mySketch2.Line(point1=(i*(x/ncol),0),point2=(i*(x/ncol),y))\n")
        f.write("for i in range(1,nrow):\n")
        f.write("    mySketch2.Line(point1=(0,i*(y/nrow)),point2=(x,i*(y/nrow)))\n")

        f.write("myPart = myModel.Part(name='Part-1', dimensionality=THREE_D,type=DEFORMABLE_BODY)\n")
        
        f.write("myPart.BaseShell(sketch=mySketch)\n")
        f.write("myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(((0,0,0),)),sketch=mySketch2)\n")
        for i in range(model.row):
            for j in range(model.col):
                f.write("myPart.Set(faces=myPart.faces.findAt(((%f,%f,0),)), name='Set_%d_%d')\n" % (((j+0.5)*(model.x/model.col)),(model.y-(i+0.5)*(model.y/model.row)),i,j))
                f.write("myPart.CompositeLayup(description='', elementType=SHELL, name='Set_%d_%d', offsetType=MIDDLE_SURFACE, symmetric=False, thicknessAssignment=FROM_SECTION)\n" % (i,j))
                f.write("myPart.compositeLayups['Set_%d_%d'].Section(integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thicknessType=UNIFORM, useDensity=OFF)\n" % (i,j))
                f.write("myPart.compositeLayups['Set_%d_%d'].ReferenceOrientation(additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, fieldName='', localCsys=None, orientationType=GLOBAL)\n" % (i,j))
        
        for i in range(model.n-1):
            f.write("myModel.Material(name='PPG%d')\n" % (i+1))
            f.write("myModel.materials['PPG%d'].Density(table=((%fe-09,),))\n" % ((i+1), L[2*i+2].density))
            strtemp="("
            for j in range(len(L[2*i+2].unit.Elastic)):
                strtemp=strtemp+'('+str(L[2*i+2].unit.Elastic[j][0])+','+str(L[2*i+2].unit.Elastic[j][1])+','+str(L[2*i+2].unit.Elastic[j][2])+')'
                if len(L[2*i+2].unit.Elastic)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+2].unit.Elastic)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['PPG%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            strtemp='('
            for j in range(len(L[2*i+2].unit.Expansion)):
                strtemp=strtemp+'('+str(L[2*i+2].unit.Expansion[j][0])+'e-06,'+str(L[2*i+2].unit.Expansion[j][1])+')'
                if len(L[2*i+2].unit.Expansion)==1:
                    strtemp=strtemp+',)'
                    break
                if j==(len(L[2*i+2].unit.Expansion)-1):
                    strtemp=strtemp+')'
                else:
                    strtemp=strtemp+','
            f.write("myModel.materials['PPG%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),strtemp))
            
        for i in range(model.row):
            for j in range(model.col):
                f.write("myModel.Material(name='SR_top_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_top_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[0].section[i][j].density))
                strtemp="("
                for k in range(len(L[0].section[i][j].Elastic)):
                    strtemp=strtemp+'('+str(L[0].section[i][j].Elastic[k][0])+','+str(L[0].section[i][j].Elastic[k][1])+','+str(L[0].section[i][j].Elastic[k][2])+')'
                    if len(L[0].section[i][j].Elastic)==1:
                        strtemp=strtemp+',)'
                        break
                    if k==(len(L[0].section[i][j].Elastic)-1):
                        strtemp=strtemp+')'
                    else:
                        strtemp=strtemp+','
                f.write("myModel.materials['SR_top_%d_%d'].Elastic(table=%s, temperatureDependency=ON)\n" % (i,j,strtemp))
                strtemp='('
                for k in range(len(L[0].section[i][j].Expansion)):
                    strtemp=strtemp+'('+str(L[0].section[i][j].Expansion[k][0])+'e-06,'+str(L[0].section[i][j].Expansion[k][1])+')'
                    if len(L[0].section[i][j].Expansion)==1:
                        strtemp=strtemp+',)'
                        break
                    if k==(len(L[0].section[i][j].Expansion)-1):
                        strtemp=strtemp+')'
                    else:
                        strtemp=strtemp+','
                f.write("myModel.materials['SR_top_%d_%d'].Expansion(table=%s, temperatureDependency=ON)\n" % (i,j,strtemp))
                
                f.write("myModel.Material(name='SR_btm_%d_%d')\n" % (i,j))
                f.write("myModel.materials['SR_btm_%d_%d'].Density(table=((%fe-09,),))\n" % (i, j, L[2*model.n].section[i][j].density))
                strtemp="("
                for k in range(len(L[2*model.n].section[i][j].Elastic)):
                    strtemp=strtemp+'('+str(L[2*model.n].section[i][j].Elastic[k][0])+','+str(L[2*model.n].section[i][j].Elastic[k][1])+','+str(L[2*model.n].section[i][j].Elastic[k][2])+')'
                    if len(L[2*model.n].section[i][j].Elastic)==1:
                        strtemp=strtemp+',)'
                        break
                    if k==(len(L[2*model.n].section[i][j].Elastic)-1):
                        strtemp=strtemp+')'
                    else:
                        strtemp=strtemp+','
                f.write("myModel.materials['SR_btm_%d_%d'].Elastic(table=%s, temperatureDependency=ON)\n" % (i,j,strtemp))
                strtemp='('
                for k in range(len(L[2*model.n].section[i][j].Expansion)):
                    strtemp=strtemp+'('+str(L[2*model.n].section[i][j].Expansion[k][0])+'e-06,'+str(L[2*model.n].section[i][j].Expansion[k][1])+')'
                    if len(L[2*model.n].section[i][j].Expansion)==1:
                        strtemp=strtemp+',)'
                        break
                    if k==(len(L[2*model.n].section[i][j].Expansion)-1):
                        strtemp=strtemp+')'
                    else:
                        strtemp=strtemp+','
                f.write("myModel.materials['SR_btm_%d_%d'].Expansion(table=%s, temperatureDependency=ON)\n" % (i,j,strtemp))
                
        for i in range(model.n):    
            for row in range(model.row):
                for col in range(model.col):
                    f.write("myModel.Material(name='L%d_%d_%d')\n" % ((i+1),row,col))
                    f.write("myModel.materials['L%d_%d_%d'].Density(table=((%fe-09,),))\n" % ((i+1),row,col, L[2*i+1].section[row][col].density))
                    strtemp="("
                    for k in range(len(L[2*i+1].section[row][col].Elastic)):
                        strtemp=strtemp+'('+str(L[2*i+1].section[row][col].Elastic[k][0])+','+str(L[2*i+1].section[row][col].Elastic[k][1])+','+str(L[2*i+1].section[row][col].Elastic[k][2])+')'
                        if len(L[2*i+1].section[row][col].Elastic)==1:
                            strtemp=strtemp+',)'
                            break
                        if k==(len(L[2*i+1].section[row][col].Elastic)-1):
                            strtemp=strtemp+')'
                        else:
                            strtemp=strtemp+','
                    f.write("myModel.materials['L%d_%d_%d'].Elastic(table=%s, temperatureDependency=ON)\n" % ((i+1),row,col,strtemp))
                    strtemp='('
                    for k in range(len(L[2*i+1].section[row][col].Expansion)):
                        strtemp=strtemp+'('+str(L[2*i+1].section[row][col].Expansion[k][0])+'e-06,'+str(L[2*i+1].section[row][col].Expansion[k][1])+')'
                        if len(L[2*i+1].section[row][col].Expansion)==1:
                            strtemp=strtemp+',)'
                            break
                        if k==(len(L[2*i+1].section[row][col].Expansion)-1):
                            strtemp=strtemp+')'
                        else:
                            strtemp=strtemp+','
                    f.write("myModel.materials['L%d_%d_%d'].Expansion(table=%s, temperatureDependency=ON)\n" % ((i+1),row,col,strtemp))
                    
        for i in range(model.row):
            for j in range(model.col):
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_btm_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,i,j,i,j,L[2*model.n].thickness))
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,model.n,i,j,i,j,L[2*model.n-1].thickness))
                for k in range(model.n-1,0,-1):
                    f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='PPG%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,k,(2*(model.n-k)+1),i,j,L[2*k].thickness))
                    f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='L%d_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,k,i,j,(2*(model.n-k)+2),i,j,L[2*k-1].thickness))
                f.write("myPart.compositeLayups['Set_%d_%d'].CompositePly(additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_3, material='SR_top_%d_%d', numIntPoints=3, orientationType=SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-%d', region=myPart.sets['Set_%d_%d'], suppressed=False, thickness=%f, thicknessType=SPECIFY_THICKNESS)\n" % (i,j,i,j,(2*model.n+1),i,j,L[0].thickness))   

    f.write("myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)\n")
    f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-1-1', part=myPart)\n")
    
    if (CheckG.get()==1): #1block, 2block
        f.write("myModel.rootAssembly.Instance(dependent=ON, name='Part-2-1', part=myPartG)\n")
        f.write("myModel.rootAssembly.Set(name='RP', referencePoints=(myModel.rootAssembly.instances['Part-2-1'].referencePoints[RP.id], ))\n")
        
        f.write("myModel.rootAssembly.Surface(name='Ground', side1Faces=myModel.rootAssembly.instances['Part-2-1'].faces.findAt(((0,0,0),)))\n")
        if model.type=='1block': f.write("myModel.rootAssembly.Surface(name='strip', side2Faces=myModel.rootAssembly.instances['Part-1-1'].faces.findAt(((0,0,0),),((x-b/2,0,0),)))\n")
        elif model.type=='2block': f.write("myModel.rootAssembly.Surface(name='strip', side2Faces=myModel.rootAssembly.instances['Part-1-1'].faces.findAt(((0,0,0),),((0.5*(x-b+c),0,0),)))\n")

    if CheckG.get()==1: f.write("myModel.StaticStep(initialInc=0.1, name='Step-1', nlgeom=ON, previous='Initial', maxNumInc=1000000, minInc=1e-12)\n")
    else: f.write("myModel.StaticStep(initialInc=0.1, name='Step-1', nlgeom=ON, previous='Initial', maxNumInc=10000, minInc=1e-08)\n")

    if model.type=='unit':
        f.write("myModel.rootAssembly.Set(name='xyz', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((-x,-y,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='yz', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((x,-y,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='z', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((-x,y,0),)))\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xyz', region=myModel.rootAssembly.sets['xyz'], u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='yz', region=myModel.rootAssembly.sets['yz'], u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='z', region=myModel.rootAssembly.sets['z'], u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    elif model.type=='1block':
        f.write("myModel.rootAssembly.Set(name='xsymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((0,(y-a)/2,0),),((0,y-a/2,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='ysymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt((((x-b)/2,0,0),),((x-b/2,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='center', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")

        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xsymm', region=myModel.rootAssembly.sets['xsymm'], u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=SET, ur3=SET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='ysymm', region=myModel.rootAssembly.sets['ysymm'], u1=UNSET, u2=SET, u3=UNSET, ur1=SET, ur2=UNSET, ur3=SET)\n")
        if (CheckG.get()==1): f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=UNSET, ur1=SET, ur2=SET, ur3=UNSET)\n")
        else: f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)\n")
    elif model.type=='2block':
        f.write("myModel.rootAssembly.Set(name='xsymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((0,(y-a)/2,0),),((0,y-a/2,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='ysymm', edges=myModel.rootAssembly.instances['Part-1-1'].edges.findAt(((c/2,0,0),),(((c+x-b)/2,0,0),),((x-b/2,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='center', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")

        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xsymm', region=myModel.rootAssembly.sets['xsymm'], u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=SET, ur3=SET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='ysymm', region=myModel.rootAssembly.sets['ysymm'], u1=UNSET, u2=SET, u3=UNSET, ur1=SET, ur2=UNSET, ur3=SET)\n")
        if (CheckG.get()==1): f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=UNSET, ur1=SET, ur2=SET, ur3=UNSET)\n")
        else: f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='center', region=myModel.rootAssembly.sets['center'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)\n")

    elif model.type=='meshed':
        f.write("myModel.rootAssembly.Set(name='xyz', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='yz', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((x,0,0),)))\n")
        f.write("myModel.rootAssembly.Set(name='z', vertices=myModel.rootAssembly.instances['Part-1-1'].vertices.findAt(((0,y,0),)))\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='xyz', region=myModel.rootAssembly.sets['xyz'], u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='yz', region=myModel.rootAssembly.sets['yz'], u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='z', region=myModel.rootAssembly.sets['z'], u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
    
    f.write("myModel.rootAssembly.Set(name='Set-4', edges=myModel.rootAssembly.instances['Part-1-1'].edges, faces=myModel.rootAssembly.instances['Part-1-1'].faces, vertices=myModel.rootAssembly.instances['Part-1-1'].vertices)\n")
    
    if CheckG.get()==1:
        f.write("myModel.StaticStep(initialInc=0.1, name='Step-2', previous='Step-1')\n")
        f.write("myModel.ContactProperty('IntProp-1')\n")
        f.write("myModel.interactionProperties['IntProp-1'].TangentialBehavior(dependencies=0, directionality=ISOTROPIC, elasticSlipStiffness=None, formulation=PENALTY, fraction=0.005, maximumElasticSlip=FRACTION, pressureDependency=OFF, shearStressLimit=None, slipRateDependency=OFF, table=((0.1, ), ), temperatureDependency=OFF)\n")
        f.write("myModel.SurfaceToSurfaceContactStd(adjustMethod=NONE, clearanceRegion=None, createStepName='Initial', datumAxis=None, initialClearance=OMIT, interactionProperty='IntProp-1', main=myModel.rootAssembly.surfaces['Ground'], name='Int-1', secondary=myModel.rootAssembly.surfaces['strip'], sliding=FINITE, thickness=ON)\n")
        f.write("myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['Part-2-1'].faces.findAt(((0,0,0),)), name='b_Set-6')\n")
        f.write("myModel.RigidBody(bodyRegion=myModel.rootAssembly.sets['b_Set-6'], name='Constraint-1', refPointRegion=myModel.rootAssembly.sets['RP'])\n")
        f.write("myModel.Gravity(comp3=-2000.0, createStepName='Step-1', distributionType=UNIFORM, field='', name='Load-1', region=myModel.rootAssembly.sets['Set-4'])\n")
    
    f.write("myModel.Temperature(createStepName='Initial', crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=UNIFORM, magnitudes=(150.0, ), name='Predefined Field-1', region=myModel.rootAssembly.sets['Set-4'])\n")
    
    if CheckG.get()==1:
        f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(150.0, ), stepName='Step-1')\n")
    else:
        f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(25.0, ), stepName='Step-1')\n")
    
    model.step.append(200)
    model.step.append(260)
    if CheckG.get()==0:
        for i in range(len(model.step)):
            f.write("myModel.StaticStep(initialInc=0.1, name='Step-%d', previous='Step-%d')\n" % ((i+2),(i+1)))
            f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(%f, ), stepName='Step-%d')\n" % (model.step[i],(i+2)))

    f.write("myPart.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=%f)\n" %(round(max(model.x,model.y)/100,1)))
    f.write("myPart.generateMesh()\n")

    if CheckG.get()==1:
        f.write("myPartG.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=%f)\n" % (max(model.x,model.y)*1.5))
        f.write("myPartG.generateMesh()\n")
        #f.write("myModel.EncastreBC(createStepName='Initial', localCsys=None, name='RP', region=myModel.rootAssembly.sets['RP'])\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='RP', region=myModel.rootAssembly.sets['RP'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)\n")
        f.write("myModel.StaticStep(name='Step-3', previous='Step-2')\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='center-DISP', region=myModel.rootAssembly.sets['center'], u1=UNSET, u2=UNSET, u3=-0.0001, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='Xsymm-DISP', region=myModel.rootAssembly.sets['xsymm'], u1=UNSET, u2=UNSET, u3=-0.0001, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.DisplacementBC(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='Ysymm-DISP', region=myModel.rootAssembly.sets['ysymm'], u1=UNSET, u2=UNSET, u3=-0.0001, ur1=UNSET, ur2=UNSET, ur3=UNSET)\n")
        f.write("myModel.boundaryConditions['Xsymm-DISP'].deactivate('Step-2')\n")
        f.write("myModel.boundaryConditions['Ysymm-DISP'].deactivate('Step-2')\n")
        f.write("myModel.boundaryConditions['center-DISP'].deactivate('Step-2')\n")
        f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(150.0, ), stepName='Step-2')\n")
        f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(25.0, ), stepName='Step-3')\n")
        for i in range(len(model.step)):
            f.write("myModel.StaticStep(initialInc=0.1, name='Step-%d', previous='Step-%d')\n" % ((i+4),(i+3)))
            f.write("myModel.predefinedFields['Predefined Field-1'].setValuesInStep(magnitudes=(%f, ), stepName='Step-%d')\n" % (model.step[i],(i+4)))
    
    f.write("myModel.rootAssembly.regenerate()\n")
    f.write("mdb.models.changeKey(fromName='Model-1', toName='POR')\n")
    if CheckCPU.get()==1: cpu=32
    else: cpu=4
    f.write("mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE, model='POR', modelPrint=OFF, multiprocessingMode=DEFAULT, name='POR', nodalOutputPrecision=SINGLE, numCpus=%d, numDomains=%d, numGPUs=0, numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)\n" % (cpu,cpu))
    
    f.write("mdb.saveAs(pathName='%s_HighT')\n" % model.project)
    if CheckJob.get()==0: return True
    f.write("mdb.jobs['POR'].submit(consistencyChecking=OFF)\n")
    f.write("mdb.jobs['POR'].waitForCompletion()\n")
    #Error in job POR: Time increment required is less than the minimum specified
    """
    f.write("myViewport=session.Viewport(name='Warpage (%s)',origin=(0,0),width=200,height=130)\n" % (model.project))

    f.write("myOdb=visualization.openOdb(path='POR.odb')\n")
    f.write("myViewport.setValues(displayedObject=myOdb)\n")
    f.write("myViewport.odbDisplay.setPrimaryVariable(variableLabel='U',outputPosition=NODAL,refinement=(COMPONENT,'U3'))\n")
    f.write("myViewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))\n")
    #f.write("myViewport.maximize()\n")
    f.write("myViewport.view.fitView()\n")
    #f.write("session.printOptions.setValues(vpBackground=ON)\n")
    if (model.type=='1block')|(model.type=='2block'):
        f.write("myViewport.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=ON, mirrorAboutYzPlane=ON)\n")
    else:
        f.write("myViewport.odbDisplay.basicOptions.setValues(mirrorAboutXzPlane=OFF, mirrorAboutYzPlane=OFF)\n")
    f.write("session.printToFile(fileName='%s_img', format=PNG, canvasObjects=(myViewport,))\n" % model.project)
    
    #
    f.write("f=open('%s_result.txt','w')\n" % model.project)
    f.write("strMinMax=myViewport.getPrimVarMinMaxLoc()\n")
    f.write("f.write(str(strMinMax)+'\\n\\n')\n")
    #f.write("if (strMinMax['minNodeLabel']==1)|(strMinMax['maxNodeLabel']==7): warpage=strMinMax['minValue']-strMinMax['maxValue']\n") #smile -
    #f.write("elif (strMinMax['maxNodeLabel']==1)|(strMinMax['minNodeLabel']==7): warpage=strMinMax['maxValue']-strMinMax['minValue']\n") #crying +
    #f.write("else: warpage=0\n")
    if CheckG.get()==1:
        f.write("fieldValues=myOdb.steps['Step-3'].frames[-1].fieldOutputs['U'].values\n")
    else:
        f.write("fieldValues=myOdb.steps['Step-1'].frames[-1].fieldOutputs['U'].values\n")
    
    if model.type=='unit':
        f.write("for v in fieldValues:\n")
        f.write("    if v.nodeLabel==1: z1=v.data[2]\n")
        f.write("if (z1>((strMinMax['maxValue']+strMinMax['minValue'])/2)): warpage=strMinMax['minValue']-strMinMax['maxValue']; sc='smile'\n")
        f.write("elif (z1<((strMinMax['maxValue']+strMinMax['minValue'])/2)): warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='crying'\n")
        f.write("else: warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='none'\n")
    elif (model.type=='1block')|(model.type=='2block'):
        f.write("for v in fieldValues:\n")
        f.write("    if v.nodeLabel==1: z1=v.data[2]\n")
        f.write("    elif v.nodeLabel==5: z5=v.data[2]\n")
        f.write("    elif v.nodeLabel==6: z6=v.data[2]\n")
        f.write("    elif v.nodeLabel==7: z7=v.data[2]; break\n")
        f.write("if z1<((z5+z6+z7)/3): warpage=strMinMax['minValue']-strMinMax['maxValue']; sc='smile'\n")
        f.write("elif z1>((z5+z6+z7)/3): warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='crying'\n")
        f.write("else: warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='none'\n")
    elif model.type=='meshed':
        f.write("for v in fieldValues:\n")
        f.write("    if v.nodeLabel==3: z3=v.data[2]\n")
        f.write("if (z3>((strMinMax['maxValue']+strMinMax['minValue'])/2)): warpage=strMinMax['minValue']-strMinMax['maxValue']; sc='smile'\n")
        f.write("elif (z3<((strMinMax['maxValue']+strMinMax['minValue'])/2)): warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='crying'\n")
        f.write("else: warpage=strMinMax['maxValue']-strMinMax['minValue']; sc='none'\n")
    f.write("f.write('warpage : '+str(round(warpage,3))+'\\n'+sc)\n")
    f.write("f.close()\n")
    """
    return True

def btnHighTClick():
    if entry_project.get()=='':
        messagebox.showwarning(title="error",message="Enter project name.")
        return
    model.project=entry_project.get()
    """
    if updatedata()==False:
        messagebox.showwarning(title="error",message="Failed to update input data")
        return
    """
    if os.path.exists('D:/AbaqusSim')==False:
        os.mkdir('D:/AbaqusSim')
    
    if os.path.exists('D:/AbaqusSim/%s' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s' % model.project)
    
    if os.path.exists('D:/AbaqusSim/%s/HighT' % model.project)==False:
        os.mkdir('D:/AbaqusSim/%s/HighT' % model.project)

    os.chdir('D:/AbaqusSim/%s/HighT' % model.project)

    #SaveInput('D:/AbaqusSim/%s/HighT' % model.project) #수정필요

    if writescriptHighT()==False:
        messagebox.showwarning(title="error",message="failed to write script (HighT)")
        return

    if CheckGUI.get()==1: os.system("abaqus cae script=%s_HighT.py" % model.project)
    else: os.system("abaqus cae nogui=%s_HighT.py" % model.project)
    """
    if CheckJob.get()==1:
        try:
            f=open("D:/AbaqusSim/%s/HighT/%s_HighT_result.txt" % (model.project,model.project),'r')
        except:
            messagebox.showwarning(title="error",message="failed to open result file (HighT)")
            return
        #수정필요
        f.readline()
        f.readline()
        result=f.readline().strip()
        sc=f.readline().strip()
        f.close()
        
        label_result_warpage.config(text=result+' ('+sc+')')
        button_result_warpage.place(x=1130, y=80, width=40, height=25)
        check_warpage.place(x=1180, y=80, width=15, height=25)
    else:
        if CheckGUI.get()==0:
            messagebox.showwarning(title="HighT", message="modeling completed (HighT)")
    """
    return

def SaveInput(dir):
    now=datetime.now()
    time=now.strftime("%Y%m%d_%H%M")
    if CheckG.get()==0: strInputFileName=time+'_'+cb_customer.get()+'_'+entry_modelname.get()+'_'+str(model.n)+'L_'+cb_structure.get()+'_'+model.type
    else:  strInputFileName=time+'_'+cb_customer.get()+'_'+entry_modelname.get()+'_'+str(model.n)+'L_'+cb_structure.get()+'_'+model.type+'_Gr'
    try:
        f=open(dir+'/'+strInputFileName+'_input.csv','w',newline='')
    except:
        messagebox.showwarning(title="error (save input)", message="failed to save the input file")
        return
    writer=csv.writer(f)
    writer.writerow(['ModelType',model.type,'#Layer',model.n])
    if model.type=='unit':
        writer.writerow(['x',str(model.x),'y',str(model.y)])
        writer.writerow(['No.','Layer','Thickness','Modulus','CTE','Poisson','Density','Fill','Portion','Modulus(unit)','CTE(unit)','Poisson(unit)','Density(unit)'])
        for i in range(2*model.n+1):
            if i==0: #SR_top
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'',list_Portion_unit[i].get(),list_Modulus_unit[i].get(),list_CTE_unit[i].get(),list_Poisson_unit[i].get(),list_Density_unit[i].get()])
            elif i==2*model.n: #SR_btm
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'',list_Portion_unit[model.n+1].get(),list_Modulus_unit[i].get(),list_CTE_unit[i].get(),list_Poisson_unit[i].get(),list_Density_unit[i].get()])
            elif i%2==1: #Cu
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),list_Fill[int((i-1)/2)].get(),list_Portion_unit[int((i+1)/2)].get(),list_Modulus_unit[i].get(),list_CTE_unit[i].get(),list_Poisson_unit[i].get(),list_Density_unit[i].get()])
            else: #PPG
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'','',list_Modulus_unit[i].get(),list_CTE_unit[i].get(),list_Poisson_unit[i].get(),list_Density_unit[i].get()])
    elif (model.type=='1block')|(model.type=='2block'):
        if model.type=='1block': writer.writerow(['x',str(model.x),'y',str(model.y),'a',str(model.a),'b',str(model.b)])
        elif model.type=='2block': writer.writerow(['x',str(model.x),'y',str(model.y),'a',str(model.a),'b',str(model.b),'c',str(model.c)])
        writer.writerow(['No.','Layer','Thickness','Modulus','CTE','Poisson','Density','Fill','Portion(unit)','Portion(dummy)','Modulus(unit)','CTE(unit)','Poisson(unit)','Density(unit)','Modulus(dummy)','CTE(dummy)','Poisson(dummy)','Density(dummy)'])
        for i in range(2*model.n+1):
            if i==0: #SR_top
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'',list_Portion_unit[i].get(),list_Portion_dummy[i].get(),list_Modulus_unit[i].get(),list_CTE_unit[i].get(),list_Poisson_unit[i].get(),list_Density_unit[i].get(),list_Modulus_dummy[i].get(),list_CTE_dummy[i].get(),list_Poisson_dummy[i].get(),list_Density_dummy[i].get()])
            elif i==2*model.n: #SR_btm
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'',list_Portion_unit[model.n+1].get(),list_Portion_dummy[model.n+1].get(),list_Modulus_unit[i].get(),list_CTE_unit[i].get(),list_Poisson_unit[i].get(),list_Density_unit[i].get(),list_Modulus_dummy[i].get(),list_CTE_dummy[i].get(),list_Poisson_dummy[i].get(),list_Density_dummy[i].get()])
            elif i%2==1: #Cu
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),list_Fill[int((i-1)/2)].get(),list_Portion_unit[int((i+1)/2)].get(),list_Portion_dummy[int((i+1)/2)].get(),list_Modulus_unit[i].get(),list_CTE_unit[i].get(),list_Poisson_unit[i].get(),list_Density_unit[i].get(),list_Modulus_dummy[i].get(),list_CTE_dummy[i].get(),list_Poisson_dummy[i].get(),list_Density_dummy[i].get()])
            else: #PPG
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'','','',list_Modulus_unit[i].get(),list_CTE_unit[i].get(),list_Poisson_unit[i].get(),list_Density_unit[i].get(),list_Modulus_dummy[i].get(),list_CTE_dummy[i].get(),list_Poisson_dummy[i].get(),list_Density_dummy[i].get()])
    elif model.type=='meshed':
        writer.writerow(['x',str(model.x),'y',str(model.y),'row',str(model.row),'col',str(model.col),'folder',str(model.folder)])
        writer.writerow(['No.','Layer','Thickness','Modulus','CTE','Poisson','Density','Fill'])
        for i in range(2*model.n+1):
            if (i==0)|(i==2*model.n): #SR
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get()])
            elif i%2==1: #Cu
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),list_Fill[int((i-1)/2)].get()])
            else: #PPG
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get()])
    else:
        messagebox.showwarning(title="error (save input)", message="error model type")
        f.close()
        return
    f.close()

def btnSaveInput():
    try:
        save_dir = filedialog.askdirectory()
    except:
        messagebox.showwarning(title="error (save input)", message="failed to save the input file")
        return
    now=datetime.now()
    time=now.strftime("%Y%m%d_%H%M")
    if CheckG.get()==0: strInputFileName=time+'_'+cb_customer.get()+'_'+entry_modelname.get()+'_'+str(model.n)+'L_'+cb_structure.get()+'_'+model.type
    else:  strInputFileName=time+'_'+cb_customer.get()+'_'+entry_modelname.get()+'_'+str(model.n)+'L_'+cb_structure.get()+'_'+model.type+'_Gr'
    try:
        f=open(save_dir+'/'+strInputFileName+'_input.csv','w',newline='')
    except:
        messagebox.showwarning(title="error (save input)", message="failed to save the input file")
        return
    writer=csv.writer(f)
    writer.writerow(['ModelType',model.type,'#Layer',model.n])
    if model.type=='unit':
        writer.writerow(['x',str(model.x),'y',str(model.y)])
        writer.writerow(['No.','Layer','Thickness','Modulus','CTE','Poisson','Density','Fill','Portion'])
        for i in range(2*model.n+1):
            if i==0: #SR_top
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'',list_Portion_unit[0].get()])
            elif i==2*model.n: #SR_btm
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'',list_Portion_unit[model.n+1].get()])
            elif i%2==1: #Cu
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),list_Fill[int((i-1)/2)].get(),list_Portion_unit[int((i+1)/2)].get()])
            else: #PPG
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get()])
    elif (model.type=='1block')|(model.type=='2block'):
        if model.type=='1block': writer.writerow(['x',str(model.x),'y',str(model.y),'a',str(model.a),'b',str(model.b)])
        elif model.type=='2block': writer.writerow(['x',str(model.x),'y',str(model.y),'a',str(model.a),'b',str(model.b),'c',str(model.c)])
        writer.writerow(['No.','Layer','Thickness','Modulus','CTE','Poisson','Density','Fill','Portion(unit)','Portion(dummy)'])
        for i in range(2*model.n+1):
            if i==0: #SR_top
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'',list_Portion_unit[0].get(),list_Portion_dummy[0].get()])
            elif i==2*model.n: #SR_btm
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),'',list_Portion_unit[model.n+1].get(),list_Portion_dummy[model.n+1].get()])
            elif i%2==1: #Cu
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),list_Fill[int((i-1)/2)].get(),list_Portion_unit[int((i+1)/2)].get(),list_Portion_dummy[int((i+1)/2)].get()])
            else: #PPG
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get()])
    elif model.type=='meshed':
        writer.writerow(['x',str(model.x),'y',str(model.y),'row',str(model.row),'col',str(model.col),'folder',str(model.folder)])
        writer.writerow(['No.','Layer','Thickness','Modulus','CTE','Poisson','Density','Fill'])
        for i in range(2*model.n+1):
            if (i==0)|(i==2*model.n): #SR
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get()])
            elif i%2==1: #Cu
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get(),list_Fill[int((i-1)/2)].get()])
            else: #PPG
                writer.writerow([str(i),list_Layer[i]['text'],list_Thickness[i].get(),list_Modulus[i].get(),list_CTE[i].get(),list_Poisson[i].get(),list_Density[i].get()])
    else:
        messagebox.showwarning(title="error (save input)", message="error model type")
        f.close()
        return
    f.close()

def btnLoadInput():
    fi=filedialog.askopenfilename(title = 'select input file to load', filetypes=(('*.csv','*csv'),))
    try:
        fcheck=open(fi,'r')
        line1=fcheck.readline().strip().split(sep=',')
        strType=line1[1]
        strLayer=line1[3]
        if strType!=model.type:
            messagebox.showwarning(title="error", message="model type 불일치")
            return
        if int(strLayer)!=model.n:
            messagebox.showwarning(title="error", message="층 수 불일치")
            return
        if model.type=='meshed':
            strFolder=fcheck.readline().strip().split(sep=',')[9]
            entry_folder.delete(0,tk.END)
            entry_folder.insert(0,strFolder)
        fcheck.close()
        dfi=pd.read_csv(fi,skiprows=2)
    except:
        messagebox.showwarning(title="error", message="failed to load input file")
        return
    
    if model.type=='unit':
        for i in range(2*model.n+1):
            list_Thickness[i].delete(0,tk.END)
            list_Thickness[i].insert(0,dfi.iloc[i].values[2])
            list_Modulus[i].delete(0,tk.END)
            list_Modulus[i].insert(0,dfi.iloc[i].values[3])
            list_CTE[i].delete(0,tk.END)
            list_CTE[i].insert(0,dfi.iloc[i].values[4])
            list_Poisson[i].delete(0,tk.END)
            list_Poisson[i].insert(0,dfi.iloc[i].values[5])
            list_Density[i].delete(0,tk.END)
            list_Density[i].insert(0,dfi.iloc[i].values[6])
        for i in range(model.n):
            list_Fill[i].set(dfi.iloc[2*i+1].values[7])
            list_Portion_unit[i+1].delete(0,tk.END)
            list_Portion_unit[i+1].insert(0,dfi.iloc[2*i+1].values[8])
        list_Portion_unit[0].delete(0,tk.END)
        list_Portion_unit[0].insert(0,dfi.iloc[0].values[8])
        list_Portion_unit[model.n+1].delete(0,tk.END)
        list_Portion_unit[model.n+1].insert(0,dfi.iloc[2*model.n].values[8])
    elif (model.type=='1block')|(model.type=='2block'):
        for i in range(2*model.n+1):
            list_Thickness[i].delete(0,tk.END)
            list_Thickness[i].insert(0,dfi.iloc[i].values[2])
            list_Modulus[i].delete(0,tk.END)
            list_Modulus[i].insert(0,dfi.iloc[i].values[3])
            list_CTE[i].delete(0,tk.END)
            list_CTE[i].insert(0,dfi.iloc[i].values[4])
            list_Poisson[i].delete(0,tk.END)
            list_Poisson[i].insert(0,dfi.iloc[i].values[5])
            list_Density[i].delete(0,tk.END)
            list_Density[i].insert(0,dfi.iloc[i].values[6])
        for i in range(model.n):
            list_Fill[i].set(dfi.iloc[2*i+1].values[7])
            list_Portion_unit[i+1].delete(0,tk.END)
            list_Portion_unit[i+1].insert(0,dfi.iloc[2*i+1].values[8])
            list_Portion_dummy[i+1].delete(0,tk.END)
            list_Portion_dummy[i+1].insert(0,dfi.iloc[2*i+1].values[9])
        list_Portion_unit[0].delete(0,tk.END)
        list_Portion_unit[0].insert(0,dfi.iloc[0].values[8])
        list_Portion_unit[model.n+1].delete(0,tk.END)
        list_Portion_unit[model.n+1].insert(0,dfi.iloc[2*model.n].values[8])
        list_Portion_dummy[0].delete(0,tk.END)
        list_Portion_dummy[0].insert(0,dfi.iloc[0].values[9])
        list_Portion_dummy[model.n+1].delete(0,tk.END)
        list_Portion_dummy[model.n+1].insert(0,dfi.iloc[2*model.n].values[9])
    elif model.type=='meshed':
        for i in range(2*model.n+1):
            list_Thickness[i].delete(0,tk.END)
            list_Thickness[i].insert(0,dfi.iloc[i].values[2])
            list_Modulus[i].delete(0,tk.END)
            list_Modulus[i].insert(0,dfi.iloc[i].values[3])
            list_CTE[i].delete(0,tk.END)
            list_CTE[i].insert(0,dfi.iloc[i].values[4])
            list_Poisson[i].delete(0,tk.END)
            list_Poisson[i].insert(0,dfi.iloc[i].values[5])
            list_Density[i].delete(0,tk.END)
            list_Density[i].insert(0,dfi.iloc[i].values[6])
        for i in range(model.n):
            list_Fill[i].set(dfi.iloc[2*i+1].values[7])
    return

def btnInitClick():
    if messagebox.askyesno(title='초기화', message='초기화를 진행하시겠습니까?')==False:
        return
    Init()
    cb_model.set('')

cwd=os.getcwd()

model=Model()
L=[]
Ls=[]

#input
list_No=[]              #col 0, lb
list_Layer=[]           #col 1, bt
list_Thickness=[]       #col 2, en
list_Modulus=[]         #col 3
list_CTE=[]             #col 4
list_Poisson=[]         #col 5
list_Density=[]         #col 6
list_Fill=[]            #col 7, cb (Cu)
list_Portion_unit=[]    #col 8 (Cu, SR)
list_Portion_dummy=[]   #col 9 (Cu,SR) - 1block, 2block

#output
list_Modulus_unit=[]    #col 10 
list_CTE_unit=[]        #col 11
list_Poisson_unit=[]    #col 12
list_Density_unit=[]    #col 13
list_Modulus_dummy=[]   #col 14 - 1block, 2block
list_CTE_dummy=[]       #col 15
list_Poisson_dummy=[]   #col 16
list_Density_dummy=[]   #col 17


win=tk.Tk()
win.geometry('1300x700+50+50')
win.title("Warpage & Material Properties Simulation ver.1.0")

try:
    df=pd.read_csv('data.csv')
except:
    messagebox.showwarning(title="error",message="failed to load input data (Material DB)")

label_select_model = tk.Label(win, text="select a model")
label_select_model.place(x=25, y=5, width=80, height=20)

label_model = tk.Label(win, text="model : ")
label_model.place(x=15, y=30, width=50, height=20)
values_model=['unit','1block','2block','meshed']
cb_model=tkinter.ttk.Combobox(master=win, height=15, values=values_model, state="readonly")
cb_model.place(x=65, y=30, width=80, height=20)
cb_model.bind("<<ComboboxSelected>>", selectmodel)

image_unit=tk.PhotoImage(file="img/unit.png")
label_img_unit=tk.Label(win, image=image_unit)

image_1block=tk.PhotoImage(file="img/1block.png")
label_img_1block=tk.Label(win, image=image_1block)

image_2block=tk.PhotoImage(file="img/2block.png")
label_img_2block=tk.Label(win, image=image_2block)

image_meshed=tk.PhotoImage(file="img/meshed.png")
label_img_meshed=tk.Label(win, image=image_meshed)

label_nLayer=tk.Label(win,text="층 수 : ")
entry_nLayer=tk.Entry(win)

label_x=tk.Label(win,text="x[mm] : ")
entry_x=tk.Entry(win)

label_y=tk.Label(win,text="y[mm] : ")
entry_y=tk.Entry(win)

label_a=tk.Label(win, text="a[mm] : ")
entry_a=tk.Entry(win)

label_b=tk.Label(win, text="b[mm] : ")
entry_b=tk.Entry(win)

label_c=tk.Label(win, text="c[mm] : ")
entry_c=tk.Entry(win)

label_row=tk.Label(win,text="row[행] : ")
entry_row=tk.Entry(win)

label_col=tk.Label(win,text="col[열] : ")
entry_col=tk.Entry(win)

label_folder=tk.Label(win, text='폴더명 : ')
entry_folder=tk.Entry(win)

CheckG=tk.IntVar()
check_gravity=tk.Checkbutton(win, text="gravity", variable=CheckG)

button_enter=tk.Button(win, text="입력", command=btnEnterClick)

frame=ScrollableFrame(win)
frame.place(x=170,y=240,width=1010,height=450)

label_No=tk.Label(win, text='No.')
label_Layer=tk.Label(win, text='Layer')
label_Thickness=tk.Label(win, text='두께\n[μm]')
label_Modulus=tk.Label(win, text='Modulus\n[MPa]')
label_CTE=tk.Label(win, text="CTE\n[ppm/℃]")
label_Poisson=tk.Label(win, text="Poisson\nratio")
label_Density=tk.Label(win, text="Density\n[g/㎤]")
label_Fill=tk.Label(win, text="Fill")
label_Portion_unit=tk.Label(win, text="Portion\n(unit)[%]")     #col 8 (Cu, SR) - unit, 1block, 2block
label_Portion_dummy=tk.Label(win, text="Portion\n(dummy)")      #col 9 (Cu,SR) - 1block, 2block

#output
label_Modulus_unit=tk.Label(win, text="Modulus\n(unit)")        #col 10 - unit, 1block, 2block
label_CTE_unit=tk.Label(win, text="CTE\n(unit)")                #col 11
label_Poisson_unit=tk.Label(win, text="Poisson\n(unit)")        #col 12
label_Density_unit=tk.Label(win, text="Density\n(unit)")        #col 13
label_Modulus_dummy=tk.Label(win, text="Modulus\n(dummy)")      #col 14 - 1block, 2block
label_CTE_dummy=tk.Label(win, text="CTE\n(dummy)")              #col 15
label_Poisson_dummy=tk.Label(win, text="Poisson\n(dummy)")      #col 16
label_Density_dummy=tk.Label(win, text="Density\n(dummy)")      #col 17

button_calc=tk.Button(win, text="물성 계산", command=btnCalcClick)

label_project=tk.Label(win, text='project name : ')
entry_project=tk.Entry(win)
button_SQBC=tk.Button(win, text='SQBC', command=btnSQBCClick)
button_warpage=tk.Button(win, text='Warpage', command=btnWarpageClick)
button_CTE=tk.Button(win, text='CTE', command=btnCTEClick)
button_modulus=tk.Button(win, text='Modulus', command=btnModulusClick)
label_modeling=tk.Label(win, text='modeling')
button_shell=tk.Button(win, text='Shell', command=btnShellClick)
button_solid=tk.Button(win, text='Solid', command=btnSolidClick)

label_result_SQBC=tk.Label(win)
label_result_warpage=tk.Label(win)
label_result_CTE=tk.Label(win)
label_result_modulus=tk.Label(win)

button_result_SQBC=tk.Button(win, text='result', command=btnResultSQBCClick)
button_result_warpage=tk.Button(win, text='result', command=btnResultWarpageClick)
button_result_CTE=tk.Button(win, text='result', command=btnResultCTEClick)
button_result_modulus=tk.Button(win, text='result', command=btnResultModulusClick)

CheckSQBC=tk.IntVar()
check_SQBC=tk.Checkbutton(win, variable=CheckSQBC)

CheckWarpage=tk.IntVar()
check_warpage=tk.Checkbutton(win, variable=CheckWarpage)

CheckCTE=tk.IntVar()
check_CTE=tk.Checkbutton(win, variable=CheckCTE)

CheckModulus=tk.IntVar()
check_modulus=tk.Checkbutton(win, variable=CheckModulus)

CheckCPU=tk.IntVar()
check_cpu=tk.Checkbutton(win, text="cpu32", variable=CheckCPU)

CheckGUI=tk.IntVar()
check_gui=tk.Checkbutton(win, text="GUI", variable=CheckGUI)

CheckJob=tk.IntVar()
check_job=tk.Checkbutton(win, text="job", variable=CheckJob)

button_highT=tk.Button(win, text='high T', command=btnHighTClick)

try:
    fc=open("customer.txt",'r')
except:
    messagebox.showwarning(title="error",message="failed to open customer list ('customer.txt')")
values_customer=fc.readlines()
fc.close()

for i in range(len(values_customer)):
    values_customer[i]=values_customer[i].strip()

label_customer = tk.Label(win, text="고객사 : ")
cb_customer=tkinter.ttk.Combobox(master=win, height=15, values=values_customer, state="readonly")

label_modelname=tk.Label(win, text='모델명 : ')
entry_modelname=tk.Entry(win)

label_structure=tk.Label(win, text='구조 : ')
values_structure=['Cored','Coreless_rev','Coreless_non','ETS']
cb_structure=tkinter.ttk.Combobox(master=win, height=15, values=values_structure, state="readonly")

button_save_input=tk.Button(win, text='save input', command=btnSaveInput)
button_load_input=tk.Button(win, text='load input', command=btnLoadInput)

button_init=tk.Button(win, text='초기화', command=btnInitClick)
button_init.place(x=35, y=600, width=70, height=30)

win.mainloop()
