#coding=utf-8
import sys
import re
import os
import shutil
import datetime
from PIL import Image

def prepare_export_dir(revealjs_preview_dir, revealjs_export_dir):
    if not os.path.exists(revealjs_export_dir):
        os.makedirs(revealjs_export_dir)
    export_repo_dir = "{}/repo".format(revealjs_export_dir)
    if os.path.exists(export_repo_dir):
        shutil.rmtree(export_repo_dir)
    os.makedirs(export_repo_dir)
    revealjs_runtime = revealjs_preview_dir + '/reveal.js'
    cmd = '/usr/bin/rsync -av "{}" "{}"'.format(revealjs_runtime, revealjs_export_dir)
    os.system(cmd)

def convert_media_links_export_repo(slide_html_file, export_html_file):

    with open(slide_html_file) as f:
        data = f.read()

    regex = r"img src=\"(.*?)\""
    inline_image_links = re.findall(regex, data)
    regex = r"data-background-image=\"(.*?)\""
    background_image_links = re.findall(regex ,data)
    regex = r"data-background-video=\"(.*?)\""
    background_video_links = re.findall(regex, data)

    links = inline_image_links + background_image_links + background_video_links

    # inline image path convert:
    regex = r"(img src=\")(.*)/(.*?)\""
    subst = "\\1repo/\\3\""
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # background image path convert:
    regex = r"(data-background-image=\")(.*)/(.*?)\""
    subst = "\\1repo/\\3\""
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # background video path convert:
    regex = r"(data-background-video=\")(.*)/(.*?)\""
    subst = "\\1repo/\\3\""
    data = re.sub(regex, subst, data, 0, re.MULTILINE)

    with open(export_html_file, 'w') as f:
        f.write(data)

    return links


def sync_media_to_export_repo_dir(links, revealjs_export_dir):
    export_repo_dir = "{}/repo".format(revealjs_export_dir)

    for link in links:
        cmd = '/usr/bin/rsync -av "{}" "{}"'.format(link, export_repo_dir)
        os.system(cmd)

def check_contain_chinese(check_str):
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def change_md_to_slide_md(infile, slide_md_file):
    with open(infile) as f:
        data = f.read()
    # change title line from h1 to title
    regex = r"^# (.*)"
    title = re.match(regex, data, flags=re.MULTILINE).group(1)

    now = datetime.datetime.now()
    if check_contain_chinese(title): #contains chinese characters in title:
        #author = "王树义"
        author = ""
        date = "{}年{}月".format(now.year, now.month)
        end_string = "\n\n## {}\n\n{}".format("放映结束", "谢谢观赏！")

    else: # English title
        #author = "Shuyi Wang"
        author = ""
        date = now.strftime("%b %Y")
        end_string = "\n\n## {}\n\n{}".format("The End", "Thanks for your time!")
    subst = "% \\1\\n% {}\\n% {}".format(author, date)
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # change h2 title to h1 title
    regex = r"^## (.*)"
    subst = "# \\1"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # change h3 title to h2 title
    regex = r"^### (.*)"
    subst = "## \\1"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # change separated inline image to one line
    regex = r"^\s*[-\*]\s+\n+!\["
    subst = "* !["
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # make background images to separate slide
    regex = r"^ *!\[.*\]\((.*)\)"
    subst = "\n\n##  {data-background-image=\"\\1\" data-background-size=\"contain\"}"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # make video links to separate video slide
    regex = r"^ *\[video\]\((.*)\)"
    subst = "\n\n##  {data-background-video=\"\\1\"}"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # make video links based on "vvv:" tag
    regex = r"^\s*[-\*]*\s*vvv:(.*\.[mM][Pp]4)"
    subst = "\n\n##  {data-background-video=\"\\1\"}"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # change inline images to html link
    regex = r"^ *([-\*])\s+!\[(.*)\]\((.*)\)"
    subst = "\\1 <img src=\"\\3\" style=\"border-style: none\" alt=\"\\2\">"
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    # resize inline images
    regex = r"^[\*-] +<img src=\"(.*?)\".*"
    links = re.findall(regex, data, re.MULTILINE)
    for link in links:
        with Image.open(link) as im:
            width, height = im.size
        if height>width and height>400:
            regex = r"^(.*" + link + r".*?alt=\".*?\").*?>"
            subst = "\\1 height=\"400\">"
            data = re.sub(regex, subst, data, 0, re.MULTILINE)
    with open(slide_md_file, 'w') as f:
        f.write(data)
        f.write(end_string)

def pandoc_slide_md_to_revealjs(slide_md_file, slide_html_file):
    cmd = """
    /usr/local/bin/pandoc -t revealjs \
    --standalone --mathjax -i\
  --variable theme="sky" \
  --variable transition="convex" \
  {} \
 -o {}
    """.format(slide_md_file, slide_html_file)
    os.system(cmd)

def preview_revealjs(slide_html_file):
    cmd = "open {}".format(slide_html_file)
    os.system(cmd)

def make_pointer_works(slide_html_file):
    with open(slide_html_file) as f:
        data = f.read()
    keyboard_string = """
            keyboard: {
            39: 'next',
            37: 'prev'
        },
    """
    regex = r"(Reveal\.initialize\({)"
    subst = "\\1" + keyboard_string
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    with open(slide_html_file, 'w') as f:
        f.write(data)

def make_mathjax_compact_work(slide_html_file):
    with open(slide_html_file) as f:
        data = f.read()
    mathjax_compact_string = """
    	math: {
		mathjax: 'mathjax-compact/MathJax.js',
		config: 'TeX-AMS_HTML-full'  // See http://docs.mathjax.org/en/latest/config-files.html
	},
    """
    regex = r"(Reveal\.initialize\({)"
    subst = "\\1" + mathjax_compact_string
    data = re.sub(regex, subst, data, 0, re.MULTILINE)
    regex = r"(dependencies: \[)"
    subst = "\\1\\n{ src: 'reveal.js/plugin/math/math.js', async: true }"
    data = re.sub(regex, subst, data, 0)
    with open(slide_html_file, 'w') as f:
        f.write(data)

def main(argv):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = working_dir + "/temp"
    temp_md_file = output_dir + "/temp.md"
    local_repo_path = output_dir + "/repo"

    infile = temp_md_file

    revealjs_preview_dir = working_dir + "/slide_temp"
    revealjs_export_dir = working_dir + "/export"
    # 1st step: convert the markdown file to a pandoc revealjs ready markdown file
    # put the file in the directory revealjs_preview_dir
    slide_md_file = revealjs_preview_dir + '/slide.md'
    change_md_to_slide_md(infile, slide_md_file)
    # 2nd step: use pandoc to convert to revealjs
    slide_html_file = revealjs_preview_dir + '/slide.html'
    pandoc_slide_md_to_revealjs(slide_md_file, slide_html_file)
    # 3rd step: make pointer works
    make_pointer_works(slide_html_file)
    # 4th step: make mathjax compact works
    # make_mathjax_compact_work(slide_html_file)
    # 5th step: open the revealjs file in browser
    if len(argv) > 1 and argv[1] == 'preview':
        preview_revealjs(slide_html_file)
    else: # by default, export
        print ('exporting ...')
        prepare_export_dir(revealjs_preview_dir, revealjs_export_dir)
        export_html_file = revealjs_export_dir + '/slide.html'
        links = convert_media_links_export_repo(slide_html_file, export_html_file)
        sync_media_to_export_repo_dir(links, revealjs_export_dir)
        preview_revealjs(export_html_file)

if __name__ == "__main__":
    main(sys.argv)
