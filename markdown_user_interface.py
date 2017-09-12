import sys
import re
import os
import datetime
import basic_path_loader

def main(argv):
    basic_path_json = basic_path_loader.get_basic_path()
    num_vars = len(argv)
    python_command = basic_path_json["python_command"]
    markdown_tools_dir = basic_path_json["markdown_tools_dir"] 
    if num_vars > 1:
        convert_type = argv[1]
        # temp_markdown = basic_path_json["temp_markdown"]

        temp_markdown = basic_path_json["output_dir"] + "/temp.md"
        if num_vars == 3: # need to convert outside markdown to local markdown first
            infile = argv[2]
            # convert to local markdown first
            cmd = "{} {}/convert-markdown-to-local-repo-markdown.py {}".format(python_command, markdown_tools_dir, infile)
            # print(cmd)
            os.system(cmd)
        # convert to output type selected:


        cmd = "{} {}/local_markdown_to_{}.py".format(python_command, markdown_tools_dir, convert_type)
        # print(cmd)
        os.system(cmd)


    else:
        print("Show me the type to convert")

if __name__ == "__main__":
    main(sys.argv)
