class JavaFileHelper:

    def __init__(self, file_path):
        self.file_path = file_path

    def change_field(self, replace_dict: dict, output_file: str):
        new_lines = []
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            line = f.readline()
            max_space_line = 10
            space_line_count = 0 if line else 1

            while line or space_line_count < max_space_line:
                if not line:
                    space_line_count = space_line_count + 1
                else:
                    space_line_count = 0

                strip_line = line.strip()

                end_idx = 0
                if ";" in strip_line:
                    end_idx = strip_line.index(";")
                if strip_line.startswith("public") \
                        and end_idx:

                    idx = 0
                    if "//" in strip_line:
                        idx = strip_line.index("//")

                    if "/*" in strip_line:
                        tmp = strip_line.index("/*")
                        idx = tmp if tmp < idx else idx

                    if 0 < idx < end_idx:
                        new_lines.append(line)
                        line = f.readline()
                        continue

                    strip_line_items = strip_line.split("=")
                    # print("field decoration: %s" % line)
                    if len(strip_line_items) == 2:
                        field = strip_line_items[0].strip().split(" ")[-1]
                        # print("field name: %s " % field)
                        fields = replace_dict.keys()
                        if field in fields:
                            tmp = replace_dict[field]
                            value = tmp
                            if callable(value):
                                value = value(strip_line_items[1])

                            line = strip_line_items[0] + " = \"" + value + "\";\n"
                            # print("set_field_value: new line = " + line)

                new_lines.append(line)

                line = f.readline()

        with open(output_file, mode="w", encoding="utf-8") as f:
            f.writelines(new_lines)
