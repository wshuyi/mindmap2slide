import sys
import re
import os
import datetime

def convert_pic_links_local_repo(infile, outfile, local_repo_path):

    link_key_pairs = {}

    with open(infile) as f:
        data = f.read()

    regex = r"(!\[.*\]\(.*)%20\d(\.\w*\))"
    subst = "\\1\\2"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)

    links = re.findall(r'\!\[.*\]\((.*)\)', data)

    # Convert all the relative links to absolute ones:
    source_path = re.search(r'.*/', infile).group()
    rel_links = {}
    for link in links:
        if (not link.startswith('http')) and (not link.startswith('ftp')): # not a web url
            if not link.startswith('/'): # not absolute path
                abs_link = os.path.abspath(source_path + link)
                rel_links[link] = abs_link

    for link in rel_links.iterkeys():
        data = data.replace(link, rel_links[link])

    # get links again, this time only absolute links
    links = re.findall(r'\!\[.*\]\((.*)\)', data)

    special_character_list = [" ", "&", "%20"]

    for link in links:
        # handle the Untitled image link from notions, hosted on amazon
        regex_notion_untitled = r"^http.+amazonaws.*/Untitled"
        # handle the Dragged Image from Ulysses
        regex_dragged_image = r"DraggedImage"
        regex_paramed_image = r"^http:.*\?.+" #image with params


        if re.search(regex_notion_untitled, link):
            out_image_name = link.split('/')[-2]
        elif re.search(regex_dragged_image, link):
            timestr = get_file_timestring(link)
            out_image_name = 'DraggedImage-' + timestr
        elif re.search(regex_paramed_image, link):
            out_image_name = link.split('?')[0].split('/')[-1]
        else:
            out_image_name = link.split('/')[-1]
        for sp_char in special_character_list:
            if out_image_name.find(sp_char):
                out_image_name = out_image_name.replace(sp_char, '_')
        # handle images without extended names like jpg, png, ...
        regex = r"(.*)(?<!jpg|png|bmp|gif|svg|peg)$"
        if re.search(regex, out_image_name):
            out_image_name = "{}.jpg".format(out_image_name)
        link_key_pairs[link] = out_image_name
        local_repo_link = "{}/{}".format(local_repo_path, out_image_name)
        data = data.replace(link, local_repo_link)

    with open(outfile, 'w') as f:
        f.write(data)

    return link_key_pairs

def sync_pics_to_local_repo(infile, link_key_pairs, local_repo_path):
    web_link_pattern = re.compile(r'(ht|f)tps?://')
    local_link_pattern = re.compile(r'^(\.*/)*(.*/)*(.*)')
    local_repo_link_pattern = re.compile(local_repo_path)

    if not os.path.exists(local_repo_path):
        os.makedirs(local_repo_path)

    links = link_key_pairs.iterkeys()

    for link in links:
        if web_link_pattern.search(link): # is a web link

            out_image_filename = link_key_pairs[link]
            cmd = '/usr/local/bin/wget -c -O {}/{} {}'.format(local_repo_path, out_image_filename, link)
            try:
                os.system(cmd)
            except:
                print('can not download the link: {}'.format(link))
        elif local_link_pattern.search(link): # is a local link
            if local_repo_link_pattern.search(link): # is already a local repo link
                print('it is already in local repo, do nothing')
            else: # is a local link, but not in local repo
                # # handle blank spaces in link
                link_to_sync = link.replace("%20", " ")
                cmd = '/usr/bin/rsync -av "{}" {}/"{}"'.format(link_to_sync, local_repo_path, link_key_pairs[link])
                try:
                    os.system(cmd)
                except:
                    print('can not sync the link: {}'.format(link))
        else: # not a valid link
            print('do nothing for a invalid link: {}'.format(link))
            pass

def get_file_timestring(filename):
    create_time = os.path.getmtime(filename)
    d = datetime.datetime.fromtimestamp(create_time)
    date_format = '%Y-%m-%d-%H-%M-%S'
    timestr = d.strftime(date_format)
    return timestr

def handle_vvv_video_tags(infile, outfile):
    with open(infile) as f:
        data = f.read()
    # make video links based on "vvv:" tag
    regex = r"^\s*[-\*]*\s*vvv:(.*\.[mM][Pp]4)"
    subst = "[video](\\1)"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    with open(outfile, 'w') as f:
        f.write(data)

def handle_separated_image_link(infile, outfile):
    with open(infile) as f:
        data = f.read()
    regex = r"[-\*]\s\n!\["
    subst = "- !["
    data = re.sub(regex, subst, data, 0)
    with open(outfile, 'w') as f:
        f.write(data)

def handle_blank_title(infile, outfile):
    # blank title created by mindnode or mistakenly by hand
    with open(infile) as f:
        data = f.read()
    regex = r"^#+ *$"
    subst = ""
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    with open(outfile, 'w') as f:
        f.write(data)

def handle_blank_lines_between_list_items(infile, outfile):
    with open(infile) as f:
        data = f.read()
    # remove blank lines after list item
    regex = r"^$\n(^\s*[-\*])"
    subst = "\\1"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    with open(outfile, 'w') as f:
        f.write(data)

def main(argv):
    num_vars = len(argv)
    working_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = working_dir + "/temp"
    outfile = output_dir + "/temp.md"
    local_repo_path = output_dir + "/repo"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if num_vars == 1:
        print "Please input the original markdown filename!"
    elif num_vars == 3:
        outfile = os.path.expanduser(argv[2])
    else:
        infile = os.path.expanduser(argv[1])
        # try to handle textbundle
        if infile.endswith("textbundle"): # it's not a markdown file, but a textbundle folder
            infile = infile + "/text.md" # set infile to the markdown file inside the folder, the rest would be the same
            if not os.path.exists(infile):
                infile = infile.replace(".md", ".markdown")
        link_key_pairs = convert_pic_links_local_repo(infile, outfile, local_repo_path)
        links = link_key_pairs.iterkeys()
        sync_pics_to_local_repo(infile, link_key_pairs, local_repo_path)
        handle_blank_title(outfile, outfile)
        handle_vvv_video_tags(outfile, outfile)
        handle_blank_lines_between_list_items(outfile, outfile)
        handle_separated_image_link(outfile, outfile)

if __name__ == "__main__":
    main(sys.argv)
