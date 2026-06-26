#!/usr/bin/env python3
import sys, zipfile, javadoc_common as c
sys.stdout.reconfigure(encoding="utf-8")
jars = c.find_javadoc_jars()
core = [j for j in jars if "vertigo-core" in j][0]
with zipfile.ZipFile(core) as z:
    h = c.read_jar_string(z, "constant-values.html")
    print(h[:3000])
    print("...")
    print(h[-500:])
