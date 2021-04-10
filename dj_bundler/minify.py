chars_to_remove = []

js_symbols = set("[](}{).,;/$=:' ")
js_couples = []
for char_one in js_symbols:
    for char_two in js_symbols:
        couple = [char_one, char_two]
        js_couples.append(couple)

css_symbols = set(",.:;}{#-' )(>"+'"')
css_couples = []
for char_one in css_symbols:
    for char_two in css_symbols:
        couple = [char_one, char_two]
        css_couples.append(couple)


def check_char_html(string, index):
    if index == 0:
        chars_to_remove.clear()
    if string[index] == " ":
        if index == 0 or string[index-1] == ">" or string[index-1] == " ":            
            if index == len(string) - 1 or string[index+1] == "<" or string[index+1] == " ":
                chars_to_remove.append(index) 


def check_char_js(string, index):
    if index == 0:
        chars_to_remove.clear()    
    if string[index] == " ":               
        if index == 0 and string[index+1] in js_symbols:
            chars_to_remove.append(index)
        elif index == len(string) - 1 and string[index-1] in js_symbols:
            chars_to_remove.append(index)
        elif [string[index-1], string[index+1]] in js_couples:
            chars_to_remove.append(index)
        elif string[index-1] in js_symbols and string[index+1].isalnum() is True:
            chars_to_remove.append(index)
        elif string[index+1] in js_symbols and string[index-1].isalnum() is True:
            chars_to_remove.append(index)


def check_char_css(string, index):
    if index == 0:
        chars_to_remove.clear()    
    if string[index] == " ":               
        if index == 0 and string[index+1] in css_symbols:
            chars_to_remove.append(index)
        elif index == len(string) - 1 and string[index-1] in css_symbols:
            chars_to_remove.append(index)
        elif [string[index-1], string[index+1]] in css_couples:
            chars_to_remove.append(index)
        elif string[index-1] in css_symbols and string[index+1].isalnum() is True:
            chars_to_remove.append(index)
        elif string[index+1] in css_symbols and string[index-1].isalnum() is True:
            chars_to_remove.append(index)
        elif string[index-1] == ":" and string[index+1].isalnum() is True:
            chars_to_remove.append(index)
        elif string[index+1] == "!" and string[index-1].isalnum() is True:
            chars_to_remove.append(index)


def minify(file_, file_type):      
    with open(file_, "r") as f:    
        if file_type == ".js":
            txt = f.readlines()
            new_txt = ""
            for line in txt:
                # remove all comments in js files
                if "//" in line:
                    lines = line.split('//')
                    line = lines[0]
                new_txt += line
            txt = new_txt
            with open(file_, "w") as w:
                w.write(txt)
            with open(file_,"r") as r:
                txt = r.read()
                txt = txt.replace('\n', '')
            for i in range(0, len(txt)):
                check_char_js(txt, i)
        else:
            txt = f.read()
            txt = txt.replace('\n', '')
            if file_type == ".html":             
                for i in range(0, len(txt)):
                    check_char_html(txt, i)        
            elif file_type == ".css":
                for i in range(0, len(txt)):
                    check_char_css(txt, i)
            else:
                chars_to_remove.clear()   

    for i in range(0, len(chars_to_remove)):
        a = txt[0:chars_to_remove[i]-i]
        b = txt[chars_to_remove[i]-i+1:len(txt)]
        txt = a+b  
    return txt  
