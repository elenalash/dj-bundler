# TODO
# check if minified code works
# include comments in html and css
# allow for a few different apps (different static and template folders)
# incorporate layout.html and jinja2 code in to html minify function
# catch errors
# provide logging of last session


from os import listdir, path, mkdir
from pathlib import Path
from shutil import copyfile
import json
from minify import minify

BASE_DIR = Path(__file__).resolve().parent.parent

working_folders = []

file_types = ["css", "js"]

file_names = {
    "css" : "styles",
    "js" : "scripts"
}

def main():
    global templates_obj, static_obj, assets_obj, working_folders, file_types, file_names
      

    settings_file = path.join(BASE_DIR, "dj_bundler/settings.json")
    with open(settings_file) as f:
        settings = json.load(f) 

    # READ TEMPLATES' SETTINGS, GET DEV PATHS, GET PROD PATHS
    templates = settings["templates"]
    templates_exists = templates["exists"]
    templates_file_type = ".html"
    if templates_exists:
        templates_path_raw = templates["path"]
        templates_minify = templates["minify"]
        templates_obj = Working_folder("templates", templates_path_raw, templates_minify, False)
        working_folders.append(templates_obj)
        

    # READ ASSETS' SETTINGS, GET DEV PATHS, GET PROD PATHS
    assets = settings["assets"]
    assets_exists = assets["exists"]
    if assets_exists:
        assets_path_raw = assets["path"]
        assets_minify = assets["minify"]
        assets_bundle = assets["bundle"]
        assets_obj = Working_folder("assets", assets_path_raw, assets_minify, assets_bundle)
        working_folders.append(assets_obj)


    # READ STATIC FILES' SETTINGS, GET DEV PATHS, GET PROD PATHS
    static = settings["static"]
    static_exists = static["exists"]
    if static_exists:
        static_path_raw = static["path"]
        static_minify = static["minify"]
        static_bundle = static["bundle"]
        static_obj = Working_folder("static", static_path_raw, static_minify, static_bundle)
        working_folders.append(static_obj)


    arr_html_paths_dev = get_files(templates_obj.folder.path_dev, templates_file_type)
    arr_hrml_objs = []
    for html_path_dev in arr_html_paths_dev:
        html_obj = Html_file(html_path_dev, templates_obj)
        arr_hrml_objs.append(html_obj)


    for html_obj in arr_hrml_objs:
        html_obj.copy_file_to_prod()
        html_obj.get_links_from_html()

        for list_ in html_obj.links_lists:
            if list_.list:                
                if list_.folder_obj is not None:
                    if list_.folder_obj.bundle:
                        bundle_and_save(list_, html_obj.file_stem)
                    else:
                        copy_and_save(list_)
                    if list_.link_for_html:
                        with open(html_obj.file.file_path_prod, "r") as f:
                            txt = f.read()
                        for link in list_.list:
                            if list_.list.index(link) == len(list_.list)-1:
                                parts = txt.split(link.html_link_full)
                                txt = parts[0] + list_.link_for_html + parts[1]
                            else:
                                parts = txt.split(link.html_link_full)
                                txt = parts[0] + parts[1]
                        with open(html_obj.file.file_path_prod, "w") as f:
                            f.write(txt)

    for working_folder in working_folders:
        if working_folder.minify:
            if working_folder.subfolders:
                for subfolder in working_folder.subfolders:
                    arr = get_files(subfolder.path_prod, subfolder.subfolder_type)
                    for file_ in arr:
                        file_path_prod = Path(path.join(subfolder.path_prod, file_))                                               
                        txt = minify(file_path_prod,subfolder.subfolder_type)
                        with open(file_path_prod, "w") as f:
                            f.write(txt)
            else:
                arr = get_files(working_folder.folder.path_prod, "html")
                for file_ in arr:
                    file_path_prod = Path(path.join(working_folder.folder.path_prod, file_))
                    txt = minify(file_path_prod, "html")
                    with open(file_path_prod, "w") as f:
                        f.write(txt)                      
           
                
def copy_and_save(list_):
    for link_ in list_.list:
        src = Path(path.join(link_.parent_folder_dev,link_.file_name))
        dst = Path(path.join(link_.parent_folder_prod,link_.file_name))
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
        bundled_file_name = html_stem + "-" + list_.list_type + "-" + file_name + "." + list_.files_type
        bundled_file_link = list_.files_type + "/" + bundled_file_name
        file_path_prod = Path(path.join(list_.folder_obj.folder.path_prod, list_.files_type,bundled_file_name))
        with open(file_path_prod, "w") as f:
            f.write(txt)
        list_.get_html_link(bundled_file_link)    
    

def get_folder_path_from_raw(folder_path_raw):
        if folder_path_raw[0] == "." and folder_path_raw[1] == "/":
            folder_path_dev = Path(path.join(BASE_DIR, folder_path_raw[2:len(folder_path_raw)]))
            return folder_path_dev

def get_files(folder_path, file_type):
        arr = [Path(path.join(folder_path, x)) for x in listdir(folder_path) if x.endswith(file_type)]
        return arr   

def copy_file(src, dst):  
    parts = dst.parents._parts
    path_ = Path(parts[0])
    for i in range(len(parts)-1):
        print(path_)
        if path_.exists() is False:
            mkdir(path_)
        path_ = Path(path.join(path_,parts[i+1]))
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
            # get the link                
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
        copy_file(self.file.file_path_dev, self.file.file_path_prod)

    def get_links_sorted(self):
        for link in self.links_all:
            found = False
            for list_ in self.links_lists:
                if list_.list_type == link.folder_obj.name:
                    if list_.files_type == link.file_type:
                        list_.list.append(link)
                        found = True
                        break
            if found is False:
                for list_ in self.links_lists:
                    if list_.files_type == "other":
                        list_.append(link)
                        break
  
    def get_links_from_html(self):
        self.links_all = get_links(self.file.file_path_prod)
        self.links_lists = []
        for working_folder in working_folders:
            if working_folder.name != "templates":
                for f_type in file_types:
                    self.links_lists.append(List_of_files(working_folder.name,f_type,self.file_stem))
        self.links_lists.append(List_of_files(None,"other",self.file_stem))
        self.get_links_sorted()

    def __init__(self, path_dev, working_folder_obj):
        self.path_dev = path_dev
        self.file_name = self.path_dev.name
        self.file_stem = self.path_dev.stem
        self.working_folder = working_folder_obj
        self.file = File(self.working_folder.path_raw, self.file_name)       


class List_of_files:
    def get_html_link(self, file_link):
        self.bundled_file_link = file_link
        self.link_for_html = '<link rel="stylesheet" href="' + "{% static '" + self.bundled_file_link + "'" + ' %}" />'

    def get_folder_obj(self):
        for working_folder in working_folders:
            if working_folder.name == self.list_type:
                return working_folder

    def __init__(self,list_type, files_type, parent_html_stem):
        self.list_type = list_type
        self.files_type = files_type
        self.parent_html_stem = parent_html_stem
        self.folder_obj = self.get_folder_obj()
        self.list = []
        self.link_for_html = False


class File:
    def __init__(self, folder_path_raw, file_name):        
        self.parent_folder = Parent_folder(folder_path_raw, True)
        self.file_path_dev = Path(path.join(self.parent_folder.path_dev, file_name))
        self.file_path_prod = Path(path.join(self.parent_folder.path_prod, file_name))
   

class Link:
    def get_file_type(self):
        if self.html_link_short.endswith(".css"):
            return "css"
        elif self.html_link_short.endswith(".js"):
            return "js"
        return None

    def get_folder_obj(self):       
        if Path(path.join(static_obj.folder.path_dev, self.html_link_short)).exists():
            return static_obj
        if Path(path.join(assets_obj.folder.path_dev,self.html_link_short)).exists():
            return assets_obj
        return None
    
    def get_file_name(self):
        parts = self.html_link_short.split("/")
        file_name = parts[len(parts)-1]
        return file_name

    def __init__(self, html_link_short, html_link_full):
        self.html_link_short = html_link_short
        self.html_link_full = html_link_full
        self.file_type = self.get_file_type()
        self.folder_obj = self.get_folder_obj()
        self.file_name = self.get_file_name()
        self.parent_parent_folder = Parent_folder(Path(path.join(self.folder_obj.folder.path_dev)), False)
        self.parent_folder_dev = Path(path.join(self.parent_parent_folder.path_dev, self.html_link_short)).parent              
        self.parent_folder_prod = Path(path.join(self.parent_parent_folder.path_prod, self.html_link_short)).parent 


class Parent_folder:
    def __init__(self, path_, raw):
        if raw:
            self.path_raw = path_
            self.path_dev = get_folder_path_from_raw(self.path_raw)            
        else:
            self.path_raw = None
            self.path_dev = path_            
        self.path_prod = Path(path.join(Path(self.path_dev).parent, Path(self.path_dev).name + "_production",))
        if self.path_prod.exists() is False:
            mkdir(self.path_prod)


class Working_folder:
    def __init__(self, name, path_raw, minify, bundle):
        self.name = name
        self.path_raw = path_raw
        self.minify = minify
        self.bundle = bundle
        self.folder = Parent_folder(self.path_raw,True)
        self.subfolders = []
        if self.name != "templates":
            self.subfolders.append(Subfolder("css", self.folder.path_dev, self.folder.path_prod))
            self.subfolders.append(Subfolder("js", self.folder.path_dev, self.folder.path_prod))


class Subfolder:
    def __init__(self, subfolder_type, parent_folder_dev, parent_folder_prod):
        self.subfolder_type = subfolder_type
        self.parent_folder_dev = parent_folder_dev
        self.parent_folder_prod = parent_folder_prod
        self.path_dev = Path(path.join(self.parent_folder_dev,self.subfolder_type))
        self.path_prod = Path(path.join(self.parent_folder_prod,self.subfolder_type))
        if self.path_prod.exists() is False:
            mkdir(self.path_prod)


if __name__ == "__main__":
    main()

