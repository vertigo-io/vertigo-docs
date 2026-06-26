import os
files = [
    "deprecated-list.html", "constant-values.html", "overview-summary.html", "overview-tree.html",
    "serialized-form.html"
]
for f in files:
    p = os.path.join("apidocs", f)
    with open(p, encoding="utf-8") as fh:
        html = fh.read()
    vc = "vertigo-core" in html
    status = "WARN" if vc else "OK"
    print(f"{status} {f} vertigo-core ref: {vc}")
