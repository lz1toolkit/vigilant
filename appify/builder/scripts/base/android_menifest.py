import os
from collections import Iterable
import xml.etree.ElementTree as ET


def activity_exported(paths):
    if not paths or not isinstance(paths, Iterable):
        return

    for p in paths:
        android_manifest_path = os.path.join(p, 'AndroidManifest.xml')

        if not os.path.exists(android_manifest_path):
            continue

        ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
        tree = ET.parse(android_manifest_path)
        root = tree.getroot()

        for child in root:
            if child.tag == 'application':
                for elem in child:
                    if elem.tag == 'activity':
                        elem.set('{http://schemas.android.com/apk/res/android}exported', 'true')

        tree.write(android_manifest_path + '', xml_declaration=True, encoding='utf-8')