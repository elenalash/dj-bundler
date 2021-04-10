# TODO
# include comments in html and css
# allow for a few different apps (different static and template folders)
# catch errors
# provide logging of last session
# implement file stamp changing only for static files that have been changed


from os import listdir, path, mkdir, remove, scandir
from pathlib import Path
from shutil import copyfile, rmtree
import json
from .minify import minify
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

working_folders = []

file_types = ["css", "js"]

file_names = {
    "css" : "styles",
    "js" : "scripts"
}

minifiable_types = ["css", "js", "html"]

def main(BASE_DIR_):
    global templates_obj, static_obj, assets_obj, working_folders, file_types, file_names, BASE_DIR, static_libraries_path_dev
      
    BASE_DIR = BASE_DIR_
    settings_file = path.join(Path(__file__).resolve().parent, "settings.json")
    with open(settings_file) as f:
        settings = json.load(f) 

    # READ TEMPLATES' SETTINGS, GET DEV PATHS, GET PROD PATHS
    templates = settings["templates"]
    templates_file_type = ".html"
    templates_path_dev_raw = templates["path"]
    templates_minify = templates["minify"]
    templates_path_prod_raw = templates["production_path"]
    templates_obj = Working_folder("templates", templates_path_dev_raw, templates_path_prod_raw, templates_minify, False)
    working_folders.append(templates_obj)
  
    # READ STATIC FILES' SETTINGS, GET DEV PATHS, GET PROD PATHS
    static = settings["static"]
    static_path_dev_raw = static["path"]
    static_minify = static["minify"]
    static_bundle = static["bundle"]
    static_path_prod_raw = static["production_path"]
    static_libraries_raw = static["libraries"]
    static_obj = Working_folder("static", static_path_dev_raw, static_path_prod_raw, static_minify, static_bundle)
    static_libraries_path_dev = get_folder_path_from_raw(static_libraries_raw)
    working_folders.append(static_obj)


    arr_html_paths_dev = get_files(templates_obj.path_dev, templates_file_type)
    arr_hrml_objs = []
    for html_path_dev in arr_html_paths_dev:
        html_obj = Html_file(html_path_dev)
        arr_hrml_objs.append(html_obj)


    for html_obj in arr_hrml_objs:
        html_obj.copy_file_to_prod()
        html_obj.get_links_from_html()

        for list_ in html_obj.links_lists:
            if list_.list:               
                if list_.folder_obj.bundle and list_.files_type in minifiable_types:
                    bundle_and_save(list_, html_obj.file_stem)
                else:
                    copy_and_save(list_)
                if list_.link_for_html: # if a few files bundled into one
                    with open(html_obj.path_prod, "r") as f:
                        txt = f.read()
                    for link in list_.list:
                        if list_.list.index(link) == len(list_.list)-1:
                            parts = txt.split(link.html_link_full)
                            txt = parts[0] + list_.link_for_html + parts[1]
                        else:
                            parts = txt.split(link.html_link_full)
                            txt = parts[0] + parts[1]
                    with open(html_obj.path_prod, "w") as f:
                        f.write(txt)
                else:
                    for link in list_.list:
                        if len(str(link.file_name_prod)) > 0:
                            link_prod = link.get_html_link()
                            with open(html_obj.path_prod, "r") as f:
                                txt = f.read()
                            parts = txt.split(link.html_link_full)
                            txt = parts[0] + link_prod + parts[1]
                            with open(html_obj.path_prod, "w") as f:
                                f.write(txt)


    for working_folder in working_folders:               
        if working_folder.minify:            
            for file_path_prod in working_folder.list_of_files_prod:
                file_type = file_path_prod.suffix[1:len(file_path_prod.suffix)]
                if file_type in minifiable_types:
                    txt = minify(file_path_prod,file_path_prod.suffix)
                    with open(file_path_prod, "w") as f:
                        f.write(txt)


def get_datetime_stamp(file_name):
    suffix = Path(file_name).suffix
    stem = Path(file_name).stem
    stamp = datetime.now().strftime("%m%y%d%H%M%S")
    file_name = Path(path.join(stem + "_" + stamp + suffix))
    return file_name

                
def copy_and_save(list_):
    for link_ in list_.list:       
        src = Path(path.join(link_.parent_folder_dev, link_.file_name))
        if link_.is_library is True:
            file_name = link_.file_name
        else:
            link_.file_name_prod = get_datetime_stamp(link_.file_name)
            file_name = link_.file_name_prod        
        dst = Path(path.join(link_.parent_folder_prod, file_name))
        list_.folder_obj.list_of_files_prod.append(dst)        
        copy_file(src,dst)      
        

def bundle_and_save(list_, html_stem):
    if len(list_.list) == 1:
        copy_and_save(list_)
    else:
        txt = ""
        for link_ in list_.list:
            file_path_dev = Path(path.join(link_.parent_folder_dev,link_.file_name))            
            with open(file_path_dev)  as f:
                txt += f.read() + "\n"
        file_name = file_names[list_.files_type]
        bundled_file_name = html_stem + "-" + file_name + "." + list_.files_type
        bundled_file_name = get_datetime_stamp(bundled_file_name)
        bundled_file_link = list_.files_type + "/" + str(bundled_file_name)
        file_path_prod = Path(path.join(list_.folder_obj.path_prod, list_.files_type, bundled_file_name))
        list_.folder_obj.list_of_files_prod.append(file_path_prod)
        update_tree(file_path_prod) 
        with open(file_path_prod, "w") as f:
            f.write(txt)
        list_.get_html_link(bundled_file_link)    
    

def get_folder_path_from_raw(folder_path_raw):
        if folder_path_raw[0] == "." and folder_path_raw[1] == "/":
            folder_path = Path(path.join(BASE_DIR, folder_path_raw[2:len(folder_path_raw)]))
            return folder_path

def get_files(folder_path, file_type):
        arr = [Path(path.join(folder_path, x)) for x in listdir(folder_path) if x.endswith(file_type)]
        return arr   

def update_tree(dst):
    parts = dst.parents._parts
    path_ = Path(parts[0])
    for i in range(len(parts)-1):        
        if path_.exists() is False:
            mkdir(path_)
        path_ = Path(path.join(path_,parts[i+1]))

def copy_file(src, dst):  
    update_tree(dst)    
    copyfile(src, dst)

def get_links(html_prod):
    with open(html_prod) as f:
        txt = f.read()
    splitter_one = "{% static "
    splitter_two = " %}"
    split_list = txt.split(splitter_one)
    links = []    
    txt_length = 0
    for block in split_list:
        if split_list.index(block) == 0:
            txt_length += len(splitter_one)
        if split_list.index(block) != 0:                           
            parts = block.split(splitter_two)            
            start = split_list[split_list.index(block) - 1].rfind("<") + txt_length - len(
                split_list[split_list.index(block) - 1]) - len(splitter_one)
            end = split_list[split_list.index(block)].find(">") + txt_length
            link = Link(parts[0][1:len(parts[0]) - 1], txt[start:end+1])
            links.append(link)            
            txt_length += len(splitter_one)
        txt_length += len(block)
    return links


class Html_file:
    def copy_file_to_prod(self):
        copy_file(self.path_dev, self.path_prod)
        self.working_folder.list_of_files_prod.append(self.path_prod)

    def get_links_sorted(self):
        for link in self.links_all:
            if link.file_type == None:
                list_other = [x for x in self.links_lists if x.files_type == "other"][0] 
                list_other.list.append(link)
            else:                          
                for list_ in self.links_lists: 
                    if list_.files_type == link.file_type:
                        list_.list.append(link)                    
                        break            
  
    def get_links_from_html(self):
        self.links_all = get_links(self.path_prod)
        self.links_lists = []
        for file_type in file_types:
            self.links_lists.append(List_of_files(file_type,self.file_stem))
        self.links_lists.append(List_of_files("other",self.file_stem))
        self.get_links_sorted()

    def __init__(self, path_dev):
        self.path_dev = path_dev
        self.file_name = self.path_dev.name
        self.file_stem = self.path_dev.stem
        self.working_folder = templates_obj
        self.parent_dev = templates_obj.path_dev
        self.parent_prod = templates_obj.path_prod
        self.path_prod = Path(path.join(self.parent_prod, self.file_name))        


class List_of_files:
    def get_html_link(self, file_link):
        self.bundled_file_link = file_link
        if self.files_type == "css":
            self.link_for_html = '<link rel="stylesheet" type="text/css"  href="' + "{% static '" + self.bundled_file_link + "'" + ' %}" />'
        elif self.files_type == "js":
            self.link_for_html = '<script src="{% static ' + "'" + self.bundled_file_link + "' %}" + '"></script>'
        else:
            self.link_for_html = self.bundled_file_link


    def __init__(self, files_type, parent_html_stem):
        self.files_type = files_type # css, js, other
        self.parent_html_stem = parent_html_stem
        self.folder_obj = static_obj
        self.list = []
        self.link_for_html = False


class Link:
    def get_html_link(self):
        link_dev = self.html_link_full
        parts = link_dev.split(self.file_name)
        link_prod = parts[0] + str(self.file_name_prod) + parts[1]
        return link_prod


    def get_file_type(self):
        if self.html_link_short.endswith(".css"):
            return "css"
        elif self.html_link_short.endswith(".js"):
            return "js"
        return None
    
    def get_file_name(self):
        parts = self.html_link_short.split("/")
        file_name = parts[len(parts)-1]
        return file_name

    def get_library_status(self):
        for parent in Path(self.html_link_short).parents:
            if str(parent) == str(static_libraries_path_dev.name):                
                return True
        return False

    def __init__(self, html_link_short, html_link_full):
        self.html_link_short = html_link_short
        self.html_link_full = html_link_full
        self.file_type = self.get_file_type() # None for not-css and non-js files
        self.folder_obj = static_obj
        self.file_name = self.get_file_name()
        self.parent_folder_dev = Path(path.join(self.folder_obj.path_dev, self.html_link_short)).parent
        self.parent_folder_prod = Path(path.join(self.folder_obj.path_prod, self.html_link_short)).parent
        self.is_library =  self.get_library_status()
        self.file_name_prod = ''
 

class Working_folder:
    def empty(self):
        if self.path_prod.exists():
            all_files = scandir(self.path_prod)
            for i in all_files:             
                if i.is_file():
                    remove(i.path)
                if i.is_dir():
                    rmtree(i.path)            
                

    def __init__(self, name, path_dev_raw, path_prod_raw, minify, bundle):
        self.name = name
        self.path_dev_raw = path_dev_raw
        self.path_prod_raw = path_prod_raw
        self.minify = minify
        self.bundle = bundle
        self.path_dev = get_folder_path_from_raw(self.path_dev_raw)
        self.path_prod = get_folder_path_from_raw(self.path_prod_raw)
        self.empty()
        self.list_of_files_prod = []


if __name__ == "__main__":
    main(BASE_DIR)
