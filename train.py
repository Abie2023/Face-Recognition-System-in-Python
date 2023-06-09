import tkinter as tk
from tkinter import Message ,Text, PhotoImage, Canvas, Label, LabelFrame
import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font

window = tk.Tk()
#helv36 = tk.Font(family='Helvetica', size=36, weight='bold')
window.title("Face Recognition System")

dialog_title = 'QUIT'
dialog_text = 'Are you sure?'

window.grid_rowconfigure(0, weight=0)
window.grid_columnconfigure(0, weight=0)

bg = PhotoImage(file='Harvey.png')
canvas1 = Canvas(window,width=1920,height=1080)
canvas1.pack(fill="both",expand=True)
canvas1.create_image(0,0,image=bg,anchor='nw')

#-------------------------------Functions---------------------------------------------------------------------
def clear():
    txt.delete(0, 'end')    
    res = ""
    message.configure(text= res)

def clear2():
    txt2.delete(0, 'end')    
    res = ""
    message.configure(text= res)    
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
 
def getImagesAndLabels(path):
    #get the path of all the files in the folder
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
    #print(imagePaths)
    
    #create empth face list
    faces=[]
    #create empty ID list
    Ids=[]
    #now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        #loading the image and converting it to gray scale
        pilImage=Image.open(imagePath).convert('L')
        #Now we are converting the PIL image into numpy array
        imageNp=np.array(pilImage,'uint8')
        #getting the Id from the image
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)        
    return faces,Ids

def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    #recognizer = cv2.face.LBPHFaceRecognizer_create()
    #recognizer = cv2.face.createLBPHFaceRecognizer()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("TrainingImageLabel\Trainner.yml")
    res = "Image Trained"#+",".join(str(f) for f in Id)
    message.configure(text= res)

def TakeImages():        
    Id=(txt.get())
    name=(txt2.get())
    if(is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        
                #incrementing sample number 
                sampleNum=sampleNum+1
                #saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("TrainingImage\ "+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                #display the frame
                cv2.imshow('frame',img)
            #wait for 100 miliseconds 
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum>60:
                break
        cam.release()
        cv2.destroyAllWindows() 
        res = "Images Saved for ID : " + Id +" Name : "+ name
        row = [Id , name]
        with open('StudentDetails\StudentDetails.csv','a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text= res)
    else:
        if(is_number(Id)):
            res = "Enter Alphabetical Name"
            message.configure(text= res)
        if(name.isalpha()):
            res = "Enter Numeric Id"
            message.configure(text= res)

def TrackImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    recognizer.read("TrainingImageLabel\Trainner.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);    
    df=pd.read_csv("StudentDetails\StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX        
    col_names =  ['Id','Name','Date','Time']
    attendance = pd.DataFrame(columns = col_names)    
    while True:
        ret, im =cam.read()
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, 1.2,5)    
        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])                                   
            if(conf < 50):
                ts = time.time()      
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa=df.loc[df['Id'] == Id]['Name'].values
                tt=str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id,aa,date,timeStamp]
                
            else:
                Id='Unknown'                
                tt=str(Id)  
            if(conf > 75):
                noOfFile=len(os.listdir("ImagesUnknown"))+1
                cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
            cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)        
        attendance=attendance.drop_duplicates(subset=['Id'],keep='first')    
        cv2.imshow('im',im) 
        if (cv2.waitKey(1)==ord('q')):
            break
    ts = time.time()      
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour,Minute,Second=timeStamp.split(":")
    fileName="Attendance\Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName,index=False)
    cam.release()
    cv2.destroyAllWindows()
    #print(attendance)
    res=attendance
    message2.configure(text= res)

#-------------------------------------------------Frames-------------------------------------------------
 # Top label frame
Top_frame = LabelFrame(
            bd=5,
            bg="grey",
            font=("times new roman", 12, "bold"),
        )
Top_frame.place(x=280, y=100, width=920, height=380)
topic_frame = LabelFrame(
            Top_frame,        
            bg="grey",
            text="New Registration Panel",
            font=("times new roman", 15, "bold"),
        )
topic_frame.place(x=5, y=0, width=900, height=365)

 #Bottom label frame
Bottom_frame = LabelFrame(
            bd=5,
            bg="grey",
            font=("times new roman", 12, "bold"),
        )
Bottom_frame.place(x=280, y=510, width=920, height=260)
topic_frame = LabelFrame(
            Bottom_frame,        
            bg="grey",
            text="Attendance Marking Panel",
            font=("times new roman", 15, "bold"),
        )
topic_frame.place(x=5, y=0, width=900, height=245)


#-------------------------------Labels and buttons---------------------------------------------------------------------
message = tk.Label(window, text="Face Recognition Based Attendance Management System" ,bg="Grey"  ,fg="black"  ,width=50  ,height=1,font=('times', 30, 'bold')) 
message.place(x=150, y=20)

lbl = tk.Label(window, text="Enter ID",width=20  ,height=1  ,fg="red"  ,bg="white" ,font=('times', 18, ' bold ') ) 
lbl.place(x=300, y=150)

txt = tk.Entry(window,width=20  ,bg="white" ,fg="red",font=('times', 16, ' bold '))
txt.place(x=670, y=150)

lbl2 = tk.Label(window, text="Enter Name",width=20,fg="red",bg="white",height=1 ,font=('times', 18, ' bold ')) 
lbl2.place(x=300, y=220)

txt2 = tk.Entry(window,width=20 ,bg="white"  ,fg="red",font=('times', 16, ' bold ')  )
txt2.place(x=670, y=220)

clearButton = tk.Button(window, text="Clear", command=clear  ,fg="white"  ,bg="black"  ,width=15  ,height=1 ,activebackground = "Red" ,font=('times', 17, ' bold '))
clearButton.place(x=950, y=145)

clearButton2 = tk.Button(window, text="Clear", command=clear2  ,fg="white"  ,bg="black"  ,width=15  ,height=1, activebackground = "Red" ,font=('times', 17, ' bold '))
clearButton2.place(x=950, y=215)  

lbl3 = tk.Label(window, text="Register New Students",width=20  ,fg="red"  ,bg="white"  ,height=1 ,font=('times', 18, 'bold')) 
lbl3.place(x=300, y=310)

takeImg = tk.Button(window, text="Take Images", command=TakeImages  ,fg="white"  ,bg="black"  ,width=15  ,height=2, font=('times', 18, ' bold '))
takeImg.place(x=670, y=290)
trainImg = tk.Button(window, text="Train Images", command=TrainImages  ,fg="white"  ,bg="black"  ,width=15  ,height=2, font=('times', 18, ' bold '))
trainImg.place(x=950, y=290)

lbl3 = tk.Label(window, text="Notification",width=20  ,fg="red"  ,bg="white"  ,height=1 ,font=('times', 18, 'bold')) 
lbl3.place(x=300, y=410)

message = tk.Label(window, text="" ,bg="white"  ,fg="black"  ,width=40  ,height=2, activebackground = "green" ,font=('times', 16, ' bold ')) 
message.place(x=670, y=400)

lbl3 = tk.Label(window, text="Attendance Status",width=20  ,fg="red"  ,bg="white"  ,height=1 ,font=('times', 18, ' bold')) 
lbl3.place(x=300, y=695)

message2 = tk.Label(window, text="" ,fg="black"   ,bg="white",activeforeground = "green", width=40  ,height=3  ,font=('times', 16, ' bold ')) 
message2.place(x=670, y=670)
  
lbl3 = tk.Label(window, text="Attendance Module",width=20  ,fg="red"  ,bg="white"  ,height=1 ,font=('times', 18, 'bold')) 
lbl3.place(x=300, y=580)

trackImg = tk.Button(window, text="Take Attendance", command=TrackImages  ,fg="white"  ,bg="black"  ,width=15  ,height=2, activebackground = "Red" ,font=('times', 18, ' bold '))
trackImg.place(x=670, y=565)

quitWindow = tk.Button(window, text="Quit", command=window.destroy  ,fg="white"  ,bg="Red"  ,width=10  ,height=2, activebackground = "Red" ,font=('times', 16, ' bold '))
quitWindow.place(x=1300, y=150)
 
window.mainloop()