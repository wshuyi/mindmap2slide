import sys
import os

def main(argv):
    num_vars = len(argv)
    python_command = "/anaconda/bin/python"
    working_dir = os.path.dirname(os.path.realpath(__file__))
    if num_vars > 1:
        convert_type = argv[1]
        if num_vars == 3: # need to convert outside markdown to local markdown first
            infile = argv[2]
            # convert to local markdown first
            cmd = "{} {}/convert-markdown-to-local-repo-markdown.py {}".format(python_command, working_dir, infile)
            os.system(cmd)

        # convert to output type selected:
        cmd = "{} {}/local_markdown_to_{}.py".format(python_command, working_dir, convert_type)
        os.system(cmd)


    else:
        print("Show me the type to convert")

if __name__ == "__main__":
    main(sys.argv)
