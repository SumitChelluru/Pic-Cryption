import cv2
import os
from Engine import Engine
from flask import Flask, render_template, request,url_for

app = Flask(__name__)

# Your existing code for encrypt function and other logic goes here
def decompose(path):
    '''
    decompose imagename as path+imagename+format
    '''
    path=os.path.abspath(path)
    upper=''
    if "\\" not in path:
        upper=''
        exe = str(path.split('.')[-1])
        img_name = path.split('.')[0:-1]

    else:
        upper=(path.split("\\")[0:-1])
        upper ="\\".join(upper)
        img_name = path.split('\\')[-1]
        exe = str(img_name.split('.')[-1])
        img_name = img_name.split('.')[0:-1]
    img_name = '.'.join(img_name)
    exe=exe.lower()
    return (upper,img_name, exe)


def safeSave(img,I,override='yes',delete_jpg=False,end=''):
    '''
    attempts to save img with given name imgname
    jpg or jpeg are not allowed to be saved
    '''

    path,imgname,exe=decompose(I)
    if (exe.lower() == 'jpg') | (exe.lower() == 'jpeg'):


        I = path+'\\'+imgname+'.'+'webp'
        safeSave(img,I,override,True,exe)


    if override=='yes':
        try:
            cv2.imwrite(I,img)
            if delete_jpg:
                os.remove(path+'\\'+imgname+'.'+end)

            return I
        except Exception as e:
            raise e


    elif os.path.isfile(I) & (override=='ask'):
        arg2=str(input(f'{imgname} already exsists in {path} override? [Y/n]')).lower()

        if(not(arg2=="y" or arg2=="n")):#invalid case
            print('Please choose from given opts only')
            return safeSave(img,I,override)
        elif arg2=='n':#override
            return safeSave(img,I,'no')
        else:#dont override
            return safeSave(img,I,'yes')

    elif(override=='no'):#dont override

        while(os.path.isfile(I)):
            imgname=input(f"Enter new name ({I} already exists)")
            I=path+'\\'+imgname+'.'+exe
        return safeSave(img, I,'yes')
    elif override=='ask':#and imgname doesn't exists
        return safeSave(img, I,'yes')
    else:
        return (0,"Invalid state",'')

def read_image(path):
    '''
    read image and catch any execeptions
    '''
    if os.path.isfile(path)==False:
        raise Exception("File not found or the program doesn't have required permissions")

    try:
        img = cv2.imread(path)
    except Exception as e:
        raise e
    else:
        return img

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/execute', methods=['POST'])
def execute():
    mode = request.form['mode']
    imgname = request.form['imgname']
    message = request.form['message']
    key = request.form['key']
    password = request.form['password']

    # Your existing logic for handling the inputs and calling the execute_operation function goes here
    engine = Engine()
    engine.setImgRead(read_image).setImgWrite(safeSave).setLogger(print)
    actionMap = {
        'arnold_cat': ('ArnoldCat', 'encrypt'),
        'arnold_cat_de': ('ArnoldCat', 'decrypt'),
        'aes_en': ('AES', 'encrypt'),
        'aes_de': ('AES', 'decrypt'),
        'stegano_write': ('Stegano', 'encrypt'),
        'stegano_read': ('Stegano', 'decrypt'),
    }
    argsDict = {
        'imgname': imgname,
        'message': message,
        'key': key,
        'password': password
    }
    mode, op = actionMap[mode]
    engine.loadStratergy(mode).exe(op, **argsDict)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
