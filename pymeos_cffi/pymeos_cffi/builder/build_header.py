import os.path
import platform
import re
import subprocess
import sys
from typing import Set, Tuple


def get_defined_functions(library_path):
    result = subprocess.check_output(["nm", "-g", library_path])
    output = result.decode("utf-8")
    lines = output.splitlines()
    defined = {line.split(" ")[-1] for line in lines if " T " in line}
    return defined


def remove_undefined_functions(content, so_path):
    defined = get_defined_functions(so_path)
    undefined_types = ["json_object"]

    def remove_if_not_defined(m):
        function = m.group(0).split("(")[0].strip().split(" ")[-1].strip("*")
        if function in defined or (
            sys.platform == "darwin" and ("_" + function) in defined
        ):
            for t in undefined_types:
                if t in m.group(0):
                    print(f"Removing function due to undefined type {t}: {function}")
                    return f"/* {m.group(0)}  (undefined type {t}) */"
            return m.group(0)
        else:
            print(f"Removing undefined function: {function}")
            return f"/* {m.group(0)}  (undefined) */"

    content = re.sub(
        r"^extern .*?;", remove_if_not_defined, content, flags=re.RegexFlag.MULTILINE
    )
    return content


def remove_repeated_functions(
    content: str, seen_functions: set
) -> Tuple[str, Set[str]]:
    def remove_if_repeated(m):
        function = m.group(0).replace("\n", "").strip()
        if function in seen_functions:
            print(f"Removing repeated function: {function}")
            return f"/* {m.group(0)}  (repeated) */"
        else:
            seen_functions.add(function)
            return m.group(0)

    content = re.sub(
        r"^extern .*?;", remove_if_repeated, content, flags=re.RegexFlag.MULTILINE
    )
    return content, seen_functions


def main(include_dir, so_path=None, destination_path="pymeos_cffi/builder/meos.h"):
    files = ["meos.h", "meos_catalog.h", "meos_internal.h"]
    global_content = ""
    functions = set()
    for file_name in files:
        file_path = os.path.join(include_dir, file_name)
        with open(file_path, "r") as f:
            content = f.read()
            # Remove comments
            content = re.sub(r"//.*", "", content)
            content = re.sub(r"/\*.*?\*/", "", content, flags=re.RegexFlag.DOTALL)

            # Remove macros that are not number constants
            content = content.replace("#", "//#")
            content = re.sub(
                r"^//(#define +\w+ +\d+)\s*$",
                r"\g<1>",
                content,
                flags=re.RegexFlag.MULTILINE,
            )
            content = re.sub(
                r"//#ifdef.*?//#endif", "", content, flags=re.RegexFlag.DOTALL
            )
            content = content.replace("//#endif", "")
            content = re.sub(r"//# *\w+ +([\w,()]+) *((?:\\\n|.)*?)\n", "", content)

            content = re.sub(r"\n\n\n+", "\n\n", content)

            # Remove functions that are not actually defined in the library
            if so_path:
                content = remove_undefined_functions(content, so_path)

            content, functions = remove_repeated_functions(content, functions)

        global_content += f"//-------------------- {file_name} --------------------\n"
        global_content += content

    # Add error handler
    global_content += '\n\nextern "Python" void py_error_handler(int, int, char*);'

    with open(destination_path, "w") as f:
        f.write(global_content)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(*sys.argv[1:])
    else:
        if sys.platform == "linux":
            main("/usr/local/include", "/usr/local/lib/libmeos.so")
        elif sys.platform == "darwin":
            if platform.processor() == "arm":
                main("/opt/homebrew/include", "/opt/homebrew/lib/libmeos.dylib")
            else:
                main("/usr/local/include", "/usr/local/lib/libmeos.dylib")
