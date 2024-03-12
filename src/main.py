import os
import shutil

from markdown import markdown_to_html_node


def copy_to_dir(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)

    if os.path.isfile(src):
        shutil.copy(src, dest)
        return

    for path in os.listdir(src):
        src_path = os.path.join(src, path)
        print(f"Copying '{src_path}' to '{dest}'")
        if os.path.isfile(src_path):
            shutil.copy(src_path, dest)
        else:
            copy_to_dir(src_path, os.path.join(dest, path))


def read_file(path):
    with open(path, "r") as file:
        return file.read()


def write_file(text, path):
    with open(path, "w") as file:
        file.write(text)


def extract_title(html):
    try:
        _, title = html.split("<h1>", maxsplit=1)
    except:
        raise Exception("Missing title header in md file.")

    title, _ = title.split("</h1>", maxsplit=1)
    return title


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page '{from_path}' to '{dest_path}' using '{template_path}'")
    markdown = read_file(from_path)
    template = read_file(template_path)
    html = markdown_to_html_node(markdown)
    html = html.to_html()
    title = extract_title(html)

    html = template.replace("{{ Content }}", html)
    html = html.replace("{{ Title }}", title)
    write_file(html, dest_path)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    if not os.path.exists(dest_dir_path):
        os.mkdir(dest_dir_path)

    for dir in os.listdir(dir_path_content):
        path = os.path.join(dir_path_content, dir)
        if os.path.isfile(path):
            name, ext = os.path.splitext(dir)
            if ext == ".md":
                dest = os.path.join(dest_dir_path, f"{name}.html")
                generate_page(path, template_path, dest)
        else:
            dest = os.path.join(dest_dir_path, dir)
            generate_pages_recursive(path, template_path, dest)


def main():
    copy_to_dir("static", "public")
    generate_pages_recursive("content", "template.html", "public")


if __name__ == "__main__":
    main()
