import os
import math
import sys
import shutil
from PIL import Image


import argparse
parser = argparse.ArgumentParser()


# ex:
# python image_grid.py -i "cards/"
# python image_grid.py -i "folder/nested_folder/" -c 3 -v -o "output_folder/output_file"
# python image_grid.py -i "input/1/" -c 1 -i "input/2/" -c 2 -i "input/3/" -c 3

# ------------------------------------- VARIABLES -----------------------------------------------------

parser.add_argument("-c", "--copy", action='append', type=int, help="Number of duplicate copies")
parser.add_argument("-d", "--delete", help="Delete old output")
parser.add_argument("-i", "--input", action='append', type=str, help="Input folder")
parser.add_argument("-o", "--output", help="Output filename")
parser.add_argument("-v", "--verbose", action='store_true', help="Verbose logging")

parser.add_argument("-gh", "--grid_height", type=int, help="Grid Height")
parser.add_argument("-gw", "--grid_width", type=int, help="Grid Width")

args = parser.parse_args()

copies_list = args.copy if args.copy else {1}
input_folders = args.input if args.input else {"print_input"}
output_file_name = args.output if args.output else "print_output"

while len(copies_list) < len(input_folders):
    copies_list.append(copies_list[0])

if os.path.splitext(output_file_name)[1].lower() != "pdf":
    output_file_name += ".pdf"

verbose = True if args.verbose else False
delete_old_output = True if args.delete else False

grid_height = args.grid_height if args.grid_height else 3
grid_width = args.grid_width if args.grid_width else 3

# ------------------------------------- FUNCTIONS -----------------------------------------------------

def merge(base, new_image, page_index):

    merged = create_empty_page(new_image)

    if(page_index != 0):
        merged.paste(base)
            
    merged.paste(new_image, (new_image.size[0]*(page_index%grid_width), new_image.size[1]*(int)(page_index/grid_height)))

    if(page_index == 8):
        page_index = -1
        if(verbose):
            print("Saving page...")
        merged.save(output_file_name, append=True)
        merged = create_empty_page(new_image)

    return merged, (page_index+1)


def create_empty_page(image):
    w = image.size[0]*grid_width
    h = image.size[1]*grid_height
    empty_page = Image.new("RGB", (w, h), (255, 255, 255))
    return empty_page
    

def read_files(filepaths, input_folder):
    print("---------------------------------------------")
    print("Searching for files in '"+input_folder+"'...")

    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)
        filepaths.append(filepath)
        if(verbose):
            with Image.open(filepath) as im:
                    print(filename, im.format, f"{im.size}x{im.mode}")
    print("Found files: "+str(len(filepaths)))
    return filepaths


def validate_number_of_files(filepaths):
    number_of_files = len(filepaths)
    if(number_of_files < 2):
        print("Too few images found: '"+str(number_of_files)+"', no merging required.")
        return False
    return True

    
def create_directories(output_file_name, delete_old_output):

    output_path = os.path.abspath(output_file_name)
    output_directory = os.path.dirname(output_path)
    
    if not os.path.exists(output_directory):
        print("Creating directory '"+output_directory+"'...")
        create_directory(output_directory)

    if os.path.exists(output_file_name):
        os.remove(output_file_name)
    with open(output_file_name, 'w+') as f:
        pass


def create_directory(directory):
    for retry in range(100):
        try:
            os.makedirs(directory, exist_ok=True)
            break
        except Exception as error:
            if retry == 99:
                print(error)
    
# ------------------------------------- MAIN -----------------------------------------------------


print("---------------------------------------------")



filepaths_list = [[] for i in range(len(input_folders))]

for i in range(len(input_folders)):
    read_files(filepaths_list[i], input_folders[i])


if verbose:
    print("---------------------------------------------")
    print("Stored contents:")
    for filepaths in filepaths_list:
        for filepath in filepaths:
            print(filepath)

page = create_empty_page(Image.open(filepaths_list[0][0]))

create_directories(output_file_name, delete_old_output)

total_files = 0
for i in range(len(filepaths_list)):
    total_files += len(filepaths_list[i]) * copies_list[i]

num_digits = len(str(total_files))
total_index = 0
page_index = 0

if(verbose):
    print("---------------------------------------------")
    print("         merge | page | name")
                
for i in range(len(filepaths_list)):
    if validate_number_of_files(filepaths_list[i]):

            filepaths = filepaths_list[i]
            copies = copies_list[i]

            num_items_this_page = 0
            num_items = len(filepaths)
            

            
            for i_inner in range(num_items):
                for copy in range(copies):
                    with Image.open(filepaths[i_inner]) as file:
                        if(verbose):
                            print("Merging: "+str((total_index+1)).zfill(num_digits)+"/"+str(total_files)+" | #"+str(math.ceil((total_index+1)/(grid_height*grid_width)))+"/"+str(math.ceil(total_files/(grid_height*grid_width)))+" | '"+filepaths[i_inner]+"'")


                        page, page_index = merge(page, file, page_index)
                        total_index += 1

if(page_index != 0):
    if(verbose):
        print("Saving page...")
    page.save(output_file_name, append=True)
        
print("---------------------------------------------")
print("---------------------------------------------")
print("Successfully merged '"+str(total_files)+"' files into '"+output_file_name+"'")
print("---------------------------------------------")






















