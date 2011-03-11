import tempfile
import subprocess
import django.http
import django.template.loader
import os.path
import shutil

def render_to_response(template, dct, context_instance):
    if 'request' in context_instance and context_instance['request'].GET.get('format', '') == 'tex':
        return django.http.HttpResponse(django.template.loader.render_to_string(template, dct, context_instance).encode('utf-8'), mimetype="text/plain")

    workdir = tempfile.mkdtemp()
    try:
        texfile = os.path.join(workdir, 'print.tex')
        pdffile = os.path.join(workdir, 'print.pdf')
        logfile = os.path.join(workdir, 'out.log')

        with open(texfile, 'w') as f:
            f.write(django.template.loader.render_to_string(template, dct, context_instance).encode('utf-8'))

        with open(logfile, 'w') as f:
            status = subprocess.call(["pdflatex", "-interaction=batchmode", texfile], cwd=workdir, stdout=f, stderr=subprocess.STDOUT)

        if os.path.exists(pdffile):
            with open(pdffile) as f:
                pdf = f.read()
        else:
            with open(logfile) as f:
                log = f.read()
            raise Exception("Unable to render document (status=%s): %s" % (status, log))

        return django.http.HttpResponse(pdf, mimetype="application/pdf")
    finally:
        shutil.rmtree(workdir)
